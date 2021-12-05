from src.exceptions import Exceptions
from src.group import Group
from src.user import User
from typing import List

class Bulletin:
    def __init__(self) -> None:
        self._last_group_id: int = -1
        self._groups: List[Group] = [Group(None)]

    # attempts to retrieve a group using an id
    # raises an exception if it does not exist
    def get_group(self, _id: int = None) -> Group:
        # group id of "None" indicates the default public group
        if _id is None:
            return self._groups[0]

        for group in self._groups:
            if group.get_info()[0] == _id:
                return group

        raise Exceptions.GroupDoesNotExist(f"Could not find requested group with id {_id}: Does not exist.")
        return

    # creates a new group for the bulletin using the requester as the owner
    # returns the group for any desired usage
    def create_group(self, user: User) -> Group:
        self._last_group_id += 1
        group: Group = Group(self._last_group_id, user)

        self._groups.append(group)

        return group

    # deletes an existing group from the bulletin with requested id
    # raises an exception if the requester is not the owner of the group
    # raises an exception if the group does not exist
    # returns the group for any desired usage
    def delete_group(self, id: int, user: User) -> Group:
        group: Group = self.get_group(id)

        if group.get_info()[1] is not user:
            raise Exceptions.UserIsNotOwner(f"Failed to remove requested group with id {id}: User is not the owner.")
        
        if group in self._groups:
            self._groups.remove(group)
        else:
            raise Exceptions.GroupDoesNotExist(f"Failed to remove requested group with id {id}: Group does not exist.")

        return group
