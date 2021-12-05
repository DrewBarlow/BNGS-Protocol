from typing import Dict, List, Tuple

class User:
    def __init__(self, _id: int, name: str) -> None:
        self._id: int = _id
        self._username: str = name
        self._seen_messages: Dict[int, List[int]] = {}
    
    # returns the list of this user's previously seen messages for a group
    def get_seen_messages(self, g_id: int) -> List[int]:
        msgs: List[int] = self._seen_messages.get(g_id)
        return msgs if msgs is not None else []

    # adds a message to a user's history
    def seen_message(self, g_id: int, m_id: int) -> None:
        # if this group has been logged before, simply append the message id
        # if not, create the list then append
        if self._seen_messages.get(g_id):
            self._seen_messages[g_id].append(m_id)
        else:
            self._seen_messages[g_id] = [m_id]

        return

    def get_info(self) -> Tuple[str, int]:
        return (self._id, self._username)
