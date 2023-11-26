import asyncio
import datetime
import sqlite3
import openai
from telethon import TelegramClient, errors
from aiogram import Bot, types, Dispatcher, utils
from config import YOUR_API_ID, YOUR_API_HASH, OPENAI_API_KEY, GROUP_LINKS, BOT_TOKEN
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from urllib.parse import quote
import sqlite3

# Настройка OpenAI и Telethon
openai.api_key = OPENAI_API_KEY
client = TelegramClient('anon', YOUR_API_ID, YOUR_API_HASH)

INTERVAL = 5
# Настройка aiogram бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Создание кнопки для клавиатуры пользователя
permanent_markup = ReplyKeyboardMarkup(resize_keyboard=True)
permanent_markup.add(KeyboardButton("Показать все чаты"))
permanent_markup.add(KeyboardButton("Мои подписки"))
permanent_markup.add(KeyboardButton("Отмена подписки"))
permanent_markup.add(KeyboardButton("Перезагрузка бота"))

# Настройка базы данных SQLite


conn = sqlite3.connect('subscriptions.db')
cursor = conn.cursor()

# Добавьте этот блок для создания таблицы 'cached_titles', если ее не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS cached_titles (
    chat_link TEXT PRIMARY KEY,
    title TEXT
)
''')
conn.commit()


# Создаем основные таблицы, если их нет
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_subscriptions (
    user_id INTEGER,
    chat_link TEXT,
    UNIQUE(user_id, chat_link)
)
''')
conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS processed_messages (
    id INTEGER PRIMARY KEY, 
    chat_link TEXT, 
    message_id INTEGER, 
    processed_time TIMESTAMP
)
''')
conn.commit()

cursor.execute('''

CREATE TABLE IF NOT EXISTS last_sent_messages (
    user_id INTEGER PRIMARY KEY,
    last_sent TIMESTAMP
)
''')
conn.commit()

# Проверяем, существует ли колонка last_message_id в таблице user_subscriptions
cursor.execute("PRAGMA table_info(user_subscriptions);")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]
#######################################################################
# Проверяем, существует ли колонка last_message_id в таблице user_subscriptions
cursor.execute("PRAGMA table_info(user_subscriptions);")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

# Если колонки нет - добавляем
if 'last_message_id' not in column_names:
    try:
        cursor.execute('ALTER TABLE user_subscriptions ADD COLUMN last_message_id INTEGER;')
        print("Column last_message_id added successfully to user_subscriptions!")
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Ошибка при добавлении колонки в таблицу user_subscriptions: {e}")

# Проверяем, существует ли колонка group_link в таблице processed_messages
cursor.execute("PRAGMA table_info(processed_messages);")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

# Если колонки нет - добавляем
if 'group_link' not in column_names:
    try:
        cursor.execute('ALTER TABLE processed_messages ADD COLUMN group_link TEXT;')
        print("Column group_link added successfully to processed_messages!")
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Ошибка при добавлении колонки в таблицу processed_messages: {e}")

# Add the following lines to add the "last_message_id" column
if 'last_message_id' not in column_names:
    try:
        cursor.execute('ALTER TABLE processed_messages ADD COLUMN last_message_id INTEGER;')
        print("Column last_message_id added successfully to processed_messages!")
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Ошибка при добавлении колонки в таблицу processed_messages: {e}")

############################################
# Функция для обрезания сообщения до заданного количества слов
def truncate_message_to_words(message, max_words=700):
    #print("truncate_message_to_words")
    words = message.split()
    if len(words) <= max_words:
        return message
    return " ".join(words[:max_words])




# Измененная функция get_group_title для использования кэша
async def get_group_title(link):
<<<<<<< HEAD
    # Попытка получить заголовок из базы данных
    cached_title = cursor.execute("SELECT title FROM cached_titles WHERE chat_link = ?", (link,)).fetchone()

    if cached_title:
        return cached_title[0]
    else:
        retries = 3
        for _ in range(retries):
            try:
                await asyncio.sleep(1)  # Задержка перед каждым запросом
                group_entity = await client.get_entity(link)

                # Сохранение заголовка в базе данных для будущего использования
                cursor.execute("INSERT OR REPLACE INTO cached_titles (chat_link, title) VALUES (?, ?)", (link, group_entity.title))
                conn.commit()

                return group_entity.title

            except errors.InviteHashExpiredError:
                print(f"Ссылка-приглашение для {link} истекла.")
                return None
            except errors.FloodWaitError as e:
                print(f"Необходимо подождать {e.seconds} секунд перед следующим запросом.")
                await asyncio.sleep(e.seconds + 10)  # Задержка при получении FloodWaitError
            except Exception as e:
                print(f"Произошла ошибка при обработке {link}: {e}")
                return None

        print(f"Превышено количество попыток для {link}. Переход к следующему.")
        return None

#######################///////////////////////////////////
import sqlite3
import time
from telethon import errors
=======
  #  print("get_group_title")
    retries = 3
    for _ in range(retries):
        try:
            await asyncio.sleep(1)  # Задержка перед каждым запросом
            group_entity = await client.get_entity(link)
            return group_entity.title
        
        except errors.InviteHashExpiredError:
            print(f"Ссылка-приглашение для {link} истекла.")
            return None
        except errors.FloodWaitError as e:
            print(f"Необходимо подождать {e.seconds} секунд перед следующим запросом.")
            await asyncio.sleep(e.seconds + 10)  # Задержка при получении FloodWaitError
        except Exception as e:
            print(f"Произошла ошибка при обработке {link}: {e}")
            return None
        
    print(f"Превышено количество попыток для {link}. Переход к следующему.")
    return None

>>>>>>> 3979f4ac8b1aeff072a4e05314996cb2103d7fb6

async def process_last_messages(group_link):
    print(f"Начало обработки чата: {group_link}")

    try:
        group_entity = await client.get_entity(group_link)

        # Запрашиваем ID последнего обработанного сообщения из базы данных
        try:
            last_processed_message_id = cursor.execute("SELECT last_message_id FROM user_subscriptions WHERE chat_link = ?", (group_link,)).fetchone()
        except sqlite3.Error as sql_error:
            print(f"Ошибка при выполнении SQL-запроса: {sql_error}")
            return None

        print(f"Last processed message ID before update: {last_processed_message_id}")

        if last_processed_message_id and last_processed_message_id[0]:
            try:
                last_messages = await client.get_messages(group_entity, limit=200, min_id=last_processed_message_id[0])
            except errors.FloodWaitError as e:
                print(f"Получено исключение FloodWaitError: {e}")
                # Добавьте код для обработки ожидания (например, time.sleep(e.seconds) и повторите запрос)
                return None
        else:
            last_messages = await client.get_messages(group_entity, limit=200)

    except errors.ChannelPrivateError:
        return f"Бот не является участником группы {group_link} или группа является закрытой."
    except Exception as e:
        print(f"Произошла ошибка при обработке {group_link}: {e}")
        return None

    # Проверка новых сообщений
    if not last_messages or len(last_messages) == 0:
        return f"В группе {group_entity.title} нет новых сообщений."

    concatenated_messages = "\n".join([msg.text if msg.text else "" for msg in last_messages])
    truncated_messages = truncate_message_to_words(concatenated_messages)

    # Если последние сообщения содержат менее 30 слов, возвращаем уведомление
    if len(truncated_messages.split()) <= 30:
        return f"В группе {group_entity.title} нет новых значимых сообщений."


    #messages = [
    #    {"role": "system", "content": "Извлечь основную мысль и ключевые пункты. Уделить особое внимание выделению главных идей и структурированию ответа."},
     #   {"role": "user", "content": truncated_messages}
    #]
    messages = [
        {"role": "system", "content": "Извлеките основное содержание и выделите ключевые аспекты. Особое внимание уделяйте выявлению главных идей и структурированию ответа."},
        {"role": "user", "content": truncated_messages}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Обновляем или вставляем последний обработанный ID сообщения в базу данных
        cursor.execute("INSERT OR REPLACE INTO processed_messages (group_link, last_message_id) VALUES (?, ?)", (group_link, last_messages[0].id))
        print("Last message ID updated successfully!")

        conn.commit()

        chat_link_with_title = f"[{group_entity.title}]({group_link})"
        processed_content = response['choices'][0]['message']['content']
        message_text = f"**💬От {chat_link_with_title}💬**\n\n💠{processed_content}"
        return message_text

    except Exception as e:
        print(f"Произошла ошибка при обработке сообщений из {group_link}: {e}")
        return None

###############################################################################################
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    print("message_handler commands=start'")    
    
    await message.answer("Нажми на кнопку 'Показать все чаты', чтобы выбрать интересующий чат.", reply_markup=permanent_markup)

@dp.message_handler(lambda message: message.text == "Показать все чаты")
async def show_all_chats(message: types.Message):
    # Удаляем исходное сообщение "Показать все чаты"
    await asyncio.sleep(2)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)  
    #print("show_all_chat")
    markup = InlineKeyboardMarkup()
    for link in GROUP_LINKS:
        group_title = await get_group_title(link)
        if group_title:
            is_subscribed = cursor.execute("SELECT * FROM user_subscriptions WHERE user_id = ? AND chat_link = ?", (message.from_user.id, link)).fetchone()
            if is_subscribed:
                markup.add(InlineKeyboardButton(f"{group_title} [Подписан✅] ", callback_data=f"unsubscribe_{link}"))
            else:
                markup.add(InlineKeyboardButton(group_title, callback_data=f"subscribe_{link}"))                
    sent_message = await bot.send_message(message.chat.id, "Выберите чат для анализа или подписки:", reply_markup=markup)    
    # Задержка в 60 секунд
    await asyncio.sleep(60)
    # Удаление кнопок
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=sent_message.message_id)  
    # Удаляем сообщение "Выберите чат для анализа или подписки:"
    await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)

@dp.message_handler(lambda message: message.text == "Мои подписки")
async def show_subscriptions(message: types.Message):
    # Удаляем сообщение "Мои подписки" отправленное пользователем
    await asyncio.sleep(3)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    subscribed_chats = cursor.execute("SELECT chat_link FROM user_subscriptions WHERE user_id = ?", (message.from_user.id,)).fetchall()
    
    if not subscribed_chats:
        await message.answer("Вы не подписаны на какой-либо чат.")
        return

    markup = InlineKeyboardMarkup()
    for chat in subscribed_chats:
        title = await get_group_title(chat[0])
        if title:
            # Создание кнопки, которая перенаправляет пользователя в чат при нажатии
            markup.add(InlineKeyboardButton(text=title, url=chat[0]))
    
    sent_message = await message.answer(f"Вы подписаны на следующие чаты,\nсообщения приходят каждые {INTERVAL} час(a/ов)...\n", reply_markup=markup)
    # Ждем 60 секунд
    await asyncio.sleep(60)
    # Удаляем сообщение и кнопки
    await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)

# Ваш исходный код "Отмена подписки"
@dp.message_handler(lambda message: message.text == "Отмена подписки")
async def unsubscribe_from_chat(message: types.Message):
    # Удаляем сообщение "Отмена подписки" отправленное пользователем
    await asyncio.sleep(2)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    subscribed_chats = cursor.execute("SELECT chat_link FROM user_subscriptions WHERE user_id = ?", (message.from_user.id,)).fetchall()
    if not subscribed_chats:
        await message.answer("Вы не подписаны на какой-либо чат.")
        return

    markup = InlineKeyboardMarkup()
    for chat in subscribed_chats:
        title = await get_group_title(chat[0])
        if title:
            markup.add(InlineKeyboardButton(title, callback_data=f"unsubscribe_{chat[0]}"))
    sent_message = await message.answer("Выберите чат, чтобы отписаться:", reply_markup=markup)
    # Ждем 60 секунд
    await asyncio.sleep(60)
    # Удаляем сообщение и кнопки
    await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    
@dp.callback_query_handler(lambda c: c.data.startswith('subscribe_') or c.data.startswith('unsubscribe_'))
async def process_subscription(callback_query: types.CallbackQuery):
    print("process_subscription")
    action, link = callback_query.data.split("_", 1)
    if action == "subscribe":
        cursor.execute("INSERT OR IGNORE INTO user_subscriptions (user_id, chat_link) VALUES (?, ?)", (callback_query.from_user.id, link))
        conn.commit()
        await bot.answer_callback_query(callback_query.id, "Вы успешно подписались на чат!")
        #print("Вы успешно подписались на чат")
    elif action == "unsubscribe": 
        cursor.execute("DELETE FROM user_subscriptions WHERE user_id = ? AND chat_link = ?", (callback_query.from_user.id, link))
        conn.commit()
        await bot.answer_callback_query(callback_query.id, "Вы успешно отписались от чата!")
        #print("Вы успешно отписались от чата!")       
    #print("show_all_chats")
async def periodic_task():
    print("Запуск периодической задачи")
    while True:
        subscribers = cursor.execute("SELECT DISTINCT user_id FROM user_subscriptions").fetchall()
        for subscriber in subscribers:
            user_id = subscriber[0]
            user_chats = cursor.execute("SELECT chat_link FROM user_subscriptions WHERE user_id = ?", (user_id,)).fetchall()
            cursor.execute("INSERT OR REPLACE INTO last_sent_messages (user_id, last_sent) VALUES (?, CURRENT_TIMESTAMP)", (user_id,))
            # Обработка сообщений
            for chat in user_chats:
                chat_link = chat[0]
                group_title = await get_group_title(chat_link)  # Получаем название группы
                response_text = await process_last_messages(chat_link)
                if response_text:
                    print("Проверка на None, чтобы избежать отправки пустого сообщения")
                    message_text = f"{response_text}\nJoin the discussion [here]({chat_link})."  # Вставляем ссылку на группу
                    await bot.send_message(user_id, message_text, parse_mode='Markdown')  # Используйте parse_mode='Markdown', чтобы разрешить использование Markdown в тексте сообщения

        # После выполнения всех действий ждем  
        #await asyncio.sleep(60 * 60)  # 1 час в секундах
        print(f"{INTERVAL} Stunde/n warten ")
        await asyncio.sleep(INTERVAL * 60 * 60)  # 4 часа в секундах

if __name__ == '__main__':
    from aiogram import executor

    async def on_startup(dp):
        print("client.start")
        await client.start()
        print("запускаем задачу в фоне")
        asyncio.create_task(periodic_task())  # запускаем задачу в фоне

    async def on_shutdown(dp):
        await client.disconnect()
        print("Закрываем соединение с базой данных")
        conn.close()  # Закрываем соединение с базой данных

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
