from src.user import User

class Message:
    def __init__(self, _id: int, subj: str, content: str, author: User) -> None:
        self._id: int = _id
        self._subject: str = subj
        self._content: str = content
        self._author: User = author

    def get_id(self) -> int:
        return self._id

    def get_subject(self) -> str:
        return self._subject

    def get_content(self) -> str:
        return self._content
    
    def get_author(self) -> User:
        return self._author 