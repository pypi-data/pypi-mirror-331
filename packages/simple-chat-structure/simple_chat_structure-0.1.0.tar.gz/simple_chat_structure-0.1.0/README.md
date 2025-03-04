# Simple Chat Structure

Библиотека для управления структурой чатов и сообщений в диалоговых системах. Простой и удобный инструмент для работы с историей сообщений в чатах, ботах и других приложениях с диалоговым интерфейсом.

[![PyPI version](https://badge.fury.io/py/simple_chat_structure.svg)](https://badge.fury.io/py/simple_chat_structure)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Возможности

- 📝 Управление сообщениями с различными ролями (пользователь, ассистент, система, функция)
- 📚 Работа с историей сообщений, ограничение по количеству
- 👥 Менеджер историй для нескольких пользователей
- 💾 Сериализация и десериализация в JSON
- ⏰ Автоматическая отметка времени для каждого сообщения
- ✨ Простой и понятный API

## Установка

```bash
pip install simple_chat_structure
```

## Требования

- Python 3.8 или выше

## Использование

### Основные примеры

#### Создание сообщений

```python
from simple_chat_structure.chat import Message, MessageRole

# Создание сообщения с ролью пользователя
user_message = Message(MessageRole.USER, "Привет, как дела?")

# Создание сообщения с ролью ассистента
assistant_message = Message(MessageRole.ASSISTANT, "Здравствуйте! У меня всё отлично, чем могу помочь?")

# Создание сообщения с ролью системы
system_message = Message(MessageRole.SYSTEM, "Вы общаетесь с AI-ассистентом.")

# Создание сообщения с указанием роли в виде строки
message = Message("user", "Какая сегодня погода?")

# Получение информации о сообщении
print(user_message.role)  # MessageRole.USER
print(user_message.content)  # "Привет, как дела?"
print(user_message.timestamp)  # datetime.datetime объект
```

#### Работа с историей сообщений

```python
from simple_chat_structure.chat import MessageHistory, MessageRole

# Создание истории сообщений
history = MessageHistory()

# Добавление сообщений
history.add_message(MessageRole.USER, "Привет!")
history.add_message(MessageRole.ASSISTANT, "Здравствуйте! Чем могу помочь?")
history.add_message(MessageRole.USER, "Какая сегодня погода?")

# Получение последних сообщений
last_messages = history.get_last_n_messages(2)
for msg in last_messages:
    print(f"{msg.role.value}: {msg.content}")

# Преобразование в формат для API
api_format = history.to_api_format()
print(api_format)
# [{"role": "user", "content": "Привет!"}, 
#  {"role": "assistant", "content": "Здравствуйте! Чем могу помочь?"}, 
#  {"role": "user", "content": "Какая сегодня погода?"}]

# Сохранение и загрузка из JSON
json_data = history.to_json()
new_history = MessageHistory().from_json(json_data)

# Очистка истории
history.clear()

# Создание истории с ограничением количества сообщений
limited_history = MessageHistory(max_messages=10)
```

#### Менеджер историй для нескольких пользователей

```python
from simple_chat_structure.chat import MessageHistoryManager, MessageRole

# Создание менеджера историй
manager = MessageHistoryManager(default_max_messages=50)

# Получение истории для конкретного пользователя
user_id = 123
history = manager[user_id]

# Добавление сообщений пользователю
history.add_message(MessageRole.USER, "Привет!")
history.add_message(MessageRole.ASSISTANT, "Здравствуйте!")

# Проверка наличия пользователя
if user_id in manager:
    print(f"У пользователя {user_id} есть история сообщений")

# Получение списка всех пользователей
users = manager.get_user_ids()
print(users)  # [123]

# Сохранение всех историй в JSON
json_data = manager.to_json()

# Загрузка историй из JSON
new_manager = MessageHistoryManager().from_json(json_data)

# Удаление истории пользователя
manager.remove_user(user_id)

# Очистка всех историй
manager.clear_all()
```

## Документация API

### Message

Класс для представления сообщений в чате.

#### Атрибуты

- `role` - Роль отправителя сообщения (MessageRole)
- `content` - Содержимое сообщения (str)
- `timestamp` - Время создания сообщения (datetime)

#### Методы

- `to_dict()` - Преобразование в словарь для API
- `to_full_dict()` - Преобразование в полный словарь с временем
- `to_json()` - Преобразование в JSON-строку

### MessageRole

Перечисление для обозначения ролей сообщений.

- `USER` - Сообщение пользователя
- `ASSISTANT` - Сообщение ассистента
- `SYSTEM` - Системное сообщение
- `FUNCTION` - Функциональное сообщение

### MessageHistory

Класс для управления историей сообщений.

#### Методы

- `add_message(role, content)` - Добавление сообщения в историю
- `clear()` - Очистка истории
- `pop()` - Удаление и возврат последнего сообщения
- `get_last_n_messages(n)` - Получение последних n сообщений
- `to_api_format()` - Преобразование в формат для API
- `to_json()` - Преобразование в JSON-строку
- `from_json(json_data)` - Загрузка из JSON-строки

### MessageHistoryManager

Класс для управления историями сообщений нескольких пользователей.

#### Методы

- `get_user_ids()` - Получение списка ID пользователей
- `remove_user(user_id)` - Удаление истории пользователя
- `clear_all()` - Очистка всех историй
- `to_json()` - Преобразование в JSON-строку
- `from_json(json_data)` - Загрузка из JSON-строки

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

## Внести вклад

Мы приветствуем вклад в развитие библиотеки! Если вы нашли ошибку или хотите предложить улучшение:

1. Форкните репозиторий
2. Создайте ветку для вашей функции (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add some amazing feature'`)
4. Отправьте изменения в ваш форк (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## Контакты

Страница проекта: [https://github.com/VKolebcev/simple_chat_structure](https://github.com/VKolebcev/simple_chat_structure)