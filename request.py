# import os
# import telebot
import random
import pandas as pd
import os
import telebot
# from dotenv import load_dotenv
#
#
# Dot Env config
# load_dotenv()
#
# TOKEN = '6522058518:AAHYQS2_J0Lz2F_gX_lrd_jt6tjSOxNyN84'
# chat_id = '6275940593'
# CHAT_IDS = set([int(x) for x in chat_id.split(',')])
MEALS_FILENAME = "meals.txt"
# # updater = Updater('API key paste it here, use_context=True)
# # dispatcher = updater.dispatcher
#
# bot = telebot.TeleBot(TOKEN)
#
#
# def verify_chat_id(func):
#     def wrapper(*args):
#         if len(args) > 0:
#             msg = args[0]
#             if msg.chat.id not in CHAT_IDS:
#                 raise PermissionError("Chat id not recognised")
#
#         func(*args)
#     return wrapper



API_TOKEN = '6522058518:AAHYQS2_J0Lz2F_gX_lrd_jt6tjSOxNyN84'

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Hi there, I am your Riverford chatbot. I am here to help you with your mealplan - what can I do for you?")


def load_meals():
    with open(MEALS_FILENAME) as f:
        meals = f.readlines()
    return meals


def save_meal(meal):
    with open(MEALS_FILENAME, 'a') as f:
        f.write(meal + '\n')


@bot.message_handler(commands=['suggest'])
def suggest(msg):
    try:
        meals = load_meals()
        suggestions = random.sample(meals, min(2, len(meals)))
        bot.send_message(msg.chat.id, '\n'.join(suggestions))
    except Exception as e:
        print(e)
        bot.send_message(msg.chat.id, "Failed to suggest meals")
        return


# @bot.message_handler(commands=['add'])
# def add(msg):
#     msg_start = '/add '
#     try:
#         meal = msg.text[len(msg_start):]
#         save_meal(meal)
#         bot.send_message(msg.chat.id, "New meal added")
#     except Exception as e:
#         bot.send_message(msg.chat.id, "Failed to add meal")

@bot.message_handler(commands=['all'])
def all(msg):
    try:
        meals = load_meals()
        bot.send_message(msg.chat.id, '\n'.join(meals))
    except Exception as e:
        return

@bot.message_handler(commands=['recipe'])
def recipe(msg):
    df_rec = pd.read_excel("data/data_w_functions.xlsx", sheet_name="recipes")
    try:
        s = df_rec.at[0, 'Greek Mushroom Ragu & Olive Oil Mash']
        bot.send_message(msg.chat.id, s)
        return
    except Exception as e:
        print(e)
        bot.send_message(msg.chat.id, "Failed to send recipe")
        return

@bot.message_handler(commands=['ingredientsearch'])
def ingredient_search(msg):
    print(msg)
    try:
        bot.send_photo(msg.chat.id,
                       'https://media.riverford.co.uk/images/photo-2600x1040-196a4c7baadddd70ed4e2f8e2a086170.jpg'
                       )
    except Exception as e:
        print(e)
        bot.send_message(msg.chat.id, "Failed to send recipe")
        return

@bot.message_handler(commands=['titlesearch'])
def title_search(msg):
    try:
        bot.send_photo(msg.chat.id,
                       'https://media.riverford.co.uk/images/photo-2600x1040-196a4c7baadddd70ed4e2f8e2a086170.jpg'
                       )
    except Exception as e:
        print(e)
        bot.send_message(msg.chat.id, "Failed to send recipe")
        return


@bot.message_handler(commands=['info'])
def info(msg):
    try:
        bot.send_message(msg.chat.id, "/info - list all bot interactions\n"
                                      # "/add <meal name> - add a new meal\n"
                                      "/all - list all meals\n"
                                      "/suggest - ask for 5 random meal suggestions\n")
    except Exception as e:
        return

import sys
from requests.exceptions import ConnectionError, ReadTimeout

try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
except (ConnectionError, ReadTimeout) as e:
    sys.stdout.flush()
    os.execv(sys.argv[0], sys.argv)
else:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
# bot.polling()