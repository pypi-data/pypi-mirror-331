from __future__ import annotations
import collections
import json
import datetime
import enum
import dataclasses
import logging


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


@dataclasses.dataclass
class Message:
    role: MessageRole
    content: str
    timestamp: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        if not isinstance(self.role, MessageRole):
            try:
                self.role = MessageRole(self.role)
            except ValueError:
                raise ValueError(
                    f"Некорректная роль: {self.role}. "
                    f"Должна быть одна из: {', '.join(r.value for r in MessageRole)}"
                )

        if not self.content or not self.content.strip():
            raise ValueError("Сообщение не может быть пустым")

        self.content = self.content.strip()

    def to_dict(self) -> dict:
        return {
            "role": self.role.value,
            "content": self.content,
        }

    def to_full_dict(self) -> dict:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    def __str__(self) -> str:
        return f"Message(role='{self.role.value}', content='{self.content}')"

    def __repr__(self) -> str:
        return f"Message(role='{self.role.value}', content='{self.content}', timestamp='{self.timestamp}')"

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class MessageHistory:
    messages: list[Message]
    max_messages: int | None
    _iterator_index: int

    def __init__(self, max_messages: int | None = None) -> None:
        self.messages: list[Message] = []
        self.max_messages = max_messages
        self._iterator_index = 0

    def add_message(self, role: str | MessageRole, content: str) -> "MessageHistory":
        message = Message(role=role, content=content)
        self.messages.append(message)
        if self.max_messages and len(self.messages) > self.max_messages:
            logging.warning("История сообщения достигла лимита, часть сообщений удалена")
            self.messages = self.messages[-self.max_messages:]
        return self

    def clear(self) -> None:
        self.messages.clear()
        self._iterator_index = 0

    def pop(self) -> Message | None:
        return self.messages.pop() if self.messages else None

    def get_last_n_messages(self, n: int) -> list[Message]:
        return self.messages[-n:] if n > 0 and self.messages else []

    def to_api_format(self) -> list[dict]:
        return [msg.to_dict() for msg in self.messages]

    def to_json(self) -> str:
        return json.dumps(self.to_api_format(), ensure_ascii=False)

    def from_json(self, json_data: str) -> 'MessageHistory':
        try:
            data = json.loads(json_data)
            self.clear()
            for msg_data in data:
                # Преобразуем timestamp обратно в datetime
                if "timestamp" in msg_data:
                    try:
                        msg_data["timestamp"] = datetime.datetime.fromisoformat(msg_data["timestamp"])
                    except ValueError:
                        msg_data["timestamp"] = datetime.datetime.now()

                message = Message(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    timestamp=msg_data.get("timestamp", datetime.datetime.now()))
                self.messages.append(message)
            return self
        except Exception as e:
            raise ValueError(f"Ошибка при загрузке истории из JSON: {e}")

    def __len__(self) -> int:
        return len(self.messages)

    def __str__(self) -> str:
        return f"MessageHistory(messages={len(self.messages)})"

    def __iter__(self) -> collections.abc.Iterator[Message]:
        self._iterator_index = 0
        return self

    def __next__(self) -> Message:
        if self._iterator_index >= len(self.messages):
            raise StopIteration
        message = self.messages[self._iterator_index]
        self._iterator_index += 1
        return message

    def __getitem__(self, index: int | slice) -> Message | "MessageHistory" | None:
        if isinstance(index, int):
            return self.messages[index]
        elif isinstance(index, slice):
            new_history = MessageHistory(max_messages=self.max_messages)
            new_history.messages = self.messages[index]
            return new_history


class MessageHistoryManager:
    def __init__(self, default_max_messages: int | None = None) -> None:
        self.default_max_messages = default_max_messages
        self._histories: dict[int, MessageHistory] = collections.defaultdict(
            lambda: MessageHistory(max_messages=default_max_messages)
        )

    def __getitem__(self, user_id: int) -> MessageHistory:
        return self._histories[user_id]

    def __iter__(self) -> collections.abc.Iterator[int]:
        return iter(self._histories)

    def __contains__(self, user_id: int) -> bool:
        return user_id in self._histories

    def get_user_ids(self) -> list[int]:
        return list(self._histories.keys())

    def remove_user(self, user_id: int) -> None:
        if user_id in self._histories:
            del self._histories[user_id]

    def clear_all(self) -> None:
        self._histories.clear()

    def to_json(self) -> str:
        histories_as_dict = {
            str(user_id): history.to_api_format() for user_id, history in self._histories.items()
        }
        return json.dumps(histories_as_dict, ensure_ascii=False)

    def from_json(self, json_data: str) -> 'MessageHistoryManager':
        try:
            data = json.loads(json_data)
            self._histories.clear()

            for user_id_str, history_data in data.items():
                try:
                    user_id = int(user_id_str)
                except ValueError:
                    continue

                history = MessageHistory(max_messages=self.default_max_messages)
                history_json = json.dumps(history_data, ensure_ascii=False)
                self._histories[user_id] = history.from_json(history_json)

            return self
        except Exception as e:
            raise ValueError(f"Ошибка при загрузке менеджера историй из JSON: {e}")

    def __len__(self) -> int:
        return len(self._histories)
