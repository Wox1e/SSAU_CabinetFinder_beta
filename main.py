import telebot
from telebot import types
from graph import *
from media_storage import save_file, get_file
from key_value_table import save_to_idTable, get_from_idTable
from config import BOT_TOKEN, TEMPLATE_IMAGE_FILENAME_SAVE, NODES_GROUP_NAME, PANORAMA_IMAGE_BUCKET, TEMPLATE_PANORAMA_IMAGE_FILENAME_SAVE, PANNELUM_URL, PANNELUM_PORT, \
MINIO_ENDPOINT

bot = telebot.TeleBot(BOT_TOKEN)


markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

buttons = [
    "/id_table",
    "/new_node",
    "/new_edge",
    "/path",
    "/nodes_list",
    "/add_panorama"
]

for button in buttons:
    markup.add(types.KeyboardButton(button))




@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-чмошник!", reply_markup=markup)

@bot.message_handler(commands=['id_table', 'table_id'])
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

@bot.message_handler(commands=['new_node','node_new'])
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

@bot.message_handler(commands=['new_edge', 'edge_new'])
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
                panorama_image_filename = node._properties["panorama_image"]
            except KeyError:
                panorama_image_filename = "3b6e95e3a1b9f54c7b1367c2e7863e2c.jpg" #default panorama

        

            #panorama_url = "PANNELLUME_SERVICE" + "BUCKET_URL" + panorama_image_filename
            image_url = "google.com" + "/" + PANORAMA_IMAGE_BUCKET + '/' + panorama_image_filename
            panorama_url = PANNELUM_URL + ":" + PANNELUM_PORT + "/src/standalone/pannellum.htm#panorama=" + image_url

            button_foo = types.InlineKeyboardButton('Панорама', callback_data='foo', url = panorama_url)

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(button_foo)

            try:
                name = node._properties["name"]
            except KeyError:
                pass
            
            local_filename = get_file(node._properties["image"])
            
            bot.send_photo(message.chat.id, photo=open(local_filename, 'rb'), caption=name, reply_markup = keyboard)
        

    bot.register_next_step_handler(message, message_input_step) #добавляем следующий шаг, перенаправляющий пользователя на message_input_step

@bot.message_handler(commands=['delete_node', 'node_delete'])
def delete_node(message):
    
    bot.send_message(message.from_user.id, " - Удаление точки -", reply_markup=markup)
    bot.send_message(message.from_user.id, "Введите id точки", reply_markup=markup)

    @bot.message_handler(content_types=['text'])  #Создаём новую функцию ,реагирующую на любое сообщение
    def message_input_step(message):
        id = message.text
        elementID = get_from_idTable(id)
        isDeleted = delete_Node(elementID)
        

    bot.register_next_step_handler(message, message_input_step) #добавляем следующий шаг, перенаправляющий пользователя на message_input_step

@bot.message_handler(commands=['nodes_list', 'list_nodes'])
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
            panorama_image_filename = node._properties["panorama_image"]
        except KeyError:
            panorama_image_filename = "3b6e95e3a1b9f54c7b1367c2e7863e2c.jpg" #default panorama

        
        #panorama_url = "PANNELLUME_SERVICE" + "BUCKET_URL" + panorama_image_filename
        image_url = "google.com" + "/" + PANORAMA_IMAGE_BUCKET + '/' + panorama_image_filename
        panorama_url = PANNELUM_URL + ":" + PANNELUM_PORT + "/src/standalone/pannellum.htm#panorama=" + image_url

        print(image_url, panorama_url)

        button_foo = types.InlineKeyboardButton('Панорама', callback_data='foo', url = panorama_url)

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(button_foo)


        try:
            name = node._properties["name"]
        except KeyError:
            pass
        
        id = node.id
        text = name + " -> " + str(id)
        local_filename = get_file(node._properties["image"])
        bot.send_photo(message.chat.id, photo=open(local_filename, 'rb'), caption=text, reply_markup = keyboard)

@bot.message_handler(commands=['add_panorama', 'panorama_add'])
def add_panorama(message):
    bot.send_message(message.from_user.id, "Отправьте панораму и id точки(одним сообщением)", reply_markup=markup)

    @bot.message_handler(content_types= ["photo", "text"])
    def message_input_step(message):
        
        
        properties = {"panorama_image":""}

        try:
            id = message.caption
            photo = message.photo[-1]
        except:
            print("Cannot get caption of photo")
            bot.send_message(message.from_user.id, "Непредвиденная ошибка...(Code 22)", reply_markup=markup)
            return

        try:
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(TEMPLATE_PANORAMA_IMAGE_FILENAME_SAVE, 'wb') as new_file:
                    new_file.write(downloaded_file)
        except:
            print("Cannot locally save the file")
            bot.send_message(message.from_user.id, "Непредвиденная ошибка...(Code 23)", reply_markup=markup)
            return

        try:
            image = save_file(TEMPLATE_PANORAMA_IMAGE_FILENAME_SAVE, PANORAMA_IMAGE_BUCKET)
        except:
            print("Cannot save image in bucket")
            bot.send_message(message.from_user.id, "Непредвиденная ошибка...(Code 24)", reply_markup=markup)
            return
        
        try:
            properties["panorama_image"] = image
            elementID = get_from_idTable(id)
            add_properties_to_node(elementID, properties)
        except:
            print("Cannot save to Neo4J or to redis")
            bot.send_message(message.from_user.id, "Непредвиденная ошибка...(Code 25)", reply_markup=markup)
            return

        bot.send_message(message.from_user.id, f"Успешно", reply_markup=markup)


    bot.register_next_step_handler(message, message_input_step)




# @bot.message_handler(commands=["test"])
# def test(message):

#     panorama_url = "https://cdn.pannellum.org/2.5/pannellum.htm#panorama=https://pannellum.org/images/alma.jpg"
#     button_foo = types.InlineKeyboardButton('Панорама', callback_data='foo', url = panorama_url)

#     keyboard = types.InlineKeyboardMarkup()
#     keyboard.add(button_foo)


#     bot.send_message(message.from_user.id, "/test", reply_markup=keyboard, parse_mode='HTML')
#     bot.send_photo(message.chat.id, photo=open(TEMPLATE_IMAGE_FILENAME_SAVE, 'rb'), caption="Какое-то название", reply_markup = keyboard)
 



bot.polling(none_stop=True, interval=0)


