token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
bot_status = "「てるてる」モード"
cmd = ".aa"


#####################################

import time
import json
import copy
import random
import asyncio
import discord
from collections import defaultdict
from pprint import pprint

async def Among_us_init(message,client):
	t = Among_us(message.channel,client,True)
	# await t.hello()
	await t.init_()
	return t

class Among_us:
	def __init__(self,channel,client,boo=False):
		if boo==False:
			raise Exception("直接の初期化は禁止されています")
		self.channel = channel
		self.client = client
		self.message_main = -1
		self.syodaku = True
		self.hosting = True
		self.message = {
			# "latest":-1,
			# "dm": -1,
			# "imposter_check":-1,
			# "start":-1,
			# "syodaku":-1,
			# "this_game_bad":-1,
			# "unmute":-1,
		}
		self.imposter_check_receive = False
		self.game_word = "てるてる"
		self.member = []
		self.wait_ams = False
		self.amu_id = "未設定"
		self.mode = "bad1"
		self.status = None
		self.emoji = {
			"play":"\U000025B6",
			"stop":"\U000026D4",
			"maru":"\U00002B55",
			"batsu":"\U0000274C",
			"add":"\U000023EB",
			"back":"\U000023EC",
			"raise_hand":"\U0000270B",
			"next":"\U000023E9",
		}

	async def init_(self):
		embed = discord.Embed(title=f"拡張Among Us",description="",color=discord.Colour.green())
		embed.add_field(name="state",value="**RUNNING**")
		embed.add_field(name="game word",value="てるてる",inline=False)
		embed.add_field(name="game mode",value=self.mode,inline=False)
		embed.add_field(name="amu",value=self.amu_id,inline=False)
		embed.add_field(name="開発",value="[hageron1229/teruteru-bot](https://github.com/hageron1229/teruteru-bot)")
		self.message_main = await self.channel.send(embed=embed)
		await self.message_main.add_reaction(self.emoji["stop"])

	async def reload_main(self):
		if self.hosting:
			embed = discord.Embed(title=f"拡張Among Us",description="",color=discord.Colour.green())
			embed.add_field(name="state",value="**RUNNING**")
		else:
			embed = discord.Embed(title=f"拡張Among Us",description="",color=discord.Colour.red())
			embed.add_field(name="state",value="**STOPPING**")
		embed.add_field(name="game word",value="てるてる",inline=False)
		embed.add_field(name="game mode",value=self.mode,inline=False)
		embed.add_field(name="amu",value=self.amu_id,inline=False)
		embed.add_field(name="開発",value="[hageron1229/teruteru-bot](https://github.com/hageron1229/teruteru-bot)")
		await self.message_main.edit(embed=embed)
		await self.message_main.clear_reactions()
		if self.hosting:
			await self.message_main.add_reaction(self.emoji["stop"])
		else:
			await self.message_main.add_reaction(self.emoji["play"])

	async def del_(self):
		await self.message_main.delete()
		keys = copy.copy(self.message.keys())
		for key in keys:
			await self.delete_message(key)
		print("delete instance",self.channel.id)

	async def hello(self):
		s = "拡張among usを開始"
		modes = [
				["none","特殊ルール無し"],
				["bad1",f"{self.game_word}が1人選ばれる"],
				["bad2",f"{self.game_word}が1人選ばれる(imposterが選ばれた場合、{self.game_word}はなし)"]
				]

	async def receive_text(self,message):
		txt = message.content
		if txt.startswith(cmd+" "):
			com = txt.split(cmd+" ")[1].split()
			if com[0]=="mode":
				await self.set_mode(com[1])
			elif com[0]=="amu":
				await self.set_amu(com[1])
			elif com[0]=="start":
				await self.game_start()
			elif com[0]=="word" and len(com)==2:
				self.game_word = com[1]
				await self.reload_main()
			elif com[0]=="send_all":
				await self.channel.send_all()
			elif com[0]=="test":
				await self.test()
			elif com[0]=="random":
				await self.random_check()
			elif com[0]=="status" and len(com)==2:
				if com[1]=="end":
					for key in self.message.keys():
						await self.delete_message(key)
			elif com[0]=="unmuteall":
				await self.unmute()
			else:
				print("UNRECOGNIZE",com[0])
			await message.delete()
		else:
			if message.author!=self.client.user:
				#auto amu
				if message.content==".au n":
					self.wait_ams = True
				elif self.wait_ams and message.author.bot:
					self.wait_ams = False
					await self.set_amu(message.id)
					await self.reload_main()

	async def receive_reaction(self,reaction,user):
		if reaction.message.author==self.client.user:
			if type(self.message_main)!=int and reaction.message.id==self.message_main.id:
				if reaction.emoji==self.emoji["play"]:
					self.hosting = True
				elif reaction.emoji==self.emoji["stop"]:
					self.hosting = False
				await self.reload_main()
			elif self.imposter_check_receive:
				new_player = False
				for e_kind,alli,enem in [["maru",self.imposter,self.crewmate],["batsu",self.crewmate,self.imposter]]:
					if reaction.emoji==self.emoji[e_kind]:
						for d in self.member:
							if d["d_id"]==user.id:
								if d in enem:
									del enem[enem.index(d)]
								if d not in alli:
									alli.append(d)
								if d["a_name"] not in self.view_memo:
									self.view_memo.append(d["a_name"])
									new_player = True
								break
				if new_player:
					embed = self.message["imposter_check"].embeds[0]
					#voted = "、".join(self.view_memo)
					embed.set_field_at(0,name="投票済み",value=f"{len(self.view_memo)}/{len(self.member)}人",inline=False)
					await self.message["imposter_check"].edit(embed=embed)
				await reaction.remove(user)
				await self.game_bad1()
			elif self.mode=="bad1" or self.mode=="bad2":
				if not self.syodaku and "syodaku" in self.message and self.message["syodaku"].id==reaction.message.id and reaction.emoji==self.emoji["maru"]:
					self.syodaku = True
					await self.delete_message("syodaku")
					#承諾したタイミングでimposterチェックも削除する
					await self.delete_message("imposter_check")
					self.message["start"] = await self.channel.send("ゲームスタート！")
					#embed = discord.Embed(title=f"[UNMUTEALL]",description="全員のミュートが解除されます。\nてるてるがつられると自動でミュートが解除されます。",color=discord.Colour.blurple())
					#self.message["unmute"] = await self.channel.send(embed=embed)
					#await self.message["unmute"].add_reaction(self.emoji["next"])
					await self.game_started()
				elif "unmute" in self.message and self.message["unmute"].id==reaction.message.id and reaction.emoji==self.emoji["next"]:
					await self.unmute(tar="all")
					await reaction.remove(user)

	async def receive_raw_mes_edit(self,payload):
		mes = payload.cached_message
		feched = False
		if mes==None:
			mes = await self.channel.fetch_message(payload.message_id)
			feched = True
		if mes.author==self.client.user:
			return
		if feched==False:
			mes = await self.channel.fetch_message(payload.message_id)
		if mes.id==self.amu_id:
			await self.amu_change(mes)

	async def amu_change(self,mes):
		status = mes.embeds[0].title
		#await set_member()
		# print(status)
		# pprint(self.member)
		await self.change_status(status)

	async def unmute(self,tar="all"):
		if tar=="all":
			await self.channel.send(".au unmuteall")

	async def set_mode(self,mode):
		kouho = ["bad1","bad2"]
		if mode in kouho:
			self.mode = mode
			await self.channel.send("MODE : "+self.mode)
		else:
			await self.channel.send(f"MODE[{mode}]は定義されていません")

	async def change_status(self,s):
		s = s.upper()
		to_com = {
			"DISCUSSION":"DISCUSSION",
			"ロビー":"LOBBY",
			"LOBBY":"LOBBY",
			"GAME OVER":"END",
			"TASKS":"TASKS",
			"メインメニュー":"MENU",
			"Nain Menu":"MENU",
		}
		b_status = self.status
		a_status = to_com[s]
		print(b_status,"→",a_status)
		self.status = a_status

		if b_status=="LOBBY" and a_status=="TASKS":
			if self.hosting==False:
				return
			#game start
			await self.game_start()
			await self.set_member()
		elif b_status=="DISCUSSION" and a_status=="DISCUSSION":
			#つられた
			b_member = copy.deepcopy(self.member)
			await self.set_member()
			a_member = self.member
			print("b",b_member)
			print("a",a_member)
			for b_data in b_member:
				b_d_id = b_data["d_id"]
				discover = False
				for a_data in a_member:
					if a_data["d_id"]==b_d_id:
						discord = True
						break
				if discord and b_data["alive"]==True and a_data["alive"]==False:
					print("つられた",a_data["a_name"])
					await self.unmute()
					self.message["game_end"] = await self.channel.send("ゲーム終了！")
					return
		elif a_status=="END":
				await asyncio.sleep(10)
				await self.delete_message("start")
				await self.delete_message("game_end")



	async def set_amu(self,s):
		try:
			amu_id = int(s)
			mes = await self.channel.fetch_message(amu_id)
			self.amu_id = amu_id
			await self.reload_main()
			await self.change_status(mes.embeds[0].title)
		except Exception as e:
			print("!")
			print(e)
			print("!")
			await self.channel.send("amuが正しくありません")

	async def random_check(self):
		await self.set_member()
		n = 10000
		#body = f"### ランダムに{n}回選びます ###\n[TARGET:all]\n"
		names = defaultdict(int)
		for i in range(n):
			res = await self.random_one(self.member)
			names[res["a_name"]]+=1
		count_body = ""
		for k in sorted(names.keys()):
			count_body+=f"{k}：{names[k]}\n"
		embed = discord.Embed(title=f"[ランダムチェック({n}回)]",description=count_body,color=discord.Colour.green())
		await self.channel.send(embed=embed)

	async def random_one(self,kouho):
		ind = int(random.random()*(10**10)+time.time()+random.randint(0,len(kouho)-1))%len(kouho)
		return kouho[ind]

	async def bad_random_choice(self,kouho,add=""):
		# ind = int(random.random()*(10**10)+time.time())%len(kouho)
		# bad_data = kouho[ind]
		bad_data = await self.random_one(kouho)
		bad = await self.client.fetch_user(bad_data["d_id"])
		self.bad_target = bad_data
		#print(self.game_word+" :",bad_data["a_name"])
		print(self.game_word+" :",'##非公開##')

		self.message["dm"] = await bad.send("あなたが"+self.game_word+"に選ばれました"+add)

		s = self.game_word+"：||{} ({}){}||\n".format(bad_data["a_name"],self.channel.guild.get_member(bad_data["d_id"]).mention,"　"*(random.randint(10,25)))
		self.message["this_game_bad"] = await self.channel.send(s)
		s = self.game_word+"に選ばれた人は〇を押してください！"
		self.message["syodaku"] = await self.channel.send(s)
		await self.message["syodaku"].add_reaction(self.emoji["maru"])

		return bad

	async def check_imposter(self):
		#AuteMuteUsのプレイヤーの名前を変更する
		await self.change_name([d["d_id"] for d in self.member])
		#imposterの人を探す
		embed = discord.Embed(title="[imposterチェック]",description="あなたがimposterの場合には〇を、crewmateの場合は✕を選択してください",color=discord.Colour.orange())
		embed.set_image(url="http://drive.google.com/uc?export=view&id=114-NfgzzHkZjzwV_-759VfQp_8KfAEO7")
		embed.add_field(name="投票済み",value=f"0/{len(self.member)}人")
		r = await self.channel.send(embed=embed)
		self.imposter_check_receive = True
		await r.add_reaction(self.emoji["maru"])
		await r.add_reaction(self.emoji["batsu"])
		self.message["imposter_check"] = r

	async def send_all(self):
		res = await self.set_member()

		body = "### これはテストです ###\n"
		body += f"あなたは「{self.game_word}」に選ばれました\n"
		body += "### 以上 ###"
		for bad_data in self.member:
			bad = await self.client.fetch_user(bad_data["d_id"])
			print(self.game_word+" :",bad_data["a_name"])
			self.dm_message_test = await bad.send(body)

	async def delete_message(self,label):
		boo = False
		if label not in self.message:
			print(f"LABEL[{label}]はself.messageに定義されていません")
		elif self.message[label]==-1:
			#print(f"LABEL[{label}]はまだ送信されていません")
			pass
		else:
			try:
				await self.message[label].delete()
				boo = True
				del self.message[label]
			except:
				print(f"LABEL[{label}]の削除に失敗しました")
		return boo

	async def change_name(self,ids,nick="???"):
		self.changed = []
		for i in ids:
			member = self.channel.guild.get_member(i)
			if member==None:
				member = await self.change.guild.fetch_member(i)
			o_nick = member.nick
			try:
				await member.edit(nick=nick)
				self.changed.append([member,o_nick])
			except:
				print("ERROR",member.display_name)
		print("changed name")
		return self.changed

	async def return_name(self):
		for member,nick in self.changed:
			await member.edit(nick=nick)
		self.changed = []
		print("returned name")

	async def set_member(self):
		#automuteusのembedから参加者情報を読み取る
		#amuの設定に失敗している場合ERRORが出力され終了する
		try:
			mes = await self.channel.fetch_message(self.amu_id)
		except Exception as e:
			return -1

		#取得したmessageから情報の抽出
		embed = mes.embeds[0]
		player = []
		tar = embed.to_dict()["fields"]
		for item in tar:
			if item["value"].startswith("<:au"):
				t = {}
				t["a_name"] = item["name"]
				if "**未連携**" in item["value"]:
					print(f"ERROR : {item['name']}が未連携です")
					#return -2
					continue
				t["d_id"] = int(item["value"].split("<@!")[1][:-1])
				t["alive"] = "dead" not in item["value"]
				player.append(t)
		self.member = player
		pprint(self.member)
		return self.member

	async def game_init(self):
		self.syodaku = False
		self.imposter = []
		self.crewmate = []
		self.view_memo = []
		self.changed = []
		await self.return_name()

	async def game_start(self):
		#パラメータの初期化
		await self.game_init()

		#AutoMuteUsからプレーヤー情報を取得
		res = await self.set_member()

		#未連携のプレイヤーがいる場合は無効化し、連携を促す
		if res==-1:
			await self.channel.send("amuが正しく設定されていません")
			return
		elif res==-2:
			await self.channel.send(f"未連携の人がいるため、ゲームを開始できません")
			return

		#全メッセージ削除
		keys = copy.copy(self.message.keys())
		for key in keys:
			await self.delete_message(key)

		if len(self.member)==0:
			await self.channel.send("ロビーに入ってください")
			return

		if self.mode=="bad1":
			##imposterチェックを行う
			# imposter check
			await self.check_imposter()

			# reaction待ち
			#await game_bad1()をリアクションが呼び出す

		elif self.mode=="bad2":
			await game_bad2()

	async def game_bad1(self):
		if len(self.crewmate)+len(self.imposter)!=len(self.member) and self.imposter_check_receive:
			#まだ終わってない
			return
		self.imposter_check_receive = False

		#狂人をランダムでひとり選んでメッセージを送信する
		await self.bad_random_choice(self.crewmate)

	async def game_bad2(self):
		caution = "\nもしあなたがimposterだった場合、狂人は無しです"
		await self.bad_random_choice(self.member,add=caution)

	async def game_started(self):
		#ニックネームを戻す
		await self.return_name()

	async def test(self):
		print("testは無効です")
		return
		changed = []
		kari_name = "Among Us Player"
		async for member in self.channel.guild.fetch_members(limit=150):
			if not member.bot:
				nick = member.nick
				print(member.display_name)
				try:
					await member.edit(nick=kari_name)
					changed.append([member,nick])
				except:
					print("ERROR",member.display_name)
		await self.channel.send("changed name")
		await asyncio.sleep(10)
		for member,nick in changed:
			await member.edit(nick=nick)
		await self.channel.send("returned name")

############################################################################################################

insts = {}

async def divide(message=False,reactions=False):
	if reactions:
		reaction,user = reactions
		#何か参加していたらそいつに送る
		if reaction.message.channel.id in insts:
			await insts[reaction.message.channel.id].receive_reaction(reaction,user)
	elif message:
		if message.content==cmd+" n":
			c_id = message.channel.id
			if c_id in insts:
				await insts[c_id].del_()
			insts[c_id] = await Among_us_init(message,client)
			#await message.channel.send("てるてるbotスタート！")
			await message.delete()
		elif message.channel.id in insts:
			await insts[message.channel.id].receive_text(message)

############################################################################################################
Intents = discord.Intents.default()
Intents.members = True
client = discord.Client(intents=Intents)

@client.event
async def on_ready():
	st = discord.Activity(name=bot_status,type=discord.ActivityType.listening)
	await client.change_presence(status=discord.Status.online,activity=st)
	print("I'm ready.")

@client.event
async def on_message(message):
	if message.author != client.user:
		await divide(message=message)

@client.event
async def on_reaction_add(reaction, user):
	if client.user != user:
		await divide(reactions=(reaction,user))

@client.event
async def on_raw_message_edit(payload):
	if payload.channel_id in insts:
		await insts[payload.channel_id].receive_raw_mes_edit(payload)


client.run(token)

############################################################################################################