import telegram
from telegram.ext import *
import requests, csv, json, geopy.distance, geocoder, random, os, os.path, time, signal

token = '567792160:AAHHkjURiYh5s2GSQm-YzMq7tVdFf-7PLJo'
list_dic = []
MAX_EXTRAC = 1000
MAX_METROS_BUSQUEDA = 500
MY_COORD = "" #Para testear desde otra ubicacion (formato: "-34.581407, -58.440111")
HORAS_ENTRE_ACTU = 24

consultas = open("consultas.json","a+")

def me(bot,update):
    myPos = geocoder.ip("me").latlng
    update.message.reply_text(myPos)

def link(bot, update):
    manejarCommand(bot, update,"LINK")
    
def banelco(bot, update):
    manejarCommand(bot, update,"BANELCO")
    
def manejarCommand(bot, update, tipoCajero):
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

def filtrarMaxDistance(lista):
    return list(filter(lambda d: d["DISTANCE"] <= MAX_METROS_BUSQUEDA/1000, lista))

def quitarEstimadosVacios(lista):
    if os.stat("consultas.json").st_size == 0:    
        json.dump({"0":0},consultas)
    consultas.seek(0)
    datos = json.load(consultas)
    return list(filter(lambda d: datos.get(d["ID"],0)<MAX_EXTRAC ,lista))

def calcularDistancias(lista):
    myPos = MY_COORD if MY_COORD!="" else geocoder.ip("me").latlng
    for cajero in lista:
        posCajero = (float(cajero["LAT"].replace(",",".")), float(cajero["LNG"].replace(",",".") ))
        cajero["DISTANCE"] = geopy.distance.vincenty(myPos, posCajero).km
    return lista

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

def devolverMapa(cajeros,bot,update):
    markers = ""
    colores = ["blue","green","red"]

    for idx,c in enumerate(cajeros):
        latlang = c["LAT"].replace(",",".") + "," + c["LNG"].replace(",",".")
        markers += "&markers=color:{color}%7Clabel:{id}%7C{cord}".format(color=colores[idx],id=str(idx+1),cord=latlang)

    tuCord = MY_COORD if MY_COORD!="" else ','.join(map(str,geocoder.ip("me").latlng))

    url = "https://maps.googleapis.com/maps/api/staticmap?size=600x400&maptype=roadmap&markers=color:yellow%7Clabel:T%7C{tu}{markers}&key=AIzaSyDtFJmOZiEyqegfXU2gY_A2AlrFSCl9C2c".format(tu=tuCord, markers = markers)
    bot.send_photo(chat_id=update.message.chat.id, photo=url)

def main():
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("link", link))
    dp.add_handler(CommandHandler("banelco", banelco))
    dp.add_handler(CommandHandler("me", me))
    updater.start_polling()

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

if __name__ == '__main__':
    main()