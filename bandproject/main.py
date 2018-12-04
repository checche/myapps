#pickle作成に用いる

from scrapemethods import *
import pandas as pd
#from livecalendar.models import Live, Band, Place
import datetime
import pickle
import sys
sys.setrecursionlimit(100000)

dfmain = pd.DataFrame(columns = ['Date', 'Place', 'Title', 'Band', 'Open', 'Start'])

zeela =['http://osaka-zeela.jp/live.html?y=YEAR&m=MONTH', '梅田Zeela']
drop=['http://clubdrop.jp/live.html?y=YEAR&m=MONTH', 'アメリカ村DROP']
vijon=['http://vijon.jp/live.html?y=YEAR&m=MONTH', '北堀江 club vijon']
varon=['http://osaka-varon.jp/live.html?y=YEAR&m=MONTH', '心斎橋VARON']
goith=['http://goith.jp/live.html?y=YEAR&m=MONTH','堺東Goith']

url=goith[0]
place=goith[1]

Y = ['2018','2019']
M = ['1','2','3','4','5','6','7','8','9','10','11','12']
for y in Y:
    for m in M:
        tmpurl = url.replace('MONTH', m).replace('YEAR', y)
        dftmp = liveInfoBOT(tmpurl,y,place)
        dfmain = dfmain.append(dftmp)

dfmain.to_pickle('./info.pkl')


"""
df_from_pkl = pd.read_pickle('./info.pkl')
for date, place, title, bandlist, open, start in zip(dfmain['Date'], dfmain['Place'], dfmain['Title'], dfmain['Band'], dfmain['Open'], dfmain['Start']):
    L = Live.objects.get_or_create(date=date, place=Place.objects.get_or_create(name=place)[0], title=title, open=open, start=start)[0]
    for bname in bandlist:
        L.band.add(Band.objects.get_or_create(name=bname)[0])
"""
