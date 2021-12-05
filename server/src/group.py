from src.exceptions import Exceptions
from src.message import Message
from src.user import User
from typing import Dict, List, Tuple

class Group:
    def __init__(self, _id: int, owner: User = None) -> None:
        self._id: int = _id
        self._messages: Dict[str, Message] = {}
        self._last_message_id: int = -1
        self._owner: User = owner

    # accessor for the information of the group in a tuple formatted as such:
    # (groupID, ownerInstance, numMessages)
    def get_info(self) -> Tuple[int, User, int]:
        return (self._id, self._owner, len(self._messages.keys()))

    # adds a message to this group
    # does not allow any two messages to have the same subject line
    # raises an exception when a duplicate subject line is encountered
    def post_message(self, subject: str, content: str, author: User) -> None:
        subjects: str = list(self._messages.keys())
        if subject in subjects:
            raise Exceptions.DuplicateSubjectLine(f"Could not add message to group with id {self._id}: Subject line \"{subject}\" already exists.")

        self._last_message_id += 1
        msg: Message = Message(self._last_message_id, subject, content, author)

        # a new subject is guaranteed, so we *should* be able to
        # safely insert into our dictionary at random
        self._messages[subject] = msg

        return

    # deletes a message from this group
    # raises an exception if the requester is not the author of the message
    # raises an exception if the message does not exist
    def del_message(self, subject: str, requester: User) -> Message:
        for subj in self._messages.keys():
            if subj == subject:
                if self._messages[subj].get_author() is not requester:
                    raise Exceptions.UserIsNotOwner(f"Failed to remove message with subject line \"{subject}\" from group with id {self._id}: Requester is not owner.")
                
                return_me: Message = self._messages[subject]
                del self._messages[subject]

                return return_me
        
        raise Exceptions.MessageDoesNotExist(f"Failed to remove message with subject line \"{subject}\" from group with id {self._id}: Message does not exist.")
        return

    # returns an f-string of all subject lines in this group
    # determines whether or not a user has read this message before;
    # if they have, display **NEW** next to the subject line
    # returns an indication of an empty group if there are no messages
    def get_fmt_subject_lines(self, user: User) -> str:
        ret_me: str = "\n"

        if len(self._messages.keys()) > 0:
            user_seen: List[int] = user.get_seen_messages(self._id)

            # enumeration is handy for giving some organization to the output
            for i, subj in enumerate(self._messages.keys()):
                msg_id: int = self._messages[subj].get_id()

                # choosing not to add this message to the user's seen list here;
                # I feel as though that should only happen when the message is "opened"
                if msg_id not in user_seen:
                    ret_me += "**NEW**: "

                ret_me += f"{i + 1}. {subj}\n"
        else:
            ret_me = "***empty***"

        return ret_me

    # functionally identical to the above function, with some extra fluff
    # returns an f-string of all message subject lines, authors, and contents in this group
    # if a user has not opened this message, it will display **NEW** next to the subject line;
    # it will then subsequently add this message to a user's "seen history", which will not
    # display **NEW** next to it in future readings
    def get_fmt_messages(self, user: User) -> str:
        ret_me: str = "\n"

        if len(self._messages.keys()) > 0:
            user_seen: List[int] = user.get_seen_messages(self._id)

            for subj, msg in self._messages.items():
                msg_id: int = msg.get_id()

                if msg_id not in user_seen:
                    ret_me += "**NEW**: "
                    user.seen_message(self._id, msg_id)

                username: str = msg.get_author().get_info()[1]
                content: str = msg.get_content()

                ret_me += f"{subj}\n    (Posted by: {username})\n    {content}\n"
        else:
            ret_me = "***empty***"

        return ret_me

    # returns and f-string of the requested message with the subject line.
    # raises an exception if it does not exist.
    def get_fmt_message(self, subject: str, user: User) -> str:
        ret_me: str = "\n"

        try:
            msg: Message = self._messages[subject]
            username: str = msg.get_author().get_info()[1]
            content: str = msg.get_content()
        
            ret_me += f"{subject}\n    (Posted by: {username})\n    {content}\n"
            user.seen_message(self._id, msg.get_id())
        except KeyError:
            raise Exceptions.MessageDoesNotExist(f"Failed to retrieve message with subject line \"{subject}\": Message does not exist in this group.")

        return ret_me

    # iterate through all messages in this board
    # if they're new, add to a counter and return as an f-string
    def get_num_new_messages(self, user: User) -> str:
        num_unseen: int = 0

        if len(self._messages.keys()) > 0:
            user_seen: List[int] = user.get_seen_messages(self._id)

            for msg in self._messages.values():
                if msg.get_id() not in user_seen:
                    num_unseen += 1

        return f"{num_unseen} new messages in this group."