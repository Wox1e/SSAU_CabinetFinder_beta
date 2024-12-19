import telebot
from telebot import types
from graph import *
from media_storage import save_file, get_file
from key_value_table import save_to_idTable, get_from_idTable
from config import BOT_TOKEN, TEMPLATE_IMAGE_FILENAME_SAVE, NODES_GROUP_NAME


bot = telebot.TeleBot(BOT_TOKEN)


markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(types.KeyboardButton("/id_table"))
markup.add(types.KeyboardButton("/new_node"))
markup.add(types.KeyboardButton("/new_edge"))
markup.add(types.KeyboardButton("/path"))
markup.add(types.KeyboardButton("/nodes_list"))


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-чмошник!", reply_markup=markup)

@bot.message_handler(commands=['id_table'])
def id_table(message):
    try:
        nodes = get_all_nodes()
    except:
        print("Failed to get nodes")
        bot.send_message(message.from_user.id, "Произошла ошибка...(Code 1)", reply_markup=markup)
        return
    
    bot.send_message(message.from_user.id, "Название : id", reply_markup=markup)

    for node in nodes:
        name = ""
        try:
            name = node._properties["name"]
        except KeyError:
            pass

        bot.send_message(message.from_user.id, f"{name}  :  {node.id}", reply_markup=markup)

@bot.message_handler(commands=['new_node'])
def new_node(message):

    properties = {
        "name":"",
        "image":""     
    }

    bot.send_message(message.chat.id, "Отправьте изображени ориентира и его название (одним сообщением) 👉👈")
    
    @bot.message_handler(content_types= ["photo", "text"])  #Создаём новую функцию ,реагирующую на любое сообщение
    def message_input_step(message):
        
        try:
            text = message.caption
            photo = message.photo[-1]
        except:
            print("Cannot get caption of photo")
            bot.send_message(message.from_user.id, "Непредвиденная ошибка...(Code 2)", reply_markup=markup)
            return

        try:
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(TEMPLATE_IMAGE_FILENAME_SAVE, 'wb') as new_file:
                new_file.write(downloaded_file)
        except:
            print("Cannot locally save the file")
            bot.send_message(message.from_user.id, "Непредвиденная ошибка...(Code 3)", reply_markup=markup)
            return

        try:
            image = save_file(TEMPLATE_IMAGE_FILENAME_SAVE)
        except:
            print("Cannot save image in bucket")
            bot.send_message(message.from_user.id, "Непредвиденная ошибка...(Code 4)", reply_markup=markup)
            return
        try:
            properties["name"] = text
            properties["image"] = image

            elementID = create_Node(NODES_GROUP_NAME, properties)
            id = elementID.split(":")[2]
            save_to_idTable(id, elementID)
        except:
            print("Cannot save to Neo4J or to redis")
            bot.send_message(message.from_user.id, "Непредвиденная ошибка...(Code 5)", reply_markup=markup)
            return
            
        
        bot.send_message(message.from_user.id, f"Точка {properties['name']} создана | id = {id}", reply_markup=markup)


    bot.register_next_step_handler(message, message_input_step)


@bot.message_handler(commands=['new_edge'])
def new_edge(message):

    bot.send_message(message.from_user.id, " - Создание новой связи -", reply_markup=markup) 
    bot.send_message(message.from_user.id, "Введите два id через пробел", reply_markup=markup)

    @bot.message_handler(content_types=['text'])  #Создаём новую функцию ,реагирующую на любое сообщение
    def message_input_step(message):
        
        try:
            text = message.text
            id1 = text.split(" ")[0]
            id2 = text.split(" ")[1]
        except:
            bot.send_message(message.from_user.id, "Вот балбес...", reply_markup=markup) 

        try:
            create_OneDirectionalEdge(get_from_idTable(id1), get_from_idTable(id2), "PATH")
        except:
            bot.send_message(message.from_user.id, "Ошибка, ёкарный бабай!", reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, "Успешно... Наверное -_-", reply_markup=markup)

    bot.register_next_step_handler(message, message_input_step) #добавляем следующий шаг, перенаправляющий пользователя на message_input_step

@bot.message_handler(commands=['path', 'get_path'])
def get_path(message):

    bot.send_message(message.from_user.id, "Введите два id через пробел", reply_markup=markup)

    @bot.message_handler(content_types=['text'])  #Создаём новую функцию ,реагирующую на любое сообщение
    def message_input_step(message):
        try:
            text = message.text
            id1 = text.split(" ")[0]
            id2 = text.split(" ")[1]
            nodes = get_path_between_nodes(get_from_idTable(id1), get_from_idTable(id2))
            bot.send_message(message.from_user.id, "Путь:", reply_markup=markup)
        except:
            print("Cannot return the path")
            bot.send_message(message.from_user.id, "Ошибка(Code 562). Некорректные id или пути не существует", reply_markup=markup)
            return

        for node in nodes:
            name = ""
            try:
                name = node._properties["name"]
            except KeyError:
                pass
            
            local_filename = get_file(node._properties["image"])
            
            bot.send_photo(message.chat.id, photo=open(local_filename, 'rb'), caption=name, reply_markup = markup)
        

    bot.register_next_step_handler(message, message_input_step) #добавляем следующий шаг, перенаправляющий пользователя на message_input_step

@bot.message_handler(commands=['delete_node'])
def delete_node(message):
    
    bot.send_message(message.from_user.id, " - Удаление точки -", reply_markup=markup)
    bot.send_message(message.from_user.id, "Введите id точки", reply_markup=markup)

    @bot.message_handler(content_types=['text'])  #Создаём новую функцию ,реагирующую на любое сообщение
    def message_input_step(message):
        id = message.text
        elementID = get_from_idTable(id)
        isDeleted = delete_Node(elementID)
        

    bot.register_next_step_handler(message, message_input_step) #добавляем следующий шаг, перенаправляющий пользователя на message_input_step

@bot.message_handler(commands=['nodes_list'])
def nodes_list(message):
    bot.send_message(message.from_user.id, " - Список точек -", reply_markup=markup)
    
    try:
        nodes = get_all_nodes()
    except:
        print("Cannot get nodes")
        bot.send_message(message.from_user.id, "Ошибка(Code 1562)", reply_markup=markup)
        return
    
    for node in nodes:
        name = ""

        try:
            name = node._properties["name"]
        except KeyError:
            pass
        
        id = node.id
        text = name + " -> " + str(id)
        local_filename = get_file(node._properties["image"])
        bot.send_photo(message.chat.id, photo=open(local_filename, 'rb'), caption=text, reply_markup = markup)



bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть



