import telebot
from telebot import types
from config import token, FILE, commands
import json


phonebook = {}
adding_new_contact = {}
change_data = []
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
    adding_new_contact[message.chat.id]["phones"] = list(message.text.split())
    bot.send_message(message.chat.id, "Enter the name of place")
    bot.register_next_step_handler(message, add_contact_place)

def add_contact_place(message):
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

# look contact by name or number
@bot.message_handler(commands=["look"])
def get_name(message):
    button = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    name_button = types.KeyboardButton("Names")
    phone_button = types.KeyboardButton("Phones")
    search_button = types.KeyboardButton("Search")
    button.add(name_button, phone_button, search_button)

    bot.send_message(message.chat.id, "Which do you want to choose by names or by phone numbers?", reply_markup=button)
    bot.register_next_step_handler(message, look_option)

def look_option(message):
    chosen_option = message.text.lower()

    if chosen_option == "names":
        button = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for k, _ in phonebook.items():
            button.add(f"{k.title()}")

        bot.send_message(message.chat.id, "Which contact do you want to choose?", reply_markup=button)
        bot.register_next_step_handler(message, look_contact)

    elif chosen_option == "phones":
        button = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for _, v in phonebook.items():
            for phone in v["phones"]:
                button.add(f"{phone}")

        bot.send_message(message.chat.id, "Which number do you want to choose?", reply_markup=button)
        bot.register_next_step_handler(message, look_phone)

    elif chosen_option == "search":
        bot.send_message(message.chat.id, "Enter the name or the phone number")
        bot.register_next_step_handler(message, search_contact)

def look_contact(message):
    contact = message.text.lower()

    bot.send_message(message.chat.id,f"""Name: *{contact.title()}*
Phones: {phonebook[contact]["phones"]}
Place: {phonebook[contact]["place"].title()}""", parse_mode="Markdown")

def look_phone(message):
    contact = message.text.lower()

    for name, v in phonebook.items():
        for v1 in v["phones"]:
            if v1 == contact:
                bot.send_message(message.chat.id, f"""Name: *{name.title()}*
Phones: {phonebook[name]["phones"]}
Place: {phonebook[name]["place"].title()}""", parse_mode="Markdown")
                
def search_contact(message):
    contact = message.text.lower()
    exist = 0
    
    if contact.strip().isalpha() or len(contact.split()) > 1:
        for k, _ in phonebook.items():
            if contact in k:
                 bot.send_message(message.chat.id,f"""Name: *{k.title()}*
Phones: {phonebook[k]["phones"]}
Place: {phonebook[k]["place"].title()}""", parse_mode="Markdown")
                 exist = 1
        if exist != 1:
            bot.send_message(message.chat.id, "This contact was not found")
    else:
        for name, v in phonebook.items():
            for v1 in v["phones"]:
                if v1 == contact:
                    bot.send_message(message.chat.id, f"""Name: *{name.title()}*
Phones: {phonebook[name]["phones"]}
Place: {phonebook[name]["place"].title()}""", parse_mode="Markdown")
                    exist = 1
        if exist != 1:
                bot.send_message(message.chat.id, "This contact was not found")  

# delete the contact or phone numbers   
@bot.message_handler(commands=["delete"])
def get_del_contact(message):
    button = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for k, _ in phonebook.items():
        button.add(f"{k.title()}")

    bot.send_message(message.chat.id, "Enter the name of the contact", reply_markup=button)
    bot.register_next_step_handler(message, choose_data)

def choose_data(message):
    change_data.append(message.text.lower())

    button = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    contact_button = types.KeyboardButton("Contact")
    phone_button = types.KeyboardButton("Phone")
    button.add(contact_button, phone_button)

    bot.send_message(message.chat.id, "What do you want to delete?", reply_markup=button)
    bot.register_next_step_handler(message, execute_change)

def execute_change(message):
    chosen_option = message.text.lower()

    if chosen_option == "contact":
        del phonebook[change_data.pop()]
        bot.send_message(message.chat.id, "The contact deleted")
        save_contact(message)

    elif chosen_option == "phone":
        button = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for i in range(len(phonebook[change_data[0]]["phones"])):
            button.add(f"{phonebook[change_data[0]]['phones'][i]}") 

        bot.send_message(message.chat.id, "Which number do you want to delete?", reply_markup=button)
        bot.register_next_step_handler(message, delete_phone)

def delete_phone(message):
    chosen_phone = message.text
    phonebook[change_data.pop()]["phones"].remove(chosen_phone)
    bot.send_message(message.chat.id, "The number of phone deleted")
    save_contact(message)

# change data
@bot.message_handler(commands=["change"])
def choose_contact(message):
    button = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for k, _ in phonebook.items():
        button.add(f"{k.title()}")

    bot.send_message(message.chat.id, "Enter the name of contact you want to change", reply_markup=button)
    bot.register_next_step_handler(message, choose_operation)

def choose_operation(message):
    change_data.append(message.text.lower()) # contact name
    
    button = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    name_button = types.KeyboardButton("Name")
    phone_button = types.KeyboardButton("Phone")
    place_button = types.KeyboardButton("Place")
    button.add(name_button, phone_button, place_button)

    bot.send_message(message.chat.id, "What do you want to change?", reply_markup=button)
    bot.register_next_step_handler(message, perform_change)

def perform_change(message):
    chosen_option = message.text.lower()

    if chosen_option == "name":
        bot.send_message(message.chat.id, "Enter the new name of contact")
        bot.register_next_step_handler(message, replace_name)
    elif chosen_option == "phone":
        bot.send_message(message.chat.id, "Enter the new number of contact")
        bot.register_next_step_handler(message, replace_phone)
    elif chosen_option == "place":
        bot.send_message(message.chat.id, "Enter the new place of contact")
        bot.register_next_step_handler(message, replace_place)

def replace_name(message):
    contact = message.text.lower() # new contact name
    phonebook[contact] = phonebook.pop(change_data.pop())
    save_contact(message)

def replace_phone(message):
    contact = message.text # new contact phone number
    phonebook[change_data.pop()]["phones"] += [contact]
    save_contact(message)

def replace_place(message):
    contact = message.text
    phonebook[change_data.pop()]["place"] = contact
    save_contact(message)

# bot menu
@bot.message_handler(content_types=["text"]) 
def greetings(message): 
    if message.text == '/menu':

        button = types.InlineKeyboardMarkup()
        button.add(types.InlineKeyboardButton("Look all my contacts", callback_data="/all"))
        button.add(types.InlineKeyboardButton("Look single contact", callback_data="/look"))
        button.add(types.InlineKeyboardButton("Add", callback_data="/add"))
        button.add(types.InlineKeyboardButton("Save", callback_data="/save"))
        button.add(types.InlineKeyboardButton("Delete", callback_data="/delete"))
        button.add(types.InlineKeyboardButton("Change", callback_data="/change"))

        bot.send_message(message.chat.id, """Hello there! I'm Bilsina's phonebook.
You can looked, found, saved and changed data here.
                         
You can output all list of your contacts by:
                /all
                         
If you want to add a new contact, you have to send a message:
                /add
                         
If you want to look single contact, you have to send message:
                /look
                         
For save your new contacts, you have to send message:
                /save
            
For delete contact, you have to send message:
                /delete
                         
For changed data, you have to send message:
                /change
                         
Or you can use the buttons below.""", reply_markup=button)

# call options
@bot.callback_query_handler(func = lambda callback: True)
def callback_all(callback):
    if callback.data == "/all":
        get_all(callback.message)
    elif callback.data == "/add":
        add_new_contact(callback.message)
    elif callback.data == "/look":
        get_name(callback.message)
    elif callback.data == "/save":
        save_contact(callback.message)
    elif callback.data == "/delete":
        get_del_contact(callback.message)
    elif callback.data == "/change":
        choose_contact(callback.message)
        
# t.me/bils1n_phonebook_bot 
bot.polling()
