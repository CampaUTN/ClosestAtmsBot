import schedule, requests, time, os, json

IMPORTAR_CSV_CADA = 48 #Horas

def getCsv():
    r = requests.get("https://data.buenosaires.gob.ar/api/files/cajeros-automaticos.csv/download/csv") 
    with open("cajeros.csv",'wb') as f:
        f.write(r.content)

def reiniciarConsultas():
    with open("consultas.json","w") as f:
        json.dump({"0":0},f)

schedule.every().monday.at("08:00").do(reiniciarConsultas)
schedule.every().tuesday.at("08:00").do(reiniciarConsultas)
schedule.every().wednesday.at("08:00").do(reiniciarConsultas)
schedule.every().thursday.at("08:00").do(reiniciarConsultas)
schedule.every().friday.at("08:00").do(reiniciarConsultas)

schedule.every(IMPORTAR_CSV_CADA).hours.do(getCsv)

while 1:
    schedule.run_pending()
    time.sleep(1)