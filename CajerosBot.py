import telegram
from telegram.ext import *
import requests, csv, json, geopy.distance, geocoder, random, os, os.path, time, signal

token = '567792160:AAHHkjURiYh5s2GSQm-YzMq7tVdFf-7PLJo'
list_dic = []
MAX_EXTRAC = 1000
MY_COORD = "" #Para testear desde otra ubicacion (formato: "-34.581407, -58.440111")
HORAS_ENTRE_ACTU = 24

consultas = open("consultas.json","a+")

def me(bot,update):
    myPos = geocoder.ip("me").latlng
    update.message.reply_text(myPos)

def link(bot, update):
    cajerosLink = select3Nearest("LINK")
    update.message.reply_text(armarStringPantalla(cajerosLink))
    devolverMapa(cajerosLink,bot,update)
    registrarConsulta(cajerosLink)

def banelco(bot, update):
    cajerosBanelco = select3Nearest("BANELCO")
    update.message.reply_text(armarStringPantalla(cajerosBanelco))
    devolverMapa(cajerosBanelco,bot,update)
    registrarConsulta(cajerosBanelco)

def devolverMapa(cajeros,bot,update):
    c1 = cajeros[0]["LAT"].replace(",",".") + "," + cajeros[0]["LNG"].replace(",",".")
    c2 = cajeros[1]["LAT"].replace(",",".") + "," + cajeros[1]["LNG"].replace(",",".")
    c3 = cajeros[2]["LAT"].replace(",",".") + "," + cajeros[2]["LNG"].replace(",",".")  
    tu = MY_COORD if MY_COORD!="" else ''.join(map(str,geocoder.ip("me").latlng))

    url = '''https://maps.googleapis.com/maps/api/staticmap?size=600x300&maptype=roadmap&markers=color:blue%7Clabel:1%7C{cord1}&markers=color:green%7Clabel:2%7C{cord2}&markers=color:red%7Clabel:3%7C{cord3}&markers=color:yellow%7Clabel:T%7C{tu}
            &key=AIzaSyDtFJmOZiEyqegfXU2gY_A2AlrFSCl9C2c'''.format(cord1=c1,cord2=c2,cord3=c3,tu=tu)

    bot.send_photo(chat_id=update.message.chat.id, photo=url)

def armarStringPantalla(cajeros):
    ret = []
    for idx, c in enumerate(cajeros):   
        line = "{id}. {banco} - {dir} \n".format(id=str(idx+1),banco=c["BANCO"],dir=c["DOM_ORIG"])
        ret.append(line)
    return ''.join(ret)

def select3Nearest(red):
    return quitarEstimadosVacios(sorted(calcularDistancias(filtrarRed(red)), key=lambda k: k["DISTANCE"]))[:3]

def filtrarRed(tipo):
    return list(filter(lambda d: d["RED"]==tipo,list_dic))

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
    if r < 70: 
        sumarExtraccion(cajeros[0])
    elif r < 90:
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