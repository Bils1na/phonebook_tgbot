import telebot
from telebot import types
from config import token, FILE, commands
import json
import random


phonebook = {}
adding_new_contact = {}
bot = telebot.TeleBot(token)
with open(FILE, "r", encoding="utf-8") as f:
    phonebook = json.load(f)
bot.set_my_commands(commands)


# look all contacts
@bot.message_handler(commands=["all"])
def get_all(message):
    number = 1
    bot.send_message(message.chat.id, "Here is your list of contacts")
    for k, v in phonebook.items():
        bot.send_message(message.chat.id, f"""{number}. *{k.title()}*:
{list(v.keys())[0].title()}: {v["phones"]}
{list(v.keys())[1].title()}: {v["place"].title()}""", parse_mode="Markdown")
        number += 1

# add a new contact in list
@bot.message_handler(commands=["add"])
def add_new_contact(message):
    bot.send_message(message.chat.id, "Enter the name for the new contact")
    bot.register_next_step_handler(message, add_contact_name)

def add_contact_name(message):
    adding_new_contact[message.chat.id] = {"name": message.text}
    bot.send_message(message.chat.id, "Enter the number of phone")
    bot.register_next_step_handler(message, add_contact_phone)

def add_contact_phone(message):
    adding_new_contact[message.chat.id]["phones"] = message.text.split()
    bot.send_message(message.chat.id, "Enter the name of place")
    bot.register_next_step_handler(message, add_contact_city)

def add_contact_city(message):
    adding_new_contact[message.chat.id]["place"] = message.text
    save_contact_data(message.chat.id)
    bot.send_message(message.chat.id, "The new contact successfully added")

def save_contact_data(chat_id): # Save the new contact in phonebook
    contact_data = adding_new_contact.pop(chat_id)
    name = contact_data["name"].lower()
    phonebook[name] = {
        "phones": contact_data["phones"],
        "place": contact_data["place"].lower()
    }


# save list of contacts in json file
@bot.message_handler(commands=["save"])
def save_contact(message):
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(phonebook, ensure_ascii=False))
    bot.send_message(message.chat.id, "Data has saved")

# look contact by name
@bot.message_handler(commands=["look"])
def get_name(message):
    bot.send_message(message.chat.id, "Enter the name of contact you want to find")
    bot.register_next_step_handler(message, look_contact)

def look_contact(message):
    try:
        name = message.text.lower()
        bot.send_message(message.chat.id,f"""Phones: {phonebook[name]["phones"]}
Place: {phonebook[name]["place"].title()}""")
    except:
        bot.send_message(message.chat.id, "This contact was not found")

# Bot menu
@bot.message_handler(content_types=["text"]) 
def greetings(message): 
    if message.text == '/menu':
        button = types.InlineKeyboardMarkup()
        button.add(types.InlineKeyboardButton("Look all my contacts", callback_data="/all"))
        bot.send_message(message.chat.id, """Hello there! I'm Bilsina's phonebook.
You can looked, found, saved and changed data here.
                         
If you want to add a new contact, you have to send a message:
                /add
                         
If you want to look single contact, you have to send message:
                /look
                         
For save your new contacts, you have to send message:
                /save""", reply_markup=button)

# Call the list of the contacts
@bot.callback_query_handler(func = lambda callback: True)
def callback_all(callback):
    get_all(callback.message)
        
# t.me/bils1n_phonebook_bot 
bot.polling()
