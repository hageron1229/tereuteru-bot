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

"""
#####################################

with open("discord_token.txt",mode="r") as f:
	token = f.read()

#####################################

#共通
import discord
import asyncio

#定数系
from c_settings import *

#言語セット
from lang_set import lang

#ログ系
from my_log import *

#database
from my_database import DB

#bot
from my_bot import bot_init

############################################################################################################
Intents = discord.Intents.default()
Intents.members = True
client = discord.Client(intents=Intents)

#データベースインスタンスに接続
database = DB()

#チャンネルごとのインスタンスの管理
insts = {}

@client.event
async def on_ready():
	st = discord.Activity(name=BOT_STATUS,type=discord.ActivityType.listening)
	await client.change_presence(status=discord.Status.online,activity=st)
	print("I'm ready.")

@client.event
async def on_message(message):
	if message.author != client.user:
		if type(message.channel)==discord.DMChannel:
			#embedの最後に記載されているchannel id
			channel_id = reaction.message.embeds[0].fileds[-1]["value"]
			if channel_id in insts:
				await insts[channel_id].on_message_dm(message)
			else:
				err("ON_MESSAGE","不明な行先のDM")
		elif message.content.startswith(cmd_prefix+" "):
			allow_cmds = ["r","ur","n"]
			arg = message.content.split(cmd_prefix+" ")[1].split()
			if arg[0]=="r" and len(arg)==2:
				res = database.register(message.channel.guild.id,arg[1])
				log("ON_MESSAGE","register")
				#コマンドに関するメッセージは削除
				await message.delete()
			elif arg[0]=="ur" and len(arg)==2:
				res = database.unregister(message.channel.guild.id,arg[1])
				log("ON_MESSAGE","unregister")
				#コマンドに関するメッセージは削除
				await message.delete()
			elif arg[0]=="n":
				if message.channel.id in insts:
					await insts[message.channel.id].del_()
				insts[message.channel.id] = await bot_init(client,message)
				log("ON_MESSAGE","init")
				#コマンドに関するメッセージは削除
				await message.delete()
			else:
				if message.channel.id in insts:
					await insts[message.channel.id].on_message(message)
				log("インスタンスに送るコマンド",message.content)
		else:
			log("コマンドではない")

@client.event
async def on_reaction_add(reaction, user):
	if client.user != user:
		if type(reaction.message.channel)==discord.DMChannel:
			#embedの最後に記載されているchannel id
			channel_id = reaction.message.embeds[0].fileds[-1]["value"]
			if channel_id in insts:
				await insts[channel_id].on_reaction_add_dm(reaction,user)
			else:
				err("ON_REACTION_ADD","不明な行先のDM")

		elif reaction.message.channel.id in insts:
			await insts[reaction.message.channel.id].on_reaction_add(reaction,user)

# amu連携機能は後で
# @client.event
# async def on_raw_message_edit(payload):
# 	if payload.channel_id in insts:
# 		await insts[payload.channel_id].receive_raw_mes_edit(payload)


client.run(token)

############################################################################################################