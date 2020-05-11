# This Python file uses the following encoding: utf-8
# インストールした discord.py を読み込む
import discord
import datetime
import re
from tabulate import tabulate
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import os
import psycopg2
import psycopg2.extras
from kabu_judge import kabu_judge 

fontprop = FontProperties(fname='./fonts/NotoSansCJKjp-Medium.otf', size=10)

# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.environ['DISCORD_BOT_ATSUMORIKABU_TOKEN']

DATABASE_URL = os.environ['DATABASE_URL']

# 接続に必要なオブジェクトを生成
client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    d = {}
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/kabu (カブ価）」と発言したら発言者とカブ価を記録する処理
    if '/kabu' in message.content :
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        #conn = psycopg2.connect("dbname = test_atsumori")#試験用
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        d = {}
        ampm = ''
        if datetime.datetime.now().hour < 12 :
            ampm = 'AM'
        else :
            ampm = 'PM'
        sql = "SELECT name,val FROM kabu WHERE date = '"+str(datetime.date.today())+"' AND ampm = '"+ampm+"';"
        cur.execute(sql)
        d = dict(cur.fetchall())
        num = int(re.sub("\\D","",message.content))

        if message.author.name not in d :
            d.setdefault(message.author.name,num)
            sql = "INSERT INTO kabu values('"+str(datetime.date.today())+"','"+datetime.date.today().strftime('%a')+"','"+ampm+"','"+message.author.name+"',"+str(num)+");"
            cur.execute(sql)

        d[message.author.name] = num
        sql = "UPDATE kabu SET val = "+str(num)+"WHERE date = '"+str(datetime.date.today())+"' AND ampm = '"+ampm+"' AND name = '"+message.author.name+"';"
        cur.execute(sql)
        #headers = ["header1", "header2"]
        table = list(d.items())
        table.sort(key=lambda x:x[1],reverse=True)
        await message.channel.send(tabulate(table,tablefmt="plain"))
        conn.commit()
        cur.close()
        conn.close()
    print(d)
    if '/graph' in message.content :
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        #conn = psycopg2.connect("dbname = test_atsumori")#試験用
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        days = [datetime.date.today()-datetime.timedelta(days=(datetime.date.today().weekday()-6)%7-i) for i in range((datetime.date.today().weekday()-6)%7+1)]
        d_graph = {}
        for i in days :
            for ampm in ['AM','PM'] :
                sql = "SELECT name FROM kabu WHERE date = '"+str(i)+"' AND ampm = '"+ampm+"';"
                cur.execute(sql)
                names = cur.fetchall()
                for j in names :
                    sql = "SELECT val FROM kabu WHERE date = '"+str(i)+"' AND ampm = '"+ampm+"' AND name = '"+j[0]+"';"
                    cur.execute(sql)
                    val = cur.fetchall()
                    val = int(val[0][0])
                    if j[0] not in d_graph :
                        d_graph.setdefault(j[0],{})
                    if str(i)+ampm not in d_graph[j[0]] :
                        d_graph[j[0]].setdefault(str(i)+ampm,val)
                    d_graph[j[0]][str(i)+ampm] = val
        fig = plt.figure()
        for i in list(d_graph.keys()) :
            plt.plot(list(d_graph[i].keys()),list(d_graph[i].values()),label = i)
        plt.legend(prop=fontprop)
        fig.savefig('graph.png')
        await message.channel.send(file = discord.File('graph.png'))
        conn.commit()
        cur.close()
        conn.close()

    if '/judge' in message.content :
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        #conn = psycopg2.connect("dbname = test_atsumori")#試験用
        cur = conn.cursor()
        
        today = datetime.date.today()
        weekday = (today.weekday() + 1) % 7
        sunday = today - datetime.timedelta(days=weekday)

        sql = "SELECT name FROM kabu WHERE date BETWEEN '"+str(sunday)+"' AND '"+str(today)+"';"
        cur.execute(sql)
        namelist = set(cur.fetchall())

        weekdays = {'Mon':'月曜', 'Tue':'火曜', 'Wed':'水曜', 'Thu':'木曜', 'Fri':'金曜', 'Sat':'土曜'}
        result = ''
        for name in namelist:
            sql = "SELECT val,weekday,ampm FROM kabu WHERE name = '" + name[0] + "' AND date BETWEEN '"+str(sunday)+"' AND '"+str(today)+"';"
            cur.execute(sql)
            data = cur.fetchall()
            prices = {'名前' : name[0]}
            for d in data:
                if(d[1] == 'Sun'):
                    prices['日曜'] = d[0]
                else:
                    prices[weekdays[d[1]] + d[2]] = d[0]
            result += kabu_judge(prices).judge() + '\n'
        
        await message.channel.send(result)
        

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)