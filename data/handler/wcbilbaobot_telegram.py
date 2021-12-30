
# This example show how to write an inline mode telegramt bot use pyTelegramBotAPI.
import telebot
import time
import sys
import logging
import os 
import pymysql.cursors
from telebot import types

API_TOKEN=os.getenv("API_TOKEN")
db_host=os.getenv("DB_HOST")
db_user=os.getenv("DB_USER")
db_password=os.getenv("DB_PASSWORD")
db_name=os.getenv("DB_NAME")




user_dict = {}

acciones = types.ReplyKeyboardMarkup()
acciones.one_time_keyboard=True
acciones.resize_keyboard=True

accion1 = types.KeyboardButton(text="/aseo")
accion2 = types.KeyboardButton(text="/help")
acciones.add(accion1,accion2)
            
            
            
class urinario:
    def __init__(self, id,name, lat, lon):
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon

bot = telebot.TeleBot(API_TOKEN)
telebot.logger.setLevel(logging.DEBUG)

def getnearest(lat,lon):
    listacercanos = []

    connection = pymysql.connect(host=db_host,
                     user=db_user,
                     password=db_password,
                     db=db_name,
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor) 
    with connection.cursor() as cursor:
        connection.commit()
        # Read a single record
        lat= float(lat)
        lon = float(lon)
        
        cursor.execute("""SELECT id, name,lat,lon, ( 6371 * acos( cos( radians(%s) ) * cos( radians(wc_bilbao.lat) ) * cos( radians(wc_bilbao.lon ) - radians(%s) ) + sin( radians(%s) ) * sin( radians(wc_bilbao.lat ) ) ) ) AS distance FROM wc_bilbao ORDER BY distance LIMIT 3""", (str(lat),str(lon),str(lat),))

        resultado = cursor.fetchall()
        for row in resultado :
            elemento = urinario(row['id'],row['name'],row['lat'],row['lon'])
            listacercanos.append(elemento)    
        return listacercanos    
            

@bot.message_handler(commands=['aseo'])
def command_lon_text(m):
    cid = m.chat.id
    
    if(len(m.text.split())==1):
        markup = types.ReplyKeyboardMarkup()
        markup.one_time_keyboard=True
        markup.resize_keyboard=True
        itembtn = types.KeyboardButton(text="Mandar ubicacion",request_location=True)
        markup.add(itembtn)
        msg = bot.send_message(cid, 'Mandame tu ubicacion', reply_markup=markup)
        bot.register_next_step_handler(msg, process_ubicacion)


def process_ubicacion(message):
    try:
        cid = message.chat.id
        if(message.content_type == "location"):
            listacercanas=getnearest(float(message.location.latitude),float(message.location.longitude))
            bot.send_message(cid,"Estos son los 3 aseos más cercanos" )

            bot.send_message(cid,listacercanas[2].name)
            bot.send_location(cid,listacercanas[2].lat,listacercanas[2].lon, reply_markup=acciones)
            bot.send_message(cid,listacercanas[1].name)
            bot.send_location(cid,listacercanas[1].lat,listacercanas[1].lon, reply_markup=acciones)            
            bot.send_message(cid,listacercanas[0].name)
            bot.send_location(cid,listacercanas[0].lat,listacercanas[0].lon, reply_markup=acciones)

    except Exception as e:
        print(e)

# Handle '/lista'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    try: 
        cid = message.chat.id
        bot.reply_to(message, """\
    Hola, soy @aseosbilbao_bot y te daré la ubicación de los aseos públicos más cercanos .

    Mis comandos son los siguientes:
    - /aseo : Te pediré que me mandes la ubicación y a continuación te mandaré los 3 aseos más cercanos.
    - /help : Muestra esta ayuda

    Puedes contactar con el creador en la direccion botmakerdvd@gmail.com o en el perfil de twitter botmakerdvd
    """, reply_markup=acciones)
    
    except Exception as e:
        print(e)

        
def main_loop():
        try:
                bot.polling(True)
                while 1:
                        time.sleep(3)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'
        sys.exit(0)
