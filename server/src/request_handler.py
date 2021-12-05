from socketserver import StreamRequestHandler
from src.bulletin import Bulletin
from src.exceptions import Exceptions
from src.group import Group
from src.lang.parser import query as parse_query
from src.user import User
from typing import List, Tuple

# admittedly, this file is a bit of a mess
# no excuse! 
class Handler(StreamRequestHandler):
    # making use of a static dictionary here to share among all instances of this Handler class
    # this is useful because we want to share the same bulletin, 
    # list of users, and last_user_id amongst all connections
    _data: dict = {
        "bulletin": Bulletin(),
        "users": [],
        "last user id": -1
    }

    def handle(self) -> None:
        print("New connection!")

        user: User = None

        # initialize user information; make use of appropriate error handling for
        # forcibly closed connections
        try:
            self.request.send("Hello, new user. What is your username?".encode())
            self.request.recv(1024)
            
            username: str = self.request.recv(1024).strip().decode()

            # increment previously used user id for new user
            self._data["last user id"] += 1

            user: User = User(self._data["last user id"], username)
            self._data["users"].append(user)

            self.request.send(f"Registered {username}. Welcome to BNGS.".encode())
        except Exception as err:
            print(err)
            return

        try:
            # main connection loop
            # allows for continuous interaction between user and client
            while True:
                # receive the user's query, then parse it for validity
                query: str = self.request.recv(1024).strip().decode()
                parsed_query: Tuple[bool, List[str]] = parse_query(query.split())
    
                # valid queries are forwarded to the determination stage,
                # invalid queries with some recognized tokens are returned with information
                #   in regards to the syntax error
                # invalid queries with no recognized tokens are fed a generic BAD QUERY
                if parsed_query[0] and len(parsed_query[1]) == 0:
                    self._det_query(query, user)
                elif len(parsed_query[1]) > 0:
                    self.request.send(f"BAD QUERY: Failed to recognize {parsed_query[1][0]}.".encode())
                else:
                    self.request.send(f"BAD QUERY".encode())

        except Exception as err:
            # regardless of the exception, we know something went wrong with the connection
            # upon a dropped connection, remove this user from the active list
            print(err)
            if user:
                self._data["users"].remove(user)
                print(f"User \"{user._username}\" disconnected.")
            else:
                print("Unregistered user disconnected.")

        return

    def _parse(self, query: str) -> bool:
        # we only have a legitimately good query if all tokens were eaten
        #   and it has proper syntax
        q: Tuple[bool, List[str]] = parse_query(query.split())
        
        return q[0] and len(q[1]) == 0

    def _det_query(self, query: str, user: User) -> None: 
        query = query.split()

        # feed the valid query to the proper handling function
        if query[0].upper() == "ADD":
            self._query_add(query[1].lower(), user)

        elif query[0].upper() == "REMOVE":
            self._query_remove(query[1].lower(), user)

        elif query[0].upper() == "GET":
            self._query_get(query[1:], user)

        elif query[0].upper() == "HELP":
            self._query_help()
        
        return

    # this help message is pretty gross, so we throw it in its own function
    def _query_help(self) -> None:
        self.request.send("""\"ADD message\": Prompts user for a new message to add to a board.
\"ADD group\": Creates a new group for this user.
\"REMOVE message\": Prompts for the subject line and group of a message to remove.
\"REMOVE group\": Deletes a group.
\"GET message\": Displays a single message from a group.
\"GET messages\": Prints all messages in a group.
\"GET subjects\": Prints all subject lines of messages in a group.
\"GET NUM new\": Displays the number of new messages in a group.
\"GET NUM messages\": Displays the total number of messages in a group.
\"BYE\": Closes the connection.""".encode())

        return

    def _query_add(self, target: str, user: User) -> None:
        if target == "message":
            details: Tuple[str, str, int] = self._new_message_details()

            # attempt to create a new message in the specified group.
            # deal with the exceptions appropriately
            try:
                self._data["bulletin"].get_group(details[2]).post_message(details[0], details[1], user)
                self.request.send("OK".encode())
            except (Exceptions.DuplicateSubjectLine, Exceptions.GroupDoesNotExist) as err:
                self.request.send(str(err).encode())

        elif target == "group":
            # create a new group with this user as the author,
            # then let them know of the group ID
            new_group: Group = self._data["bulletin"].create_group(user)
            g_id: str = f"Created your group with ID {new_group.get_info()[0]}."
            self.request.send(g_id.encode())

        return

    def _query_remove(self, target: str, user: User) -> None:
        if target == "message":
            details: Tuple[str, int] = self._old_message_details()

            # delete a message from a group if we're able, deal with exceptions otherwise
            try:
                self._data["bulletin"].get_group(details[1]).del_message(details[0], user)
                self.request.send("OK".encode())
            except (Exceptions.MessageDoesNotExist, Exceptions.UserIsNotOwner, Exceptions.GroupDoesNotExist) as err:
                self.request.send(str(err).encode()) 
        elif target == "group":
            g_id: int = self._group_details()

            # delete a group if we're able, deal with exceptions otherwise
            try:
                self._data["bulletin"].delete_group(g_id, user)
                self.request.send("OK".encode())
            except (Exceptions.GroupDoesNotExist, Exceptions.UserIsNotOwner) as err:
                self.request.send(str(err).encode())

        return

    def _query_get(self, query: List[str], user: User) -> None:
        # all queries will deal with the group maybe not existing,
        # so it's safe to wrap it in a try/except
        try:
            # retrieve a specific message
            if query[0].lower() == "message":
                details: Tuple[str, int] = self._old_message_details()

                try:
                    self.request.send(self._data["bulletin"].get_group(details[1]).get_fmt_message(details[0], user).encode())
                except Exceptions.MessageDoesNotExist as err:
                    self.request.send(str(err).encode())

            # receive bulk messages or subject lines
            elif query[0].lower() == "messages":
                g_id: int = self._group_details()
                self.request.send(self._data["bulletin"].get_group(g_id).get_fmt_messages(user).encode())

            elif query[0].lower() == "subjects":
                g_id: int = self._group_details()
                self.request.send(self._data["bulletin"].get_group(g_id).get_fmt_subject_lines(user).encode())
            
            # enumerated returns, both total messages and new messages
            elif query[0].upper() == "NUM":
                target: str = query[1].lower()

                if target == "messages":
                    g_id: int = self._group_details()
                    num_msgs: int = self._data["bulletin"].get_group(g_id).get_info()[2]
                    self.request.send(f"{num_msgs} messages in this group.".encode())

                elif target == "new":
                    g_id: int = self._group_details()
                    self.request.send(self._data["bulletin"].get_group(g_id).get_num_new_messages(user).encode())

        except Exceptions.GroupDoesNotExist as err:
            self.request.send(str(err).encode())

        return

    # gather proper input from the user to craft their new message
    def _new_message_details(self) -> Tuple[str, str, int]:
        self.request.send("Subject Line: ".encode())
        subj: str = self.request.recv(1024).strip().decode()
        self.request.send("Content: ".encode())
        content: str = self.request.recv(1024).strip().decode()
        g_id: int = self._group_details()

        return (subj, content, g_id)

    # gather proper input from the user to retrieve an existing message
    def _old_message_details(self) -> Tuple[str, int]:
        self.request.send("Subject Line: ".encode())
        subj: str = self.request.recv(1024).strip().decode()
        g_id: int = self._group_details()

        return (subj, g_id)

    # gather proper input from the user to retrieve a group
    def _group_details(self) -> int:
        self.request.send("Group ID (any string if public): ".encode())
        g_id: str = self.request.recv(1024).strip().decode()
        
        # we're letting any random string be the default for the public group
        # honestly, that's the easiest thing for both me and the user to deal with, I think
        try:
            return int(g_id)
        except:
            return None
