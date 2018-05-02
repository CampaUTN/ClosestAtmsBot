import telegram
from telegram.ext import *
import requests, csv, json, geopy.distance, geocoder

token = '567792160:AAHHkjURiYh5s2GSQm-YzMq7tVdFf-7PLJo'
list_dic = []

def start(bot, update):
    update.message.reply_text("asd")

def link(bot, update):
    cajerosLink = select3Nearest("LINK")
    update.message.reply_text(armarStringPantalla(cajerosLink))
    devolverMapa(cajerosLink,bot,update)

def banelco(bot, update):
    cajerosLink = select3Nearest("BANELCO")
    update.message.reply_text(armarStringPantalla(cajerosLink))

#40.702147,-74.015794
def devolverMapa(cajeros,bot,update):
    c1 = cajeros[0]["LAT"].replace(",",".") + "," + cajeros[0]["LNG"].replace(",",".")
    c2 = cajeros[1]["LAT"].replace(",",".") + "," + cajeros[1]["LNG"].replace(",",".")
    c3 = cajeros[2]["LAT"].replace(",",".") + "," + cajeros[2]["LNG"].replace(",",".")

    url = '''https://maps.googleapis.com/maps/api/staticmap?zoom=13&size=600x300&maptype=roadmap&markers=color:blue%7Clabel:1%7C{cord1}&markers=color:green%7Clabel:2%7C{cord2}&markers=color:red%7Clabel:3%7C{cord3}
            &key=AIzaSyDtFJmOZiEyqegfXU2gY_A2AlrFSCl9C2c'''.format(cord1=c1,cord2=c2,cord3=c3)

    r = requests.get(url)
    bot.send_photo(chat_id=update.chat_id, photo=url)

def armarStringPantalla(cajeros):
    ret = []
    for idx, c in enumerate(cajeros):   
        line = "{id}. {banco} - {dir} \n".format(id=str(idx+1),banco=c["BANCO"],dir=c["DOM_ORIG"])
        ret.append(line)
    return ''.join(ret)

def getLink():
    print(select3Nearest("LINK"))

def getBanelco():
    print(select3Nearest("BANELCO"))

def select3Nearest(red):
    return sorted(calcularDistancias(filtrarRed(red)), key=lambda k: k["DISTANCE"])[:3]

def filtrarRed(tipo):
    return list(filter(lambda d: d["RED"]==tipo,list_dic))

def calcularDistancias(lista):
    myPos = geocoder.ip("me").latlng
    for cajero in lista:
        posCajero = (float(cajero["LAT"].replace(",",".")), float(cajero["LNG"].replace(",",".") ))
        cajero["DISTANCE"] = geopy.distance.vincenty(myPos, posCajero).km
    return lista

def main():
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("link", link))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("banelco", banelco))
    updater.start_polling()

    #getCsv()
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