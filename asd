import requests, csv, json, os
import urllib

testfile = urllib.URLopener()
testfile.retrieve("https://data.buenosaires.gob.ar/api/files/cajeros-automaticos.csv/download/csv", "cajeros.csv")

reader = csv.reader(open('cajeros.csv', 'r'))
d = {}
for row in reader:
    k, v = row
    d[k] = v