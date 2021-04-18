token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
cmd = ".aa"


#####################################

import time
import json
import random
import asyncio
import discord
from collections import deque
from pprint import pprint

async def Among_us_init(channel,client):
	t = Among_us(channel,client,True)
	await t.hello()
	await t.init()
	return t

class Among_us:
	dec_num = 0
	def __init__(self,channel,client,boo=False):
		if boo==False:
			raise Exception("直接の初期化は禁止されています。")
		self.channel = channel
		self.client = client
		self.message = {
			"latest":-1,
			"dm": -1,
			"imposter_check":-1,
			"start":-1,
			"syodaku":-1,
			"this_game_kyojin":-1,
		}
		self.finish_watch_log = False
		self.game_word = "てるてる"
		self.member = []
		self.amu_id = -1
		self.mode = "kyojin1"
		self.state = "none"
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
		self.can_start = True
		# self.game_start_message = -1
		# self.syodaku_message = -1
		# self.this_game_kyojin = -1

	async def del_(self):
		Among_us.dec_num -= 1
		print("delete instance",Among_us.dec_num)
		pass

	async def hello(self):
		s = "拡張among usを開始"
		modes = [
				["none","特殊ルール無し"],
				["kyojin1","狂人が1人選ばれる"],
				["kyojin2","狂人が1人選ばれる(imposterが選ばれた場合、狂人はなし)"]
				]
		#await self.send(s)

	async def init(self):
		if Among_us.dec_num!=0:
			await self.send("[INTERNAL ERROR]\nこの機能は複数のチャンネルで使用することはできません。")
			raise Exception("複数拡張Among usの宣言の禁止")
			return
		Among_us.dec_num += 1

		#among us captureを監視する
		asyncio.ensure_future(self.start_watch_log())

	async def receve_text(self,message):
		txt = message.content
		prefix = cmd
		if txt.startswith(prefix+" "):
			com = txt.split(prefix+" ")[1].split()
			if com[0]=="mode":
				await self.set_mode(com[1])
			elif com[0]=="amu":
				self.amu_id = int(com[1])
				await self.send("amuをセット")
			elif com[0]=="start":
				await self.game_start()
			elif com[0]=="word" and len(com)==2:
				self.game_word = com[1]
			elif com[0]=="send_all":
				await self.send_all()
			elif com[0]=="test":
				await self.test()
			elif com[0]=="random":
				await self.random_check()
			elif com[0]=="status" and len(com)==2:
				if com[1]=="end":
					await self.status_end()
			else:
				print("UNRECOGNIZE",com[0])
			await message.delete()
		else:
			pass

	async def receve_reaction(self,reaction,user):
		if reaction.message.author==self.client.user:
			if self.mode=="kyojin1" and self.sent.id==reaction.message.id:
				new_player = False
				if reaction.emoji==self.emoji["maru"]:
					for d in self.member:
						if d["d_id"]==user.id:
							if d in self.imposter:
								break
							elif d in self.crewmate:
								del self.crewmate[self.crewmate.index(d)]
							self.imposter.append(d)
							if d["a_name"] not in self.view_memo:
								self.view_memo.append(d["a_name"])
								new_player = True
							break
				else:
					for d in self.member:
						if d["d_id"]==user.id:
							if d in self.crewmate:
								break
							elif d in self.imposter:
								del self.imposter[self.imposter.index(d)]
							self.crewmate.append(d)
							if d["a_name"] not in self.view_memo:
								self.view_memo.append(d["a_name"])
								new_player = True
							break
				# print("imposter", self.imposter)
				# print("crewmate", self.crewmate)
				# print("投票済み",self.view_memo)
				if new_player:
					embed = self.sent.embeds[0]
					voted = "、".join(self.view_memo)
					embed.set_field_at(0,name="投票済み",value=f"{len(self.view_memo)}人",inline=False)
					await self.sent.edit(embed=embed)
				await reaction.remove(user)
			elif self.mode=="kyojin1" or self.mode=="kyojin2":
				if not self.syodaku and self.syodaku_message.id==reaction.message.id and reaction.emoji==self.emoji["maru"]:
					self.syodaku = True
					await self.syodaku_message.delete()
					#承諾したタイミングでimposterチェックも削除する
					if self.sent!=-1:
						await self.sent.delete()
						self.sent = -1
					self.game_start_message = await self.send("ゲームスタート！")

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
		await self.send("changed name")
		await asyncio.sleep(10)
		for member,nick in changed:
			await member.edit(nick=nick)
		await self.send("returned name")

	async def set_member(self):
		#automuteusのembedから参加者情報を読み取る
		#amuの設定に失敗している場合ERRORが出力され終了する
		try:
			mes = await self.channel.fetch_message(self.amu_id)
		except Exception as e:
			print("ERROR")
			print(e)
			return

		#取得したmessageから情報の抽出
		embed = mes.embeds[0]
		player = []
		print(embed)
		tar = embed.to_dict()["fields"]
		pprint(tar)
		for item in tar:
			if item["value"].startswith("<:au"):
				t = {}
				t["a_name"] = item["name"]
				if "**未連携**" in item["value"]:
					print(f"ERROR : {item['name']}が未連携です。")
					return False
				t["d_id"] = int(item["value"].split("<@!")[1][:-1])
				player.append(t)
		self.member = player
		pprint(self.member)

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
		await self.send(embed=embed)

	async def random_one(self,kouho):
		ind = int(random.random()*(10**10)+time.time()+random.randint(0,len(kouho)-1))%len(kouho)
		return kouho[ind]

	async def kyojin_random_choice(self,kouho,add=""):
		# ind = int(random.random()*(10**10)+time.time())%len(kouho)
		# kyojin_data = kouho[ind]
		kyojin_data = await self.random_one(kouho)
		kyojin = await self.client.fetch_user(kyojin_data["d_id"])
		#print(self.game_word+" :",kyojin_data["a_name"])
		print(self.game_word+" :",'##非公開##')

		### test ###
		#exit()

		self.dm_message = await kyojin.send("あなたが"+self.game_word+"に選ばれました。"+add)

		s = self.game_word+"：||{}||\n".format(kyojin_data["a_name"]+"#"*(random.randint(1,25)+6))
		self.this_game_kyojin = await self.send(s)
		s = self.game_word+"に選ばれた人は〇を押してください！"
		self.syodaku_message = await self.send(s)
		await self.syodaku_message.add_reaction(self.emoji["maru"])

		return kyojin

	async def check_imposter(self):
		#全員の名前を一時的にAmong Us Playerに変更する

		#imposterの人を探す
		embed = discord.Embed(title="[imposterチェック]",description="あなたがimposterの場合には〇を、crewmateの場合は✕を選択してください。",color=discord.Colour.orange())
		embed.set_image(url="http://drive.google.com/uc?export=view&id=114-NfgzzHkZjzwV_-759VfQp_8KfAEO7")
		embed.add_field(name="投票済み",value="-")
		r = await self.send(embed=embed)
		await r.add_reaction(self.emoji["maru"])
		await r.add_reaction(self.emoji["batsu"])
		self.sent = r

	async def set_mode(self,mode):
		kouho = ["kyojin1","kyojin2"]
		if mode in kouho:
			self.mode = mode
		await self.send("MODE : "+self.mode)

	async def send_all(self):
		res = await self.set_member()

		body = "### これはテストです ###\n"
		body += f"あなたは「{self.game_word}」に選ばれました\n"
		body += "### 以上 ###"
		for kyojin_data in self.member:
			kyojin = await self.client.fetch_user(kyojin_data["d_id"])
			print(self.game_word+" :",kyojin_data["a_name"])
			self.dm_message_test = await kyojin.send(body)

	async def delete_message(self,label):
		boo = False
		if label not in self.message:
			print(f"LABEL[{label}]はself.messageに定義されていません。")
		elif self.message[label]==-1:
			print(f"LABEL[{label}]はまだ送信されていません。")
		else:
			try:
				await self.message[label].delete()
				boo = True
			except:
				print(f"LABEL[{label}]の削除に失敗しました。")
		return boo

	async def game_init(self):
		self.syodaku = False
		self.imposter = []
		self.crewmate = []
		self.view_memo = []

	async def change_name(self,ids,nick="Among Us Player"):
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
		print("returned name")


	async def game_start(self):
		#パラメータの初期化
		await self.game_init()

		#AutoMuteUsからプレーヤー情報を取得
		res = await self.set_member()

		#未連携のプレイヤーがいる場合は無効化し、連携を促す
		if res==False:
			await self.send("未連携の人がいるため、狂人を設定できません")
			return

		#狂人のmessageを削除
		await self.delete_message("this_game_kyojin")

		if self.mode=="kyojin1":
			##imposterチェックを行う

			#AuteMuteUsのプレイヤーの名前を変更する
			await self.change_name([self.member[d]["d_id"] for d in self.member])

			# imposter check
			await self.check_imposter()

			# reaction待ち
			await game_kyojin1()

		elif self.mode=="kyojin2":
			await game_kyojin2()

	async def game_kyojin1():
		if len(self.crewmate)+len(self.imposter)!=len(self.member):
			#まだ終わってない
			return

		#狂人をランダムでひとり選んでメッセージを送信する
		await self.kyojin_random_choice(self.crewmate)

		#ニックネームを戻す
		await self.return_name([self.member[d]["d_id"] for d in self.member])

	async def game_kyojin2():
		caution = "\nもしあなたがimposterだった場合、狂人は無しです。"
		user = await self.kyojin_random_choice(self.member,add=caution)

	async def send(self,content=False,embed=False,update=True):
		params = {}
		if content:
			params["content"] = content
		if embed:
			params["embed"] = embed
		r = await self.channel.send(**params)
		if update:
			self.latest_message = r
		return r

	async def stop_watch_log(self):
		self.finish_watch_log = True

	async def processing(self,do):
		#tmp {Name : name, IsDead: False, Disconnected: False, Color: color}
		if do.startswith("{"):
			data = json.loads(do)
			if self.state=="LOBBY":
				print("--CHANGED MEMBER--")
				#結局何もしない
		elif do.startswith("State change"):
			data = json.loads(do.split(": ")[1])
			self.state = data["NewState"]
			print("--CHANGED STATE--",self.state)
			if self.state=="ENDED":
				await status_end()
			elif self.state=="TASKS" and self.can_start:
				await self.game_start()
				self.can_start = False
		else:
			return
		print()

	async def status_end(self):
		self.can_start = True
		#ゲームが終わったらゲームスタートのテキストを削除する
		if self.game_start_message!=-1:
			await self.game_start_message.delete()
			self.game_start_message = -1
		#とりあえずDMに送ったmessageはそのままにしておく→やっぱ消す
		if self.dm_message!=-1:
			await self.dm_message.delete()
			self.dm_message = -1

############################################################################################################

insts = {}

async def new_inst(message,label):
	global insts
	c_id = message.channel.id

	if message.content.startswith(cmd+" n"):
		insts[c_id] = await Myams_init(message,client)
	else:
		print("定義されていません",label)

async def divide(message=False,reactions=False):
	#print(insts)
	if reactions:
		reaction,user = reactions
		#何か参加していたらそいつに送る
		if reaction.message.channel.id in insts:
			await insts[reaction.message.channel.id].receve_reaction(reaction,user)
	elif message:
		if message.channel.id in insts:
			await insts[message.channel.id].receve_text(message)
############################################################################################################
Intents = discord.Intents.default()
Intents.members = True
client = discord.Client(intents=Intents)

@client.event
async def on_ready():
	st = discord.Activity(name="てるてるbot",type=discord.ActivityType.listening)
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

client.run(token)
#asyncio.ensure_future(client.run(token))

############################################################################################################