import unittest
import json
import datetime
import sys
import os

# Добавляем родительскую директорию в sys.path для импорта тестируемого модуля
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simple_chat_structure.chat import Message, MessageRole, MessageHistory, MessageHistoryManager


class TestMessageRole(unittest.TestCase):
    """Тесты для перечисления MessageRole"""

    def test_message_role_values(self):
        """Проверка значений ролей сообщений"""
        self.assertEqual(MessageRole.USER.value, "user")
        self.assertEqual(MessageRole.ASSISTANT.value, "assistant")
        self.assertEqual(MessageRole.SYSTEM.value, "system")
        self.assertEqual(MessageRole.FUNCTION.value, "function")


class TestMessage(unittest.TestCase):
    """Тесты для класса Message"""

    def test_create_message(self):
        """Тест создания сообщения"""
        message = Message(MessageRole.USER, "Привет, мир!")
        self.assertEqual(message.role, MessageRole.USER)
        self.assertEqual(message.content, "Привет, мир!")
        self.assertIsInstance(message.timestamp, datetime.datetime)

    def test_create_message_with_string_role(self):
        """Тест создания сообщения с ролью в виде строки"""
        message = Message("user", "Привет, мир!")
        self.assertEqual(message.role, MessageRole.USER)
        self.assertEqual(message.content, "Привет, мир!")

    def test_create_message_with_invalid_role(self):
        """Тест создания сообщения с недопустимой ролью"""
        with self.assertRaises(ValueError):
            Message("invalid_role", "Привет, мир!")

    def test_create_message_with_empty_content(self):
        """Тест создания сообщения с пустым содержимым"""
        with self.assertRaises(ValueError):
            Message(MessageRole.USER, "")
        with self.assertRaises(ValueError):
            Message(MessageRole.USER, "   ")

    def test_message_content_strip(self):
        """Тест удаления пробелов в содержимом сообщения"""
        message = Message(MessageRole.USER, "  Привет, мир!  ")
        self.assertEqual(message.content, "Привет, мир!")

    def test_to_dict(self):
        """Тест преобразования сообщения в словарь"""
        message = Message(MessageRole.USER, "Привет, мир!")
        expected = {
            "role": "user",
            "content": "Привет, мир!"
        }
        self.assertEqual(message.to_dict(), expected)

    def test_to_full_dict(self):
        """Тест преобразования сообщения в полный словарь"""
        timestamp = datetime.datetime(2023, 1, 1, 12, 0, 0)
        message = Message(MessageRole.USER, "Привет, мир!", timestamp=timestamp)
        expected = {
            "role": "user",
            "content": "Привет, мир!",
            "timestamp": "2023-01-01T12:00:00"
        }
        self.assertEqual(message.to_full_dict(), expected)

    def test_to_json(self):
        """Тест преобразования сообщения в JSON"""
        message = Message(MessageRole.USER, "Привет, мир!")
        expected = json.dumps({"role": "user", "content": "Привет, мир!"}, ensure_ascii=False)
        self.assertEqual(message.to_json(), expected)

    def test_str_representation(self):
        """Тест строкового представления сообщения"""
        message = Message(MessageRole.USER, "Привет, мир!")
        self.assertEqual(str(message), "Message(role='user', content='Привет, мир!')")


class TestMessageHistory(unittest.TestCase):
    """Тесты для класса MessageHistory"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.history = MessageHistory()

    def test_add_message(self):
        """Тест добавления сообщения в историю"""
        self.history.add_message(MessageRole.USER, "Привет")
        self.assertEqual(len(self.history), 1)
        self.assertEqual(self.history[0].role, MessageRole.USER)
        self.assertEqual(self.history[0].content, "Привет")

    def test_max_messages(self):
        """Тест ограничения максимального числа сообщений"""
        history = MessageHistory(max_messages=2)
        history.add_message(MessageRole.USER, "Первое")
        history.add_message(MessageRole.ASSISTANT, "Второе")
        history.add_message(MessageRole.USER, "Третье")

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].content, "Второе")
        self.assertEqual(history[1].content, "Третье")

    def test_clear(self):
        """Тест очистки истории сообщений"""
        self.history.add_message(MessageRole.USER, "Привет")
        self.history.add_message(MessageRole.ASSISTANT, "Привет")
        self.assertEqual(len(self.history), 2)

        self.history.clear()
        self.assertEqual(len(self.history), 0)

    def test_pop(self):
        """Тест удаления последнего сообщения"""
        self.history.add_message(MessageRole.USER, "Первое")
        self.history.add_message(MessageRole.ASSISTANT, "Второе")

        message = self.history.pop()
        self.assertEqual(message.content, "Второе")
        self.assertEqual(len(self.history), 1)

        message = self.history.pop()
        self.assertEqual(message.content, "Первое")
        self.assertEqual(len(self.history), 0)

        message = self.history.pop()
        self.assertIsNone(message)

    def test_get_last_n_messages(self):
        """Тест получения последних N сообщений"""
        self.history.add_message(MessageRole.USER, "1")
        self.history.add_message(MessageRole.ASSISTANT, "2")
        self.history.add_message(MessageRole.USER, "3")

        last_messages = self.history.get_last_n_messages(2)
        self.assertEqual(len(last_messages), 2)
        self.assertEqual(last_messages[0].content, "2")
        self.assertEqual(last_messages[1].content, "3")

        # Проверка с n > количества сообщений
        last_messages = self.history.get_last_n_messages(5)
        self.assertEqual(len(last_messages), 3)

        # Проверка с n <= 0
        last_messages = self.history.get_last_n_messages(0)
        self.assertEqual(len(last_messages), 0)

    def test_to_api_format(self):
        """Тест преобразования истории в формат API"""
        self.history.add_message(MessageRole.USER, "Привет")
        self.history.add_message(MessageRole.ASSISTANT, "Привет, как дела?")

        api_format = self.history.to_api_format()
        expected = [
            {"role": "user", "content": "Привет"},
            {"role": "assistant", "content": "Привет, как дела?"}
        ]
        self.assertEqual(api_format, expected)

    def test_to_json(self):
        """Тест преобразования истории в JSON"""
        self.history.add_message(MessageRole.USER, "Привет")
        self.history.add_message(MessageRole.ASSISTANT, "Привет, как дела?")

        json_data = self.history.to_json()
        expected = json.dumps([
            {"role": "user", "content": "Привет"},
            {"role": "assistant", "content": "Привет, как дела?"}
        ], ensure_ascii=False)
        self.assertEqual(json_data, expected)

    def test_from_json(self):
        """Тест загрузки истории из JSON"""
        json_data = json.dumps([
            {"role": "user", "content": "Привет"},
            {"role": "assistant", "content": "Привет, как дела?"},
            {"role": "user", "content": "Всё хорошо", "timestamp": "2023-01-01T12:00:00"}
        ], ensure_ascii=False)

        self.history.from_json(json_data)
        self.assertEqual(len(self.history), 3)
        self.assertEqual(self.history[0].role, MessageRole.USER)
        self.assertEqual(self.history[0].content, "Привет")
        self.assertEqual(self.history[2].content, "Всё хорошо")
        self.assertEqual(self.history[2].timestamp.isoformat(), "2023-01-01T12:00:00")

    def test_from_json_invalid_data(self):
        """Тест загрузки истории из некорректного JSON"""
        with self.assertRaises(ValueError):
            self.history.from_json("invalid-json")

    def test_iterator(self):
        """Тест итератора истории сообщений"""
        self.history.add_message(MessageRole.USER, "1")
        self.history.add_message(MessageRole.ASSISTANT, "2")

        messages = []
        for message in self.history:
            messages.append(message.content)

        self.assertEqual(messages, ["1", "2"])

        # Проверка повторной итерации
        messages = []
        for message in self.history:
            messages.append(message.content)

        self.assertEqual(messages, ["1", "2"])

    def test_getitem_with_index(self):
        """Тест доступа к сообщениям по индексу"""
        self.history.add_message(MessageRole.USER, "1")
        self.history.add_message(MessageRole.ASSISTANT, "2")

        self.assertEqual(self.history[0].content, "1")
        self.assertEqual(self.history[1].content, "2")

        with self.assertRaises(IndexError):
            _ = self.history[2]

    def test_getitem_with_slice(self):
        """Тест доступа к сообщениям по срезу"""
        self.history.add_message(MessageRole.USER, "1")
        self.history.add_message(MessageRole.ASSISTANT, "2")
        self.history.add_message(MessageRole.USER, "3")

        slice_history = self.history[1:3]
        self.assertIsInstance(slice_history, MessageHistory)
        self.assertEqual(len(slice_history), 2)
        self.assertEqual(slice_history[0].content, "2")
        self.assertEqual(slice_history[1].content, "3")


class TestMessageHistoryManager(unittest.TestCase):
    """Тесты для класса MessageHistoryManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.manager = MessageHistoryManager()

    def test_get_history_for_user(self):
        """Тест получения истории для пользователя"""
        history = self.manager[1]
        self.assertIsInstance(history, MessageHistory)
        self.assertEqual(len(history), 0)

        # Проверка сохранения истории в менеджере
        history.add_message(MessageRole.USER, "Привет")
        self.assertEqual(len(self.manager[1]), 1)

    def test_default_max_messages(self):
        """Тест ограничения максимального числа сообщений по умолчанию"""
        manager = MessageHistoryManager(default_max_messages=2)

        history = manager[1]
        history.add_message(MessageRole.USER, "1")
        history.add_message(MessageRole.ASSISTANT, "2")
        history.add_message(MessageRole.USER, "3")

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].content, "2")
        self.assertEqual(history[1].content, "3")

    def test_contains(self):
        """Тест проверки наличия пользователя в менеджере"""
        self.assertNotIn(1, self.manager)

        _ = self.manager[1]
        self.assertIn(1, self.manager)

    def test_get_user_ids(self):
        """Тест получения списка ID пользователей"""
        _ = self.manager[1]
        _ = self.manager[2]
        _ = self.manager[3]

        user_ids = self.manager.get_user_ids()
        self.assertEqual(set(user_ids), {1, 2, 3})

    def test_remove_user(self):
        """Тест удаления пользователя из менеджера"""
        _ = self.manager[1]
        _ = self.manager[2]

        self.manager.remove_user(1)
        self.assertNotIn(1, self.manager)
        self.assertIn(2, self.manager)

    def test_clear_all(self):
        """Тест очистки всех историй"""
        _ = self.manager[1]
        _ = self.manager[2]

        self.manager.clear_all()
        self.assertNotIn(1, self.manager)
        self.assertNotIn(2, self.manager)
        self.assertEqual(len(self.manager), 0)

    def test_iterator(self):
        """Тест итератора менеджера историй"""
        _ = self.manager[1]
        _ = self.manager[2]

        user_ids = []
        for user_id in self.manager:
            user_ids.append(user_id)

        self.assertEqual(set(user_ids), {1, 2})

    def test_to_json(self):
        """Тест преобразования менеджера историй в JSON"""
        self.manager[1].add_message(MessageRole.USER, "Привет")
        self.manager[2].add_message(MessageRole.ASSISTANT, "Привет, как дела?")

        json_data = self.manager.to_json()
        data = json.loads(json_data)

        self.assertIn("1", data)
        self.assertIn("2", data)
        self.assertEqual(data["1"][0]["content"], "Привет")
        self.assertEqual(data["2"][0]["content"], "Привет, как дела?")

    def test_from_json(self):
        """Тест загрузки менеджера историй из JSON"""
        json_data = json.dumps({
            "1": [{"role": "user", "content": "Привет"}],
            "2": [{"role": "assistant", "content": "Привет, как дела?"}],
            "abc": [{"role": "user", "content": "Некорректный ID"}]  # Должен быть пропущен
        }, ensure_ascii=False)

        self.manager.from_json(json_data)
        self.assertIn(1, self.manager)
        self.assertIn(2, self.manager)
        self.assertEqual(len(self.manager), 2)
        self.assertEqual(self.manager[1][0].content, "Привет")
        self.assertEqual(self.manager[2][0].content, "Привет, как дела?")

    def test_from_json_invalid_data(self):
        """Тест загрузки менеджера историй из некорректного JSON"""
        with self.assertRaises(ValueError):
            self.manager.from_json("invalid-json")


if __name__ == "__main__":
    unittest.main()