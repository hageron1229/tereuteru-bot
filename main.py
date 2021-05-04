# 追加役職
# てるてる、狂人、恋人、スパイ
# teruteru,madmate,lovers,spy,diviner

with open("discord_token.txt",mode="r") as f:
	token = f.read()
bot_status = "AmongUs拡張bot"
cmd = ".ab"


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
	await t.init_()
	return t

class Among_us:
	def __init__(self,channel,client,boo=False):
		if boo==False:
			raise Exception("直接の初期化は禁止されています")
		self.channel = channel
		self.client = client
		self.message_main = -1
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
		self.game_setting = {
			"teruteru":[0,"人"],
			"madmate":[0,"人"],
			"lovers":[0,"組"],
			"spy":[0,"人"],
			"diviner":[2,"人"],
		}
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

	def create_embed(self,title,description,fields,color=discord.Colour.green(),inline=False):
		embed = discord.Embed(title=title,description=description,color=color)
		for name,value in fields:
			embed.add_field(name=name,value=value,inline=inline)
		return embed

	async def init_(self):
		await self.game_init()
		fields = [["state","**RUNNING**"]]
		fields.extend([[key, str(self.game_setting[key][0])+" "+str(self.game_setting[key][1])] for key in self.game_setting])
		fields.extend([
			#["game_mode",self.mode],
			["amu",self.amu_id],
			["開発","[hageron1229/teruteru-bot](https://github.com/hageron1229/teruteru-bot)"],
		])
		embed = self.create_embed("拡張Among Us","",fields)
		self.message_main = await self.channel.send(embed=embed)
		await self.message_main.add_reaction(self.emoji["stop"])

	async def reload_main(self):
		if self.hosting: color=discord.Colour.green(); fields=[["state","**RUNNING**"]]
		else: color=discord.Colour.red(); fields=[["state","**STOPPING**"]]
		fields.extend([[key, str(self.game_setting[key][0])+" "+str(self.game_setting[key][1])] for key in self.game_setting])
		fields.extend([
			#["game_mode",self.mode],
			["amu",self.amu_id],
			["開発","[hageron1229/teruteru-bot](https://github.com/hageron1229/teruteru-bot)"],
		])
		await self.message_main.edit(embed=self.create_embed("拡張Among Us","",fields,color))
		await self.message_main.clear_reactions()
		if self.hosting: await self.message_main.add_reaction(self.emoji["stop"])
		else: await self.message_main.add_reaction(self.emoji["play"])

	async def del_(self):
		await self.message_main.delete()
		await self.delete_message_all()
		print("delete instance",self.channel.id)

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
			elif com[0]=="settings":
				try:
					self.game_setting[com[1]][0] = int(com[2])
				except:
					pass
				finally:
					await self.reload_main()
			elif com[0]=="send_all":
				await self.channel.send_all()
			elif com[0]=="test":
				await self.test()
			elif com[0]=="random":
				await self.random_check()
			elif com[0]=="status" and len(com)==2:
				if com[1]=="end":
					for key in list(copy.copy(self.message.keys())):
						await self.delete_message(key)
			elif com[0]=="unmuteall":
				await self.unmute()
			elif com[0]=="func":
				print("self."+com[1]+"()")
				#await exec("self."+com[1]+"()")
				await eval(com[1])
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
				print(user.display_name,reaction.emoji)
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
					await self.game_started()
				# elif "unmute" in self.message and self.message["unmute"].id==reaction.message.id and reaction.emoji==self.emoji["next"]:
				# 	await self.unmute(tar="all")
				# 	await reaction.remove(user)

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
		tar = mes.embeds[0].to_dict()
		await self.change_status(status,False)

	async def unmute(self,tar="all"):
		if tar=="all":
			for data in self.member:
				mem = await self.gf_member(data["d_id"])
				try:
					#ボイスチャンネルに入っていない場合エラーになる
					await mem.edit(mute=False,deafen=False)
				except:
					pass

	async def set_mode(self,mode):
		kouho = ["bad1","bad2"]
		if mode in kouho:
			self.mode = mode
			await self.channel.send("MODE : "+self.mode)
		else:
			#await self.channel.send(f"MODE[{mode}]は定義されていません")
			pass

	async def find_member(self,d_id=None,a_name=None):
		ans = None
		if d_id:
			for m in self.member:
				if m["d_id"]==d_id:
					ans = m
					break
		elif a_name:
			for m in self.member:
				if m["a_name"]==a_name:
					ans = m
					break
		if ans==None:
			return False
		else:
			return ans

	async def change_status(self,s,stop=False):
		if self.hosting==False:
			return
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

		await self.set_member()
		new_member = self.member

		async def role_do_check():
			#てるてるがつられたら終了
			if b_status==a_status and b_status=="DISCUSSION":
				for a_member in new_member:
					b_member = {"d_id":0,"alive":False}
					for m in self.old_member:
						if m["d_id"]==a_member["d_id"]:
							b_member = m
							break
					if b_member["alive"]==True and a_member["alive"]==False:
						if sum([teru["d_id"]==a_member["d_id"] for teru in self.role["teruteru"]]):
							print("てるてる",a_member["a_name"],"がつられた")
							await asyncio.sleep(8)
							await self.channel.send(f'{a_member["a_name"]}はてるてるだったため、ゲーム終了！')
							return
						else:
							print(a_member["a_name"],"はてるてるじゃなかった、、、")
			if b_status=="TASKS" and a_status=="DISCUSSION":
				if self.night_count>0:
					print("占い師が占えるタイム",self.night_count)
					asyncio.ensure_future(self.diviner_action())
				else:
					print("初夜は占いできない")
				self.night_count += 1
			if a_status!="DISCUSSION":
				self.can_diviner_action = False

		await role_do_check()

		self.status = a_status
		self.old_member = copy.deepcopy(self.member)
		await self.set_member()

	async def gf_member(self,d_id):
		ans = self.channel.guild.get_member(d_id)
		if ans==None:
			ans = await self.channel.guild.fetch_member(d_id)
		return ans

	async def diviner_action(self):
		self.can_diviner_action = True
		async def diviner_action_reply(tars):
			global global_dm
			while tars and self.can_diviner_action:
				await asyncio.sleep(2)
				print(tars)
				remove_list = []
				for tar,mes in tars:
					for d_id,emoji in copy.deepcopy(global_dm):
						print(d_id,tar["d_id"])
						print(emoji,"au" in str(emoji))
						if tar["d_id"]==d_id and "au" in str(emoji):
							print(emoji)
							remove_list.append([(d_id,emoji),[tar,mes]])
							broke = False
							for member in self.member:
								if member["color"] in str(emoji):
									broke = True
									break
							if broke==False:
								print("プレイヤーが見つかりません")
							else:
								m = await self.gf_member(d_id)
								if member in self.crewmate:
									await m.send(f'{member["a_name"]}は「crewmate」です')
								elif member in self.imposter:
									await m.send(f'{member["a_name"]}は「imposter」です')
								else:
									await m.send(f'{member["a_name"]}は「不明」です')
								await mes.delete()
				for r in remove_list:
					global_dm.remove(r[0])
					del tars[tars.index(r[1])]
			for tar,mes in tars:
				await mes.delete()



		#s_embed = discord.Embed(title=f"占い師のアクション",description="crewmate?imposter?",color=discord.Colour.orange())
		fields = []
		alive_mate = []

		mes = await self.channel.fetch_message(self.amu_id)
		tar = mes.embeds[0].to_dict()["fields"]
		for item in tar:
			if item["value"].startswith("<:au"):
				fields.append([item["name"],item["value"]])
				#s_embed.add_field(name=item["name"],value=item["value"],inline=True)
				if "dead" not in item["value"]:
					alive_mate.append(f'<{item["value"].split("<")[1].split(">")[0]}>')

		tars = copy.deepcopy(self.role["diviner"])
		global_dm = set()
		info = []

		embed = self.create_embed("占い師のアクション","Crewmate? Imposter?",fields,discord.Colour.orange(),True)

		for tar in tars:
			member = await self.gf_member(tar["d_id"])
			r = await member.send(embed=embed)
			info.append([tar,r])
			for em in alive_mate:
				await r.add_reaction(em)
		asyncio.ensure_future(diviner_action_reply(info))


	async def set_amu(self,s):
		try:
			amu_id = int(s)
			mes = await self.channel.fetch_message(amu_id)
			self.amu_id = amu_id
			await self.reload_main()
			await self.change_status(mes.embeds[0].title)
		except Exception as e:
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

	# async def random_one(self,kouho):
	# 	ind = int(random.random()*(10**10)+time.time()+random.randint(0,len(kouho)-1))%len(kouho)
	# 	return kouho[ind]

	# async def bad_random_choice(self,kouho,add=""):
	# 	# ind = int(random.random()*(10**10)+time.time())%len(kouho)
	# 	# bad_data = kouho[ind]
	# 	bad_data = await self.random_one(kouho)
	# 	bad = await self.client.fetch_user(bad_data["d_id"])
	# 	self.bad_target = bad_data
	# 	#print(self.game_word+" :",bad_data["a_name"])
	# 	print(self.game_word+" :",'##非公開##')

	# 	self.message["dm"] = await bad.send("あなたが"+self.game_word+"に選ばれました"+add)

	# 	#s = self.game_word+"：||{} ({}){}||\n".format(bad_data["a_name"],self.channel.guild.get_member(bad_data["d_id"]).mention,"　"*(random.randint(10,25)))
	# 	s = "||{} ({}){}||\n".format(bad_data["a_name"],self.channel.guild.get_member(bad_data["d_id"]).mention,"　"*(random.randint(10,25)))
	# 	embed = discord.Embed(title="このゲームの"+self.game_word,description=s,color=discord.Colour.dark_gold())
	# 	embed.set_thumbnail(url="https://illustcute.com/photo/dl/4659.png?20200805")
	# 	self.message["this_game_bad"] = await self.channel.send(embed=embed)
	# 	s = self.game_word+"に選ばれた人は〇を押してください！"
	# 	self.message["syodaku"] = await self.channel.send(s)
	# 	await self.message["syodaku"].add_reaction(self.emoji["maru"])

	# 	return bad

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

	# async def send_all(self):
	# 	res = await self.set_member()

	# 	body = "### これはテストです ###\n"
	# 	body += f"あなたは「{self.game_word}」に選ばれました\n"
	# 	body += "### 以上 ###"
	# 	for bad_data in self.member:
	# 		bad = await self.client.fetch_user(bad_data["d_id"])
	# 		print(self.game_word+" :",bad_data["a_name"])
	# 		self.dm_message_test = await bad.send(body)

	async def delete_message_all(self):
		keys = copy.deepcopy(list(self.message.keys()))
		for key in keys:
			await self.delete_message(key)

	async def delete_message(self,label):
		boo = False
		if label not in self.message:
			#print(f"LABEL[{label}]はself.messageに定義されていません")
			pass
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
				member = await self.channel.guild.fetch_member(i)
			o_nick = member.nick
			try:
				await member.edit(nick=nick)
				self.changed.append([member,o_nick])
			except:
				#print("ERROR",member.display_name)
				pass
		print("changed name")
		return self.changed

	async def return_name(self):
		for member,nick in self.changed:
			await member.edit(nick=nick)
		self.changed = []
		#print("returned name")

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
					#print(f"ERROR : {item['name']}が未連携です")
					#return -2
					continue
				t["d_id"] = int(item["value"].split("<@!")[1][:-1])
				t["alive"] = "dead" not in item["value"]
				if t["alive"]:
					t["color"] = item["value"].split("<:au")[1].split(":")[0]
				else:
					t["color"] = item["value"].split("<:au")[1].split("dead:")[0]
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
		self.turareted = False
		self.bad_target = []
		self.old_member = []
		self.role = defaultdict(list)
		self.night_count = 0
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
		# keys = copy.copy(list(self.message.keys()))
		# for key in keys:
		# 	await self.delete_message(key)
		#代用
		await self.delete_message_all()

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
		await self.delete_message("imposter_check")
		await self.return_name()

		#狂人をランダムでひとり選んでメッセージを送信する
		#await self.bad_random_choice(self.crewmate)

		#ver2.0
		await self.choose_roles()

	async def add_blank(self):
		return "."*random.randint(20,35)

	async def choose_roles(self):
		print("choose_roles")
		self.stock = copy.deepcopy(self.member)
		self.stock_crewmate = copy.deepcopy(self.crewmate)
		self.stock_imposter = copy.deepcopy(self.imposter)
		self.all_roles = ""
		if self.game_setting["lovers"][0]:
			pair = self.game_setting["lovers"][0]
			for i in range(pair):
				lovers = random.sample(self.stock,2)
				love_message = ["ラブラブですね","アツアツですね","おふたりは倦怠期です","おふたりの結婚式は来週です","相手は昨日浮気をしました"]
				await self.role_check(lovers[0],f"あなたは「{lovers[1]['a_name']}」と恋人です❤\n"+random.choice(love_message))
				await self.role_check(lovers[1],f"あなたは「{lovers[0]['a_name']}」と恋人です❤\n"+random.choice(love_message))
				self.all_roles += f'恋人：||{lovers[0]["a_name"]}❤{lovers[1]["a_name"]}{await self.add_blank()}||\n'
				self.role["lovers"].append([lovers])
				await self.delete_from_stock(lovers[0])
				await self.delete_from_stock(lovers[1])

		if self.game_setting["teruteru"][0]:
			num = self.game_setting["teruteru"][0]
			for i in range(num):
				teruteru = random.sample(self.stock_crewmate,1)[0]
				teruteru_message = ["みんなを出し抜きましょう"]
				await self.role_check(teruteru,f"あなたは「てるてる」に選ばれました\n"+random.choice(teruteru_message))
				self.all_roles += f'てるてる：||{teruteru["a_name"]}{await self.add_blank()}||\n'
				self.role["teruteru"].append(teruteru)
				await self.delete_from_stock(teruteru)

		if self.game_setting["madmate"][0]:
			num = self.game_setting["madmate"][0]
			for i in range(num):
				tar = random.sample(self.stock_crewmate,1)[0]
				message = ["imposterを探し出そう"]
				await self.role_check(tar,f"あなたは「狂人(madmate)」に選ばれました\n"+random.choice(message))
				self.all_roles += f'狂人：||{tar["a_name"]}{await self.add_blank()}||\n'
				self.role["madmate"].append(tar)
				await self.delete_from_stock(tar)

		if self.game_setting["spy"][0]:
			num = self.game_setting["spy"][0]
			for i in range(num):
				tar = random.sample(self.stock_crewmate,1)[0]
				message = ["imposterに協力しましょう"]
				notify = "imposterは、"+"、".join([j["a_name"] for j in self.imposter])
				await self.role_check(tar,f"あなたは「スパイ」に選ばれました\n"+notify+"です\n"+random.choice(message))
				self.all_roles += f'スパイ：||{tar["a_name"]}{await self.add_blank()}||\n'
				self.role["spy"].append(tar)
				await self.delete_from_stock(tar)

		if self.game_setting["diviner"][0]:
			num = self.game_setting["diviner"][0]
			for i in range(num):
				tar = random.sample(self.stock_crewmate,1)[0]
				message = ["気になる人を占おう"]
				await self.role_check(tar,f"あなたは「占い師」に選ばれました\n"+random.choice(message))
				self.all_roles += f'占い師：||{tar["a_name"]}{await self.add_blank()}||\n'
				self.role["diviner"].append(tar)
				await self.delete_from_stock(tar)

		self.message["all_roles_message"] = await self.channel.send(f"このゲームの全ての役職\n{self.all_roles}")
		self.message["game_start"] = await self.channel.send("**ゲームスタート！**")

	async def role_check(self,tar,message):
		global global_dm

		member = self.channel.guild.get_member(tar["d_id"])
		if member==None:
			member = await self.channel.guild.fetch_message(tar["d_id"])

		#dm
		self.role_check_dm = await member.send(message)
		await self.role_check_dm.add_reaction(self.emoji["maru"])

		while 1:
			await asyncio.sleep(1)
			tar = (member.id,self.emoji["maru"])
			if tar in global_dm:
				global_dm.remove(tar)
				break
			else:
				print("waiting...")
		return

	async def delete_from_stock(self,tar):
		print(self.stock)
		print(tar)
		for i in range(len(self.stock)):
			if self.stock[i]["a_name"]==tar["a_name"]:
				del self.stock[i]
				break
		for i in range(len(self.stock_crewmate)):
			if self.stock_crewmate[i]["a_name"]==tar["a_name"]:
				del self.stock_crewmate[i]
				break
		for i in range(len(self.stock_imposter)):
			if self.stock_imposter[i]["a_name"]==tar["a_name"]:
				del self.stock_imposter[i]
				break


	# async def game_bad2(self):
	# 	caution = "\nもしあなたがimposterだった場合、狂人は無しです"
	# 	await self.bad_random_choice(self.member,add=caution)

	async def game_started(self):
		#ニックネームを戻す
		print("return name")
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
		else:
			global global_dm
			global_dm.add((user.id,str(reaction.emoji)))
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

global_dm = set()

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