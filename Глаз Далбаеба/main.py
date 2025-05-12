# -*- coding: utf8 -*-
import telebot
from telebot import types
import config
import keyboard
import time
import random
import re
import requests
import json
import os

bot = telebot.TeleBot(config.token, parse_mode=None)

# Глобальная переменная для хранения базы данных
database = {}


# Функция для загрузки базы данных из файла
def load_database(file_path):
    """Загружает базу данных из файла JSON"""
    global database
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                database = json.load(file)
            print(f"База данных успешно загружена из {file_path}")
            print(f"Количество записей: {len(database)}")
            return True
        else:
            print(f"Файл базы данных не найден: {file_path}")
            return False
    except Exception as e:
        print(f"Ошибка при загрузке базы данных: {str(e)}")
        return False


# Функция для поиска в базе данных
def search_database(query, search_type=None):
    """
  Выполняет поиск в базе данных

  :param query: Поисковый запрос
  :param search_type: Тип поиска (phone, name, car, email, etc.)
  :return: Результаты поиска
  """
    results = []
    query = query.lower()

    try:
        if search_type == "phone":
            # Поиск по номеру телефона
            for item in database:
                if "phone" in item and query in str(item["phone"]).lower():
                    results.append(item)

        elif search_type == "name":
            # Поиск по имени
            for item in database:
                if "name" in item and query in item["name"].lower():
                    results.append(item)

        elif search_type == "car":
            # Поиск по автомобилю
            for item in database:
                if "car" in item and query in item["car"].lower():
                    results.append(item)

        elif search_type == "email":
            # Поиск по email
            for item in database:
                if "email" in item and query in item["email"].lower():
                    results.append(item)

        else:
            # Общий поиск по всем полям
            for item in database:
                for key, value in item.items():
                    if isinstance(value, str) and query in value.lower():
                        results.append(item)
                        break

        return results
    except Exception as e:
        print(f"Ошибка при поиске в базе данных: {str(e)}")
        return []


# Функция для форматирования результатов поиска
def format_search_results(results, query):
    """Форматирует результаты поиска для отображения пользователю"""
    if not results:
        return f"🔍 По запросу *{query}* ничего не найдено."

    formatted_text = f"🔍 Результаты поиска по запросу *{query}*:\n\n"

    for i, item in enumerate(results[:10], 1):  # Ограничиваем до 10 результатов
        formatted_text += f"*Результат #{i}*\n"

        for key, value in item.items():
            if key == "name":
                formatted_text += f"👤 ФИО: *{value}*\n"
            elif key == "phone":
                formatted_text += f"📱 Телефон: *{value}*\n"
            elif key == "email":
                formatted_text += f"📧 Email: *{value}*\n"
            elif key == "address":
                formatted_text += f"🏠 Адрес: *{value}*\n"
            elif key == "car":
                formatted_text += f"🚗 Автомобиль: *{value}*\n"
            elif key == "passport":
                formatted_text += f"🛂 Паспорт: *{value}*\n"
            else:
                formatted_text += f"{key}: *{value}*\n"

        formatted_text += "\n"

    if len(results) > 10:
        formatted_text += f"...и еще {len(results) - 10} результатов."

    return formatted_text


# Функция для проверки, является ли пользователь администратором
def is_admin(user_id):
    return int(user_id) == int(config.admin_id)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     '🆘 Вы можете прислать боту запросы в следующем формате\n\n👤 Поиск по имени\n├  `Блогер`\n├  `Проскура Валерий`\n├  `Проскура Валерий Николаевич`\n└  `Устимова Ольга Сергеевна 29.03.1983`\n\n🚗 Поиск по авто\n├  `М999ММ99` - поиск авто по РФ\n├  `ВО4561АХ` - поиск авто по УК\n└  `ХТА21150053965897` - поиск по VIN\n\n👨 Социальные сети\n├  `https://vk.com/id1` - Вконтакте\n├  `https://www.facebook.com/profile.php?id=1` - Facebook\n└  `https://ok.ru/profile/464476975745` - Однокласссники\n\n📱 `79998887777` - для поиска по номеру телефона\n📨 `name@mail.ru` - для поиска по Email\n📧 @anton или перешлите сообщение - поиск по Telegram аккаунту \n\n🔐 `/pas churchill7` - поиск почты, логина и телефона по паролю \n🏚 `/adr Москва, Тверская, д 1, кв 1` - информация по адресу (РФ) \n\n🏛 `/company Сбербанк` - поиск по юр лицам \n📑 `/inn 784806113663` - поиск по ИНН \n\n🌐 `8.8.8.8` или `https://google.com` - информация об IP или домене \n💰 `1AmajNxtJyU7JjAuyiFFkqDaaxuYqkNSkF` - информация о Bitcoin адресе \n\n📸 Отправьте *фото человека*, что бы найти его или двойника в сети Вконтакте. \n🚙 Отправьте *фото номера автомобиля*, что бы получить о нем информацию. \n🌎 Отправьте *точку на карте*, чтобы найти людей которые сейчас там. \n🗣 С помощью *голосовых команд* также можно выполнять *поисковые запросы*.\n',
                     parse_mode='Markdown', reply_markup=keyboard.button_1)


@bot.message_handler(commands=['loaddb'])
def load_db_command(message):
    if is_admin(message.chat.id):
        bot.send_message(message.chat.id, "Отправьте файл базы данных в формате JSON")
        bot.register_next_step_handler(message, process_db_file)
    else:
        bot.send_message(message.chat.id, "Эта команда доступна только администратору")


def process_db_file(message):
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open('database.json', 'wb') as new_file:
                new_file.write(downloaded_file)

            # Загружаем базу данных
            if load_database('database.json'):
                bot.send_message(message.chat.id,
                                 f"✅ База данных успешно загружена!\nКоличество записей: {len(database)}")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка при загрузке базы данных")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка при обработке файла: {str(e)}")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте файл базы данных")


@bot.message_handler(commands=['dbstats'])
def db_stats(message):
    if is_admin(message.chat.id):
        if not database:
            bot.send_message(message.chat.id, "База данных не загружена или пуста")
            return

        stats = {
            "total": len(database),
            "with_phone": sum(1 for item in database if "phone" in item),
            "with_email": sum(1 for item in database if "email" in item),
            "with_name": sum(1 for item in database if "name" in item),
            "with_car": sum(1 for item in database if "car" in item),
        }

        stats_text = f"📊 Статистика базы данных:\n\n"
        stats_text += f"📝 Всего записей: {stats['total']}\n"
        stats_text += f"📱 Записей с телефонами: {stats['with_phone']}\n"
        stats_text += f"📧 Записей с email: {stats['with_email']}\n"
        stats_text += f"👤 Записей с именами: {stats['with_name']}\n"
        stats_text += f"🚗 Записей с автомобилями: {stats['with_car']}\n"

        bot.send_message(message.chat.id, stats_text)
    else:
        bot.send_message(message.chat.id, "Эта команда доступна только администратору")


@bot.message_handler(content_types=['text'])
def message(message):
    # Проверяем, является ли пользователь администратором
    if message.text == '🆘 Команды':
        bot.send_message(message.chat.id,
                         '🆘 Вы можете прислать боту запросы в следующем формате\n\n👤 Поиск по имени\n├  `Блогер`\n├  `Проскура Валерий`\n├  `Проскура Валерий Николаевич`\n└  `Устимова Ольга Сергеевна 29.03.1983`\n\n🚗 Поиск по авто\n├  `М999ММ99` - поиск авто по РФ\n├  `ВО4561АХ` - поиск авто по УК\n└  `ХТА21150053965897` - поиск по VIN\n\n👨 Социальные сети\n├  `https://vk.com/id1` - Вконтакте\n├  `https://www.facebook.com/profile.php?id=1` - Facebook\n└  `https://ok.ru/profile/464476975745` - Однокласссники\n\n📱 `79998887777` - для поиска по номеру телефона\n📨 `name@mail.ru` - для поиска по Email\n📧 @slivmenss или перешлите сообщение - поиск по Telegram аккаунту \n\n🔐 `/pas churchill7` - поиск почты, логина и телефона по паролю \n🏚 `/adr Москва, Тверская, д 1, кв 1` - информация по адресу (РФ) \n\n🏛 `/company Сбербанк` - поиск по юр лицам \n📑 `/inn 784806113663` - поиск по ИНН \n\n🌐 `8.8.8.8` или `https://google.com` - информация об IP или домене \n💰 `1AmajNxtJyU7JjAuyiFFkqDaaxuYqkNSkF` - информация о Bitcoin адресе \n\n📸 Отправьте *фото человека*, что бы найти его или двойника в сети Вконтакте. \n🚙 Отправьте *фото номера автомобиля*, что бы получить о нем информацию. \n🌎 Отправьте *точку на карте*, чтобы найти людей которые сейчас там. \n🗣 С помощью *голосовых команд* также можно выполнять *поисковые запросы*.',
                         parse_mode='Markdown')
    elif message.text == '📓 Руководство':
        bot.send_message(message.chat.id,
                         '*👁 Руководство по работе с платформой Глаз Далбаеба.*\n└ Данное руководство описывает популярные функции поиска и работу с ними.',
                         reply_markup=keyboard.inline_manual, parse_mode='Markdown')
    elif message.text == '👤 Мой аккаунт':
        bot.send_message(message.chat.id,
                         'Подпишись на наш telegram канал\nhttps://t.me/FindpeopleG\n\nВаш ID: `' + str(
                             message.chat.id) + '`\nЮзернейм: `@' + str(
                             message.chat.username) + '`\n\n📅 Подписка:  `активна`\n💵 Внутренний баланс: `59₽`\n\n🔎 Статистика поисков\n├ Фотографий: `0`\n├ Автомобилей: `0`\n├ Электронных почт: `0`\n└ Номеров телефонов: `0`',
                         parse_mode='Markdown')
    elif message.text == '👁 О сервисе':
        bot.send_message(message.chat.id,
                         '👁 Глаз Далбаеба- система по поиску информации с огромным количеством возможностей.\n\nСервис позволяет получать информацию о физических лицах в режиме реального времени. *Работа ведётся в рамках Федерального закона от 27 июля 2006 г. № 152-ФЗ «О персональных данных»*, в соответствии с которым обработка персональных данных осуществляется *только с согласия субъекта* персональных данных.\n\n📩 Сотрудничество: ПошелНахуй.рф\n🛡 Юридический отдел: хертебе\n⚙️ Служба поддержки: Думай Сам\n📰 Пресс-центр:А еще че?\n👮‍♂️ Гос. и правоохранительным органам:Пошли нахуй мы вас не звали !',
                         reply_markup=keyboard.inline_about, parse_mode='Markdown')
    else:
        # Обрабатываем поисковый запрос
        bot.send_message(message.chat.id, '⏳ Обрабатываю запрос..')

        # Определяем тип запроса
        search_type = None
        query = message.text

        # Проверяем, является ли запрос номером телефона
        if re.match(r'^\+?\d{10,15}$', query.replace(' ', '')):
            search_type = "phone"
            query = query.replace(' ', '').replace('+', '')

        # Проверяем, является ли запрос email
        elif re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', query):
            search_type = "email"

        # Проверяем, является ли запрос автомобильным номером
        elif re.match(r'^[А-Я]\d{3}[А-Я]{2}\d{2,3}$', query) or re.match(r'^[A-Z]\d{3}[A-Z]{2}\d{2,3}$', query):
            search_type = "car"

        # В остальных случаях считаем, что это поиск по имени
        else:
            search_type = "name"

        # Выполняем поиск
        time.sleep(random.randint(1, 3))  # Имитация задержки поиска

        if not database:
            bot.send_message(message.chat.id, "❌ База данных не загружена. Пожалуйста, обратитесь к администратору.")
            return

        results = search_database(query, search_type)

        # Форматируем и отправляем результаты
        formatted_results = format_search_results(results, query)
        bot.send_message(message.chat.id, formatted_results, parse_mode='Markdown')


@bot.message_handler(content_types=['document'])
def document_react(message):
    # Если пользователь отправил документ, проверяем, не является ли это базой данных
    if is_admin(message.chat.id) and message.document.file_name.endswith('.json'):
        bot.send_message(message.chat.id,
                         "Это похоже на файл базы данных. Хотите загрузить его? Используйте команду /loaddb")
    else:
        bot.send_message(message.chat.id, "Я не могу обработать этот документ. Пожалуйста, отправьте текстовый запрос.")


# Загружаем базу данных при запуске, если файл существует
if os.path.exists('database.json'):
    load_database('database.json')

if __name__ == '__main__':
    bot.polling(none_stop=True)