import telegram
from telegram.ext import *
import requests, csv, json, geopy.distance, random, os, os.path

token = '567792160:AAHHkjURiYh5s2GSQm-YzMq7tVdFf-7PLJo'
list_dic = []
MAX_EXTRAC = 1000
MAX_METROS_BUSQUEDA = 500
CUSTOM_COORD = "-34.581600,-58.421050" #Para testear desde otra ubicacion (ejemplo funcional: "-34.581600,-58.421050")
USER_COORD = "" #Var Global. Seteada al enviar ubicacion

consultas = open("consultas.json","a+")

def link(bot, update):
    manejarCommand(bot, update,"LINK")
    
def banelco(bot, update):
    manejarCommand(bot, update,"BANELCO")

def manejarCommand(bot, update, tipoCajero):
    if(CUSTOM_COORD=="" and USER_COORD==""):
        update.message.reply_text("Debe permitir acceder a su ubicación. Use el comando /ubicacion")

    cajeros = select3Nearest(tipoCajero)

    if len(cajeros)!=0:
        update.message.reply_text(armarStringPantalla(cajeros))
        devolverMapa(cajeros,bot,update)
        registrarConsulta(cajeros)
    else:
        update.message.reply_text("No se encuentran cajeros automáticos cercanos")

def armarStringPantalla(cajeros):
    ret = []

    for idx, c in enumerate(cajeros):   
        line = "{id}. {banco} - {dir} \n".format(id=str(idx+1),banco=c["BANCO"],dir=c["DOM_ORIG"])
        ret.append(line)

    return ''.join(ret)

def select3Nearest(red):
    return quitarEstimadosVacios(sorted(filtrarMaxDistance(calcularDistancias(filtrarRed(red))), key=lambda k: k["DISTANCE"]))[:3]

def filtrarRed(tipo):
    return list(filter(lambda d: d["RED"]==tipo,list_dic))

def calcularDistancias(lista):
    myPos = list(map(float,(CUSTOM_COORD if CUSTOM_COORD!="" else USER_COORD).split(',')))

    for cajero in lista:
        posCajero = float(cajero["LAT"].replace(",",".")), float(cajero["LNG"].replace(",",".") )
        cajero["DISTANCE"] = geopy.distance.vincenty(myPos,posCajero).km

    return lista

def filtrarMaxDistance(lista):
    return list(filter(lambda d: d["DISTANCE"] <= MAX_METROS_BUSQUEDA/1000, lista))

def quitarEstimadosVacios(lista):
    if os.stat("consultas.json").st_size == 0:    
        json.dump({"0":0},consultas)
    consultas.seek(0)
    datos = json.load(consultas)

    return list(filter(lambda d: datos.get(d["ID"],0)<MAX_EXTRAC ,lista))

def devolverMapa(cajeros,bot,update):
    markers = ""
    colores = ["blue","green","red"]
    for idx,c in enumerate(cajeros):
        latlang = c["LAT"].replace(",",".") + "," + c["LNG"].replace(",",".")
        markers += "&markers=color:{color}%7Clabel:{id}%7C{cord}".format(color=colores[idx],id=str(idx+1),cord=latlang)
    tuCord = CUSTOM_COORD if CUSTOM_COORD!="" else USER_COORD

    url = "https://maps.googleapis.com/maps/api/staticmap?size=600x400&maptype=roadmap&markers=color:yellow%7Clabel:T%7C{tu}{markers}&key=AIzaSyDtFJmOZiEyqegfXU2gY_A2AlrFSCl9C2c".format(tu=tuCord, markers = markers)
    bot.send_photo(chat_id=update.message.chat.id, photo=url)

def registrarConsulta(cajeros):
    r = random.randint(0,100)
    if r < 70 or len(cajeros)==1: 
        sumarExtraccion(cajeros[0])
    elif r < 90 or len(cajeros)==2:
        sumarExtraccion(cajeros[1])
    else:
        sumarExtraccion(cajeros[2])

def sumarExtraccion(cajero):
    if os.stat("consultas.json").st_size == 0:    
        json.dump({"0":0},consultas)
    consultas.seek(0)
    datos = json.load(consultas)
    datos[cajero["ID"]] = datos.get(cajero["ID"],0)+1
    with open("consultas.json","w") as new:
        json.dump(datos,new)

def main():
    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("link", link))
    dp.add_handler(CommandHandler("banelco", banelco))
    dp.add_handler(CommandHandler("ubicacion", ubicacion))
    dp.add_handler(MessageHandler(Filters.location,location))

    updater.start_polling()

    with open("cajeros.csv",'w+'):
        if os.stat("cajeros.csv").st_size == 0:    
            getCsv()

    csvToDic()

    updater.idle()

def getCsv():
    r = requests.get("https://data.buenosaires.gob.ar/api/files/cajeros-automaticos.csv/download/csv") 
    with open("cajeros.csv",'wb') as f:
        f.write(r.content)
    
def csvToDic():
    reader = csv.DictReader(open('cajeros.csv', 'r'),delimiter=";")
    for line in reader:
        list_dic.append(line)

def ubicacion(bot,update): 
    reply_markup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton('Compartir ubicación', request_location=True, one_time_keyboard=True)]])
    
    bot.sendMessage(update.message.chat.id, "Presiona 'Compartir ubicación' para usar la aplicación", reply_markup=reply_markup)

def location(bot, update):
    global USER_COORD 
    user_location = update.message.location
    USER_COORD = str(user_location.latitude) + "," + str(user_location.longitude)

    update.message.reply_text("Gracias por compartir tu ubicación. Puede utilizar los comandos /link y /banelco")

if __name__ == '__main__':
    main()