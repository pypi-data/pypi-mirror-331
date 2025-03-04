# Statgram

[![PyPI Version](https://img.shields.io/pypi/v/statgram)](https://pypi.org/project/statgram/)
[![License](https://img.shields.io/github/license/generext/statgram)](https://github.com/generext/statgram/blob/main/LICENSE)

**Statgram** — AI-платформа аналитики и управления чат-ботами и мини-приложениями в Telegram.  
Обеспечивает расширенные возможности по мониторингу пользователей, логированию событий и интеграции с базой данных.

📌 **Официальный сайт:** [Statgram.org](https://statgram.org)

---

## 🚀 Возможности

- 📊 **AI-аналитика с LLM** — анализ пользовательских данных и ответ на сложные вопросы.
- 📩 **Рассылки** — система автоматически подбирает аудиторию для целевых рассылок.
- 📈 **Адаптивный Dashboard** — кастомизируемый интерфейс с KPI-метриками.
- 🔐 **Интеграция с базой данных** — Statgram подключается к PostgreSQL для генерации SQL-запросов.
- 📝 **Логирование событий** — автоматический сбор логов для аналитики.

---

## 📚 Установка

Установите библиотеку через PyPI:

```sh
pip install statgram
```

---

## 🛠️ Начало работы

### 1️⃣ **Инициализация бота**
Подключите Statgram к своему Telegram-боту:

```python
from aiogram import Bot
from statgram import Statgram

TOKEN = "ВАШ_ТОКЕН_БОТА"
bot = Bot(token=TOKEN)
statgram = Statgram(token=TOKEN, bot=bot)
```

### 2️⃣ **Подключение к базе данных**
Statgram поддерживает PostgreSQL:

```python
statgram.connect_postgresql(
    host="localhost",
    port=5432,
    user="postgres",
    password="password",
    database="statgram_db"
)
```

### 3️⃣ **Отправка логов**
Логирование событий в Statgram:

```python
from statgram.schemas import MessageSchema

message_data = MessageSchema(data="Новый пользователь зарегистрирован.")
statgram.log(message_data)
```

### 4️⃣ **Запуск периодического анализа сообщений**
Для обработки входящих сообщений настройте обработчик:

```python
import asyncio

asyncio.create_task(statgram.periodic_get())
```

---

## 🛠️ API Методы

| Метод | Описание |
|--------|--------------------------------|
| `get_bot_username()` | Получает username бота |
| `log(message_data)` | Логирует сообщение |
| `send_message(data)` | Отправляет сообщение в Telegram |
| `delete_message(chat_id)` | Удаляет сообщение по chat_id |
| `connect_postgresql(host, port, user, password, database)` | Подключает PostgreSQL |

---

## 📝 Лицензия

Этот проект распространяется под лицензией MIT.

📌 **Официальный сайт:** [Statgram.org](https://statgram.org)  
📌 **PyPI:** [Statgram на PyPI](https://pypi.org/project/statgram/)  
📌 **GitHub:** [Statgram на GitHub](https://github.com/generext/statgram)  

