import telegram
from telegram.ext import *
import logging, requests, csv, json

token = '567792160:AAHHkjURiYh5s2GSQm-YzMq7tVdFf-7PLJo'

jsonfile = open('file.json', 'w')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):
    update.message.reply_text('Que rica estaba la torta!!')


def echo(bot, update):
    update.message.reply_text(update.message.text)

def main():
    # Manejador de eventos 
    updater = Updater(token)

    dp = updater.dispatcher

    # Reconocer los siguientes eventos
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # Start
    updater.start_polling()
    updater.idle()

    getCsv()


if __name__ == '__main__':
    main()

def getCsv():
    url = "https://data.buenosaires.gob.ar/api/files/cajeros-automaticos.csv/download/csv"
    r = requests.get(url, allow_redirects=True)
    csvToJson(r.content)
    #open('cajerosCsv.csv', 'wb').write(r.content)

def csvToJson(csvFile):
    fieldnames = ('ID','LAT','LNG','BANCO','RED','DOM_GEO','TERMINALES','WEB','ACTUALIZAC','DOM_NORMA','BARRIO','COMUNA','CODIGO_POSTAL','CODIGO_POSTAL_ARGENTINO')
    reader = csv.DictReader( csvFile, fieldnames)
    for row in reader:
        json.dump(row, jsonfile)
        jsonfile.write('\n')