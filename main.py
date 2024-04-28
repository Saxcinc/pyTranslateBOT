from add_word import add_words
from table_models.settings import init_db
from bot import bot

if __name__ == '__main__':
    init_db()
    add_words()
    bot.infinity_polling()
