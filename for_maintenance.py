# 追加役職
# てるてる、狂人、恋人、スパイ、占い師
# teruteru,madmate,lovers,spy,diviner

"""
仕様
いつもはAutoMuteUsから情報を読み取っていた
AuteMuteUs連携モードとそうでないモードを作る
runmode: AMU, IND


cmd_prefix r xxx コードの登録
cmd_prefix ur コードの登録解除
cmd_prefix n ゲームの初期化

1時間操作がない状態が続いたらインスタンスを削除する
（5分おきにチェック？）

"""
#####################################

BOT_STATUS_MAINTENANCE = "Under maintenance"

with open("discord_token.txt",mode="r") as f:
	token = f.read()

#####################################

#共通
import time
import discord
import asyncio

import pytz
from datetime import datetime

#定数系
from c_settings import *

#言語セット
import lang_set

#ログ系
from my_log import *

#database
from my_database import DB

#bot
from my_bot import bot_init

#####################################

#インスタンス強制終了
#2時間で10分おきに監視
exit_hour = 2#/180
exit_interval_minute = 10#/100
async def force_exit():
	global insts
	while 1:
		force_exit_list = []
		for inst in insts:
			if insts[inst].last_run_time+exit_hour*3600<time.time():
				#終了
				await insts[inst].del_()
				force_exit_list.append(inst)
				log("FORCE_EXIT",f"{inst}は{exit_hour}時間経過したので強制終了")
			else:
				#終了しない
				t = insts[inst].last_run_time
				d = datetime.fromtimestamp(t, tz=pytz.timezone('Asia/Tokyo'))
				log("FORCE_EXIT",f"LAST RUN TIME: {d}({inst})")
		for inst in force_exit_list:
			del insts[inst]
		await asyncio.sleep(exit_interval_minute*60)

async def delete_me(channel_id):
	await insts[channel_id].del_()
	del insts[channel_id]



############################################################################################################
Intents = discord.Intents.default()
Intents.members = True
client = discord.Client(intents=Intents)

#データベースに接続
database = DB()

#チャンネルごとのインスタンスの管理
insts = {}

#force監視
asyncio.ensure_future(force_exit())

#dmの宛先管理
dm_address = {}

@client.event
async def on_ready():
	st = discord.Activity(name=BOT_STATUS_MAINTENANCE,type=discord.ActivityType.listening)
	await client.change_presence(status=discord.Status.online,activity=st)
	print("I'm ready.")

@client.event
async def on_message(message):
	if message.author != client.user:
		if message.channel.guild.id==839383474544705567 and message.content.startswith(cmd_prefix+" admin "):
			#管理サーバー用コマンド
			arg = message.content.split(cmd_prefix+" admin ")[1].split()
			if arg[0]=="maintenance" and len(arg)==2:
				if arg[1]=="1":
					await database.set_maintenance(True)
					await message.channel.send("メンテナンス　オン")
				else:
					await database.set_maintenance(False)
					await message.channel.send("メンテナンス　オフ")
			elif arg[0]=="running":
				await message.channel.send(f"稼働数 {len(insts)}")
			elif arg[0]=="act":
				if arg[1]=="new" and len(arg)==3:
					r = await database.create_activation_code(arg[2])
					await message.channel.send(r)
				elif arg[1]=="disable" and len(arg)==3:
					r = await database.disable_activation_code(arg[2])
					await message.channel.send(r)
		elif message.content.startswith(cmd_prefix+" "):
			await message.channel.send("ただいまメンテナンス中です。\nしばらくお待ちください。")
		else:
			log("コマンドではない")

@client.event
async def on_reaction_add(reaction, user):
	if client.user!=user:
		pass
# amu連携機能は後で
# @client.event
# async def on_raw_message_edit(payload):
# 	if payload.channel_id in insts:
# 		await insts[payload.channel_id].receive_raw_mes_edit(payload)


client.run(token)

############################################################################################################