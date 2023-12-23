import os
import telebot
import random
import pandas as pd
from dotenv import load_dotenv
#
#
# # Dot Env config

# load_dotenv()

#
# TOKEN = '6522058518:AAHYQS2_J0Lz2F_gX_lrd_jt6tjSOxNyN84'
# chat_id = '6275940593'
# CHAT_IDS = set([int(x) for x in chat_id.split(',')])
MEALS_FILENAME = "meals.txt"
# updater = Updater('API key paste it here, use_context=True)
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
def dl_data():
    df_rec=pd.read_excel("data/data_w_functions.xlsx",sheet_name="recipes")
    df_quant=pd.read_excel("data/data_w_functions.xlsx",sheet_name="quantity")
    df_meas=pd.read_excel("data/data_w_functions.xlsx",sheet_name="measurement",na_values="")
    df_ingr=pd.read_excel("data/data_w_functions.xlsx",sheet_name="ingredient")

    df_sp_quant=pd.read_excel("data/data_w_functions.xlsx",sheet_name="quantity_sp")
    df_sp_meas=pd.read_excel("data/data_w_functions.xlsx",sheet_name="measurement_sp",na_values="")
    df_sp_ingr=pd.read_excel("data/data_w_functions.xlsx",sheet_name="ingredient_sp")

    df_quant=pd.concat([df_quant,df_sp_quant],axis=1)
    df_meas=pd.concat([df_meas,df_sp_meas],axis=1)
    df_ingr=pd.concat([df_ingr,df_sp_ingr],axis=1)
    return df_ingr,df_meas,df_quant,df_rec

df_ingr,df_meas,df_quant,df_rec=dl_data()

def get_recipe(str_recipe):
    return df_rec.at[0,str_recipe]

def get_recipe_no(str_recipe):
    return df_rec.at[1,str_recipe]

def get_df_ingr(str_recipe,multiplier=1):
    df_1=df_quant[str_recipe]*multiplier
    df_1=df_1.rename('quantity')
    df_1=pd.to_numeric(df_1)
    df_2=df_meas[str_recipe]
    df_2=df_2.rename('measure')
    df_3=df_ingr[str_recipe]
    df_3=df_3.rename('ingredient_name')

    df_out=pd.concat([df_1,df_2,df_3],axis=1)
    df_out.dropna(axis = 0, how = 'all', inplace = True)
    df_out.drop(df_out[df_out['quantity'] <=0].index, inplace = True)

    return df_out

def get_list(recipe_array,multiplier):

    #multiply individually, then combine
    df_combined=get_df_ingr(recipe_array[0])[0:0]
    for i in range(len(recipe_array)):
        df_combined=pd.concat([df_combined,get_df_ingr(recipe_array[i],multiplier[i])])

    df_combined=df_combined.groupby(['ingredient_name'],as_index=False, sort=False).agg({'quantity': 'sum','measure':'first'})

    #now concatenate columns to get single ingredients list
    df_out = df_combined[['quantity','measure','ingredient_name']]
    df_out.fillna('',inplace=True)
    df_out[df_out['measure']=="None"]=""
    df_out['quantity']=df_out['quantity'].apply(lambda x: f'{x:.0f}' if x%1==0 else str(x))
    df_out['ingredients']=df_out['quantity'] + df_out['measure'] + " " + df_out['ingredient_name']
    df_out=df_out.drop(columns=['quantity','measure','ingredient_name'], axis=1)

    return df_out

def get_spice_pots(recipe_array):
    #multiply individually, then combine
    df_combined=get_df_ingr(recipe_array[0])[0:0]
    df_combined=df_combined.drop(columns=['quantity','measure','ingredient_name'],axis=1)
    for i in range(len(recipe_array)):
        df_i=get_df_ingr(recipe_array[i])
        df_sp_i=df_i.loc[df_i['ingredient_name'].str.contains('spice pot')]
        if len(df_sp_i)>0:
            #check if we have spice pot:
                if df_sp_i['ingredient_name'].iat[0] in df_ingr.columns:
                    ingred_list_i=get_list([df_sp_i['ingredient_name'].iat[0]],[1])
                    ingred_list_i.rename(columns={"ingredients":(str(1) + " " + df_sp_i['ingredient_name'].iat[0]) }, inplace=True)
                    df_combined=pd.concat([df_combined,ingred_list_i],axis=1)
                else:
                    df_combined[(str(1) + " " + df_sp_i['ingredient_name'].iat[0])]=""
                    df_combined[(str(1) + " " + df_sp_i['ingredient_name'].iat[0])].iat[0]="We do not have this, please check original card"

    df_combined.fillna('',inplace=True)
    return df_combined

def get_sainsburys_link(recipe_array,multiplier):
    #multiply individually, then combine
    df_combined=get_df_ingr(recipe_array[0])[0:0]
    for i in range(len(recipe_array)):
        df_combined=pd.concat([df_combined,get_df_ingr(recipe_array[i],multiplier[i])])

    df_combined=df_combined.groupby(['ingredient_name'],as_index=False, sort=False).agg({'quantity': 'sum','measure':'first'})

    #now concatenate columns to get single ingredients list
    df_out = df_combined[['quantity','measure','ingredient_name']]
    df_out.fillna('',inplace=True)
    df_out=df_out.drop(columns=['quantity','measure'], axis=1)
    ls_out=df_out['ingredient_name'].tolist()
    str_out=",".join(ls_out)
    sains_link="https://www.sainsburys.co.uk/gol-ui/SearchResults/"
    return sains_link + str_out

def load_meals():
    list_meals=list(df_rec.columns)
    list_numbers=df_rec.loc[1,:].values.flatten().tolist()
    list_numbers=[str(x) for x in list_numbers]
    list_out=[m+": " + str(n) for m,n in zip(list_numbers,list_meals)]
    return list_out


API_TOKEN = '6522058518:AAHYQS2_J0Lz2F_gX_lrd_jt6tjSOxNyN84'

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Hi there, ich bin your Riverford chatbot. I am here to help you with your mealplan - what can I do for you?")





def save_meal(meal):
    with open(MEALS_FILENAME, 'a') as f:
        f.write(meal + '\n')


@bot.message_handler(commands=['suggest'])
def suggest(msg):
    try:
        meals = load_meals()
        suggestions = random.sample(meals, min(3, len(meals)))
        bot.send_message(msg.chat.id, '\n'.join(suggestions))
    except Exception as e:
        print(e)
        bot.send_message(msg.chat.id, "Failed to suggest meals")
        return



@bot.message_handler(commands=['add'])
def add(msg):
    msg_start = '/add '
    try:
        meal = msg.text[len(msg_start):]
        save_meal(meal)
        bot.send_message(msg.chat.id, "New meal added")
    except Exception as e:
        bot.send_message(msg.chat.id, "Failed to add meal")

@bot.message_handler(commands=['all'])
def all(msg):
    try:
        meals = load_meals()
        bot.send_message(msg.chat.id, '\n'.join(meals))
    except Exception as e:
        return

@bot.message_handler(commands=['recipe'])
def recipe(msg):
    try:
        bot.send_photo(msg.chat.id,
                       'https://media.riverford.co.uk/images/photo-2600x1040-196a4c7baadddd70ed4e2f8e2a086170.jpg'
                       )
    except Exception as e:
        print(e)
        bot.send_message(msg.chat.id, "Failed to send recipe")
        return

@bot.message_handler(commands=['recipe'])
def suggest(msg):
    try:
        meals = load_meals()
        suggestions = random.sample(meals, min(2, len(meals)))
        sent_message=bot.send_message(msg.chat.id, '\n'.join(suggestions))
        bot.send_message(msg.chat.id,"If you would like to see the ingredients for any of these recipes, please reply with the number")
        bot.register_next_step_handler(sent_message,rec_handler)
    except Exception as e:
        print(e)
        bot.send_message(msg.chat.id, "Failed to suggest meals")
        return

def sign_handler(message):
    text = ""
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, rec_handler)

def rec_handler(message):
    recipe_str = message.text
    text = "What day do you want to know?\nChoose one: *TODAY*, *TOMORROW*, *YESTERDAY*, or a date in format YYYY-MM-DD."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")


import requests


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

@bot.message_handler(commands=['info'])
def info(msg):
    try:
        bot.send_message(msg.chat.id, "/info - list all bot interactions\n"
                                      "/add <meal name> - add a new meal\n"
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