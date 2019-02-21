import pandas as pd
import requests
from bs4 import BeautifulSoup
import lxml
import datetime
import datetime
import pickle
import sys

#taget_urlのページ上のライブ情報をDFにして返す.ex)target_url ='http://osaka-zeela.jp/live.html?y=2018&m=11'
def liveInfoBOT(target_url,Y,p):
    place = p

    df = pd.DataFrame(columns = ['Date', 'Place', 'Title', 'Band', 'Open', 'Start'])

    r = requests.get(target_url)#webから取得
    soup = BeautifulSoup(r.content, 'lxml')#要素抽出
    live_table = soup.find_all("table", attrs={'class':'listCal'})#指定した要素内のHTMLを取得

    for i, live in enumerate(live_table):
        rows = live.find_all('tr')#5つのtrが得られる
        day = rows[0].th.string#日付
        print(day)
        day = day.replace('/','-')#DateFieldの形に書き換え
        ymd = Y+'-'+day
        tdate = datetime.datetime.strptime(ymd, '%Y-%m-%d')
        livedate = datetime.date(tdate.year, tdate.month, tdate.day)#DateField
        title = rows[0].p.string#タイトル

        """get bandlist"""
        try:
            band = rows[2].strong.string#バンド名リストの文字列
            bandlist = band.split(' / ')#リスト化
        except AttributeError:
            bandlist=[]

        """get open/start"""
        rows[2].strong.extract()
        text = rows[2].prettify()#テキスト部読み込み
        lines = text.split('\n')#行ごとにリスト化
        ostext = lines[5].strip().strip('OPEN/START').strip()
        os = ostext.split('/')
        stropen = os[0]#オープン時間
        try:
            strstart = os[1]#スタート時間
        except IndexError:
            print("error:open,start couldn't be got")

        try:
            to = datetime.datetime.strptime(stropen, '%H:%M')
            ts = datetime.datetime.strptime(strstart, '%H:%M')
            open = datetime.time(to.hour, to.minute)#TimeField
            start = datetime.time(ts.hour, ts.minute)#TimeField
        except ValueError:
            print('error:open,start werent got')
            to = datetime.datetime.strptime('00:00', '%H:%M')
            ts = datetime.datetime.strptime('00:00', '%H:%M')
            open = datetime.time(to.hour, to.minute)#TimeField
            start = datetime.time(ts.hour, ts.minute)#TimeField
        df.loc[i] = [livedate, place, title, bandlist, open, start]#格納
    return df

#pickle作成に用いる
def makePickle(number):
    sys.setrecursionlimit(100000)
    dfmain = pd.DataFrame(columns = ['Date', 'Place', 'Title', 'Band', 'Open', 'Start'])
    zeela =['http://osaka-zeela.jp/live.html?y=YEAR&m=MONTH', '梅田Zeela']
    drop=['http://clubdrop.jp/live.html?y=YEAR&m=MONTH', 'アメリカ村DROP']
    vijon=['http://vijon.jp/live.html?y=YEAR&m=MONTH', '北堀江 club vijon']
    varon=['http://osaka-varon.jp/live.html?y=YEAR&m=MONTH', '心斎橋VARON']
    goith=['http://goith.jp/live.html?y=YEAR&m=MONTH','堺東Goith']
    place = [zeela,drop,vijon,varon,goith]
    Y = ['2018','2019']
    M = ['1','2','3','4','5','6','7','8','9','10','11','12']

    p=place[number]
    url=p[0]
    name=p[1]
    for y in Y:
        for m in M:
            tmpurl = url.replace('MONTH', m).replace('YEAR', y)
            dftmp = liveInfoBOT(tmpurl,y,name)
            dfmain = dfmain.append(dftmp)

    dfmain.to_pickle('./liveinfo/info.pkl')

def makeTable(lina):
    from livecalendar.models import Live, Band, Place
    df_from_pkl = pd.read_pickle('./liveinfo/{}.pkl'.format(lina))
    for date, place, title, bandlist, open, start in zip(df_from_pkl['Date'], df_from_pkl['Place'], df_from_pkl['Title'], df_from_pkl['Band'], df_from_pkl['Open'], df_from_pkl['Start']):
        L = Live.objects.get_or_create(date=date, place=Place.objects.get_or_create(name=place)[0], title=title, open=open, start=start)[0]
        for bname in bandlist:
            L.band.add(Band.objects.get_or_create(name=bname)[0])

if __name__ =='__main__':
    makePickle()
