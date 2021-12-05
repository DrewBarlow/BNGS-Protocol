
class Exceptions:
    class DuplicateSubjectLine(Exception): pass
    class GroupDoesNotExist(Exception): pass
    class MessageDoesNotExist(Exception): pass
    class UserIsNotOwner(Exception): pass