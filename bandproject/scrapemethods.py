import pandas as pd
import requests
from bs4 import BeautifulSoup
import lxml
import datetime

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

if __name__ == '__main__':
    liveInfoBOT('http://osaka-zeela.jp/live.html?y=2018&m=2','2018')
