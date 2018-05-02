import telegram
from telegram.ext import *
import requests, csv, json, urllib, os
from io import StringIO

token = "567792160:AAHHkjURiYh5s2GSQm-YzMq7tVdFf-7PLJo"

#csvfile = open("cajeros.csv", "w+")
jsonfile = open("cajeros.json", "w+")

lista = []

def start(bot, update):
    update.message.reply_text("Que rica estaba la torta!!")

def donde(bot, update):
    update.message.reply_text(lista)

"""def echo(bot, update):
    update.message.reply_text(update.message.text)"""

def main():
    # Manejador de eventos 
    updater = Updater(token)

    dp = updater.dispatcher

    # Reconocer los siguientes eventos
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("donde", donde))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # Start
    updater.start_polling()

    getCsv()

    #jsonToObjects()
    
    #csvToObjects()

    updater.idle()

"""
https://maps.googleapis.com/maps/api/staticmap?
center=Brooklyn+Bridge,New+York,NY
&zoom=13&size=600x300&maptype=roadmap
&markers=color:blue%7Clabel:S%7C40.702147,-74.015794&markers=color:green%7Clabel:G%7C40.711614,-74.012318
&markers=color:red%7Clabel:C%7C40.718217,-73.998284
&markers=color:green%7Clabel:C%7C40.718217,-73.998284
&key=AIzaSyDtFJmOZiEyqegfXU2gY_A2AlrFSCl9C2c
"""

def jsonToObjects():
    data = json.load(jsonfile)


def csvToObjects():
    fieldnames = ("ID","LAT","LNG","BANCO","RED","DOM_ORIG","DOM_GEO","TERMINALES","WEB","ACTUALIZAC","DOM_NORMA","BARRIO","COMUNA","CODIGO_POSTAL","CODIGO_POSTAL_ARGENTINO")
    with open('cajeros.csv', 'r') as f:
        reader = csv.reader( f, fieldnames, delimiter=';')
        lista = list(reader)        

def getCsv():
    url = "https://data.buenosaires.gob.ar/api/files/cajeros-automaticos.csv/download/csv"
    response = requests.get(url)

    csvToJson(response)
    #guardarCsv(response)

def guardarCsv(response):
    with open('cajeros.csv', 'w+', encoding="utf-8") as f:
        writer = csv.writer(f)
        reader = csv.reader(response.text.splitlines())

        for row in reader:
            writer.writerow(row)

def csvToJson(r):
    fieldnames = ("ID","LAT","LNG","BANCO","RED","DOM_ORIG","DOM_GEO","TERMINALES","WEB","ACTUALIZAC","DOM_NORMA","BARRIO","COMUNA","CODIGO_POSTAL","CODIGO_POSTAL_ARGENTINO")
    mem = StringIO(r.content.decode("utf-8"))

    reader = csv.DictReader( mem, fieldnames, delimiter=';')
    jsonfile.write('[')
    for idx, row in enumerate(reader):
        if idx!=0:
            json.dump(row, jsonfile)
            jsonfile.write(',\n')
    jsonfile.write(']')

            
if __name__ == '__main__':
    main()



    