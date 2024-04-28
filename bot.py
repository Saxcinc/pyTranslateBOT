import logging
import os
import random

import telebot
from telebot.handler_backends import StatesGroup, State
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
from sqlalchemy import func

from table_models.settings import session
from table_models.users import Translations, Words, Users, UserWords

logging.basicConfig(level=logging.INFO)

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

correct = []


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


class AddWord(StatesGroup):
    waiting_for_word = State()
    waiting_for_translation = State()


def main_keyboard():
    main_button = ['Следующее слово 🔑️️️️️️', 'Добавить слово ➕', 'Удалить слово 🗑']

    return main_button


@bot.message_handler(commands=['start'])
def hello_message(message):
    username = message.from_user.username

    if not username:
        bot.send_message(message.chat.id, 'Пожалуйста, установите username в настройках Telegram и попробуйте снова:'
                                          '/start')
        return  # Выходим из функции, если у пользователя нет username

    existing_user = session.query(Users).filter_by(username=username).first()
    if existing_user:
        # Пользователь уже существует, просто отправляем приветствие
        bot.send_message(message.chat.id, f'Приветствую 👋 @{username}\n\n'
                                          'Сейчас мы будем практиковаться в изучении Английского языка!\n\n'
                                          'Я буду присылать тебе слова на русском языке, а ты постарайся выбрать'
                                          ' правильный из предложенных ответов!\n\nЕсли ты готов, нажми на: '
                                          '/start_game')
    else:
        # Пользователя нет в базе, создаем нового
        try:
            new_user = Users(username=username)
            session.add(new_user)
            session.commit()
            bot.send_message(message.chat.id, f'Приветствую 👋 @{username}\n\n'
                                              'Сейчас мы будем практиковаться в изучении Английского языка!\n\n'
                                              'Я буду присылать тебе слова на русском языке, а ты постарайся выбрать'
                                              ' правильный из предложенных ответов!\n\nЕсли ты готов, нажми на: '
                                              '/start_game')
        except Exception as e:
            session.rollback()
            bot.send_message(message.chat.id, 'Произошла ошибка при регистрации.\n'
                                              'Пожалуйста, попробуйте еще раз: /start')
            print(f"Ошибка: {e}")


@bot.message_handler(commands=['start_game'])
def main_game(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    target_word = session.query(Words).order_by(func.random()).first()
    russian_word = session.query(Translations.translation).filter(Translations.word_id == target_word.id).first()
    other_random_buttons = session.query(Words).filter(target_word.word != Words.word).order_by(func.random()).limit(
        3).all()
    # main_button = [KeyboardButton(text) for text in main_keyboard()]
    target_word_button = KeyboardButton(f'{target_word.word}')
    incorrect_keyboards_button = [KeyboardButton(word.word) for word in other_random_buttons]
    buttons = [target_word_button] + incorrect_keyboards_button
    random.shuffle(buttons)

    markup.add(*buttons)

    bot.send_message(message.chat.id, f'Какой из нижепредставленных на клавиатуре перевод слова верный?'
                                      f'\n\n{russian_word.translation}', reply_markup=markup)

    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word.word
        data['translate_word'] = russian_word.translation
        data['other_words'] = other_random_buttons
        correct.append(data['target_word'])
        correct.append([word.word for word in other_random_buttons])


@bot.message_handler(func=lambda message: message.text == f'{correct[0]}' or message.text in f'{correct[1][:]}')
def message_reply(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']

    trust_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)

    if message.text == target_word:
        main_button = [KeyboardButton(text) for text in main_keyboard()]
        trust_markup.add(*main_button)
        bot.send_message(message.chat.id, f'Верно 👍️️️️️️\n\n'
                                          f'Нажимай «Следующее слово 🔑️️️»_ - чтобы продолжить.'
                                          f'\n\n«Добавить слово ➕»_ - желаешь добавить в словарь своё слово?🫠'
                                          f'\n\n«Удалить слово 🗑» - желаешь удалить слово из словаря? 🫣',
                         reply_markup=trust_markup)

    else:
        bot.send_message(message.chat.id, f'Это не верный перевод, попробуй еще 🙈')


@bot.message_handler(func=lambda message: message.text == "Следующее слово 🔑️️️️️️")
def db_manipulation(message):
    if message.text == 'Следующее слово 🔑️️️️️️':
        correct.clear()
        main_game(message)


@bot.message_handler(func=lambda message: message.text == "Удалить слово 🗑")
def ask_word_to_delete(message):
    correct.clear()
    bot.send_message(message.chat.id, "Введите слово, которое хотите удалить:")
    bot.register_next_step_handler(message, delete_word)


def delete_word(message):
    user_id = message.from_user.id  # ID пользователя в Telegram
    word_to_delete = message.text.strip().lower()  # Полученное слово для удаления

    # Находим пользователя и слово в базе данных
    user = session.query(Users).filter_by(username=message.from_user.username).first()
    word = session.query(Words).filter_by(word=word_to_delete).first()

    if not user or not word:
        correct.clear()
        bot.send_message(message.chat.id, "Слово не найдено.Продолжим?\n\n"
                                          "/start_game")
        return

    # Находим связь пользователя со словом
    user_word = session.query(UserWords).filter_by(user_id=user.id, word_id=word.id).first()

    if user_word:
        correct.clear()
        session.delete(user_word)  # Удаляем связь пользователя со словом
        session.commit()
        bot.send_message(message.chat.id, "Слово успешно удалено. Продолжим?\n\n"
                                          "/start_game")
    else:
        correct.clear()
        bot.send_message(message.chat.id, "Это слово не было найдено в вашем списке.")


@bot.message_handler(func=lambda message: message.text == "Добавить слово ➕")
def ask_for_word(message):
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Введите слово на 🇬🇧, которое хотите добавить:", reply_markup=markup)
    bot.register_next_step_handler(message, process_word_input)


def process_word_input(message):
    word = message.text.lower()
    logging.info(f"Получено слово: {word}")
    # Сохраняем слово в словаре или через `bot.send_message` передаем дальше
    message_data = {'word': word}
    bot.send_message(message.chat.id, 'Введите перевод слова на 🇷🇺:')
    bot.register_next_step_handler(message, process_translation_input, message_data)


def process_translation_input(message, message_data):
    translation = message.text.lower()
    word = message_data['word']
    user_id = message.from_user.id  # ID пользователя Telegram
    username = message.from_user.username

    logging.info(f"Сохранение слова {word} и перевода {translation}")
    try:
        user = session.query(Users).filter_by(username=username).first()
        if not user:
            user = Users(username=username)
            session.add(user)
            session.commit()

        new_word = session.query(Words).filter_by(word=word).first()
        if not new_word:
            new_word = Words(word=word)
            session.add(new_word)
            session.commit()

        new_translation = Translations(translation=translation, words=new_word)
        session.add(new_translation)
        session.commit()

        # Добавляем связь между словом и пользователем
        new_user_word = UserWords(user_id=user.id, word_id=new_word.id)
        session.add(new_user_word)
        session.commit()

        correct.clear()
        bot.send_message(message.chat.id, "Слово и перевод успешно добавлены!")
        main_game(message)

    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при добавлении слова и перевода.\n\n"
                                          "Давай начнем заного. Нажми на start game 👉: /start_game")
        correct.clear()


@bot.message_handler(content_types=['text'])
def warn(message):
    bot.send_message(message.chat.id, 'Бот не смог обработать Ваш запрос, попробуйте заного, /start')