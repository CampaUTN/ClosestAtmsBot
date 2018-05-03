import schedule, requests, time, os

IMPORTAR_CSV_CADA = 48 #Horas
REINICIAR_CONSULTAS_CADA = 24 #Horas

def getCsv():
    r = requests.get("https://data.buenosaires.gob.ar/api/files/cajeros-automaticos.csv/download/csv") 
    with open("cajeros.csv",'wb') as f:
        f.write(r.content)

def reiniciarConsultas():
    os.remove("consultas.json")

schedule.every(IMPORTAR_CSV_CADA).hours.do(getCsv)
schedule.every(REINICIAR_CONSULTAS_CADA).hours.do(reiniciarConsultas)

while 1:
    schedule.run_pending()
    time.sleep(1)