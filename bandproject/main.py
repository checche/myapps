#shellで実行

from scrapemethods import *
import pandas as pd
from livecalendar.models import Live, Band, Place
import datetime

dfmain = pd.DataFrame(columns = ['Date', 'Place', 'Title', 'Band', 'Open', 'Start'])

zeelaurl ='http://osaka-zeela.jp/live.html?y=YEAR&m=MONTH'
Y = ['2018','2019']
M = ['1','2','3','4','5','6','7','8','9','10','11','12']
for y in Y:
    for m in M:
        zeela = zeelaurl.replace('MONTH', m).replace('YEAR', y)
        dftmp = liveInfoBOT(zeela,y)
        dfmain = dfmain.append(dftmp)

dfmain.to_csv('./check.csv', encoding='utf-8')


#list型もstr型になってしまう.dfmain = pd.read_csv('./check.csv',encoding='utf-8')

for date, place, title, bandlist, open, start in zip(dfmain['Date'], dfmain['Place'], dfmain['Title'], dfmain['Band'], dfmain['Open'], dfmain['Start']):
    L = Live.objects.get_or_create(date=date, place=Place.objects.get_or_create(name=place)[0], title=title, open=open, start=start)[0]
    for bname in bandlist:
        L.band.add(Band.objects.get_or_create(name=bname)[0])
