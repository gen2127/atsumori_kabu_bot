# インストールした discord.py を読み込む
import discord
import datetime
import re
from tabulate import tabulate
import matplotlib.pyplot as plt
import os
import pickle

# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.environ['DISCORD_BOT_ATSUMORIKABU_TOKEN']
# 接続に必要なオブジェクトを生成
client = discord.Client()

datapath = 'data.pickle'

# 起動時に動作する処理
@client.event
async def on_ready():
    # カブ価データを読み込む
    global d
    try:
        with open(datapath, mode='rb') as f:
            d = pickle.load(f)
    except FileNotFoundError:
        with open(datapath, mode='wb') as f:
            pass
        d = {}
    except EOFError:
        d = {}

    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/kabu (カブ価）」と発言したら発言者とカブ価を記録する処理
    if '/kabu' in message.content :
        ampm = ''
        if datetime.datetime.now().hour < 12 :
            ampm = 'AM'
        else :
            ampm = 'PM'
        num = int(re.sub("\\D","",message.content))
        if datetime.datetime.now().strftime('%Y/%m/%d')+ampm not in d :
            d.setdefault(datetime.datetime.now().strftime('%Y/%m/%d')+ampm,{})

        if message.author.name not in d[datetime.datetime.now().strftime('%Y/%m/%d')+ampm] :
            d[datetime.datetime.now().strftime('%Y/%m/%d')+ampm].setdefault(message.author.name,num)    
        d[datetime.datetime.now().strftime('%Y/%m/%d')+ampm][message.author.name] = num
        with open(datapath, mode='wb') as f:
            pickle.dump(d, f)
        #headers = ["header1", "header2"]
        table = list(d[datetime.datetime.now().strftime('%Y/%m/%d')+ampm].items())
        table.sort(key=lambda x:x[1],reverse=True)
        await message.channel.send(tabulate(table,tablefmt="plain"))
    print(d)
    if '/graph' in message.content :
        days = list(d.keys())
        d_graph = {}
        for i in days :
            names = list(d[i].keys())
            for j in names :
                if j not in d_graph :
                    d_graph.setdefault(j,{})
                if i not in d_graph[j] :
                    d_graph[j].setdefault(i,d[i][j])
                d_graph[j][i] = d[i][j]
        fig = plt.figure()
        for i in list(d_graph.keys()) :
            plt.plot(list(d_graph[i].keys()),list(d_graph[i].values()),label = i)
        plt.legend() # おそらく日本語で文字化けするがサーバのOSがわからないので対応できず
        fig.savefig('graph.png')
        await message.channel.send(file = discord.File('graph.png'))



# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)