from c_settings import *
from my_log import *

import time
import copy
import lang_set
import random
import discord
import asyncio
from pprint import pprint
from collections import defaultdict

#メインとなるbotのクラス
"""
送るDMにはスポイラーでチャンネルidを必ず最後につける（識別するために必要）


"""

async def bot_init(client,message,database,exit_func,dm_address):
	ans = BOT()
	await ans.init_(client,message,database,exit_func,dm_address)
	log("botを初期化")
	return ans

class BOT:
	def __init__(self):
		pass

	async def init_(self,client,message,database,exit_func,dm_address):
		self.exit_func = exit_func
		self.database = database
		self.last_run_time = time.time()
		self.imposter_check_receive = False
		self.client = client
		self.guild = message.channel.guild
		self.channel = message.channel
		self.lang = "ja"
		self.hosting = True
		self.message = {"main":None,"sub":{}}
		self.roles = {
			"teruteru":[0,"people"],
			"madmate":[0,"people"],
			"lovers":[0,"pair"],
			"spy":[0,"people"],
			"diviner":[1,"people"],
		}
		self.dm_address = dm_address
		######
		self.amu_id = "not set"
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
			"up":"⬆️",
			"down":"⬇️",
			"plus":"➕",
			"minus":"➖",
			"angel":"😇",
		}
		self.emoji_alpha = ["🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","🇮","🇯","🇰","🇱","🇲","🇳","🇴","🇵","🇶","🇷","🇸","🇹","🇺","🇻","🇼","🇽","🇾","🇿"]
		await self.init_game()

		embed = self.create_embed(BOT_TITLE,"",[])
		self.message["main"] = await self.channel.send(embed=embed)
		self.now_cursor = 0
		await self.reload_main()
		# await self.message["main"].add_reaction(self.emoji["stop"])
		await self.message["main"].add_reaction(self.emoji["up"])
		await self.message["main"].add_reaction(self.emoji["down"])
		await self.message["main"].add_reaction(self.emoji["plus"])
		await self.message["main"].add_reaction(self.emoji["minus"])
		await self.message["main"].add_reaction(self.emoji["next"])

	async def del_(self):
		await self.delete_message(main=True)

	async def on_message(self,message):
		self.last_run_time = time.time()
		if message.content.startswith(cmd_prefix+" "):
			arg = message.content.split(cmd_prefix+" ")[1].split()
			if arg[0]=="start":
				if await self.database.can_start():
					await self.start_game()
				else:
					await self.exit_func(self.channel.id)
					await self.channel.send("ただいまメンテナンス中です。\nしばらくお待ちください。")
			elif arg[0]=="settings":
				try:
					self.roles[arg[1]][0] = int(arg[2])
				except:
					pass
				finally:
					await self.reload_main()
			elif arg[0]=="exit":
				await self.exit_func(self.channel.id)
			elif arg[0]=="act-div":
				await self.diviner_action()

	async def on_reaction_add(self,reaction,user):
		self.last_run_time = time.time()
		if reaction.message.author==self.client.user and user!=self.client.user:
			if self.message["main"]==reaction.message:
				if reaction.emoji==self.emoji["play"]:
					self.hosting = True
				elif reaction.emoji==self.emoji["stop"]:
					self.hosting = False
				elif reaction.emoji==self.emoji["up"]:
					self.now_cursor = max(0,self.now_cursor-1)
				elif reaction.emoji==self.emoji["down"]:
					self.now_cursor = min(self.now_cursor+1,len(self.roles)-1)
				elif reaction.emoji==self.emoji["plus"]:
					key = list(self.roles.keys())[self.now_cursor]
					self.roles[key][0]+=1
				elif reaction.emoji==self.emoji["minus"]:
					key = list(self.roles.keys())[self.now_cursor]
					self.roles[key][0] = max(0,self.roles[key][0]-1)
				elif reaction.emoji==self.emoji["next"]:
					if await self.database.can_start():
						await self.start_game()
					else:
						await self.exit_func(self.channel.id)
						await self.channel.send("ただいまメンテナンス中です。\nしばらくお待ちください。")
						return
				await self.reload_main()
				await reaction.remove(user)
			elif self.imposter_check_receive and reaction.message==self.message["sub"]["check_imposter"]:
				asyncio.ensure_future(self.vote_check_imposter(reaction,user))
				try:
					await reaction.remove(user)
				except:
					pass
			elif reaction.message==self.message["sub"]["diviner_action"]:
				if reaction.emoji==self.emoji["play"]:
					await self.diviner_action()
					self.diviner_action_reaction = (reaction,user)
				elif reaction.emoji==self.emoji["stop"]:
					self.wait_diviner_action = set()
					try:
						r,u = self.diviner_action_reaction
						await r.remove(u)
					except:
						pass
					await reaction.remove(user)



	async def on_reaction_add_dm(self,reaction,user):
		if reaction.message.author==self.client.user:
			if reaction.message in self.dm_wating_list and reaction.emoji==self.emoji["maru"]:
				await self.role_check_wait(reaction,user)
			elif reaction.message in self.dm_list and self.find_assigned_role(user.id)=="lovers" and reaction.emoji==self.emoji["angel"]:
				pair = self.find_lovers_pair(user.id)
				await pair.send(f"恋人（{user.display_name}）が死亡しました")
			elif reaction.message in self.wait_diviner_action:
				self.wait_diviner_action.remove(reaction.message)
				ind = self.emoji_alpha.index(reaction.emoji)
				alpha = list(self.member.keys())[ind]
				member = self.member[alpha]
				if member.id in self.crewmate:
					await user.send(f"{member.display_name}はcrewmateです")
				elif member.id in self.imposter:
					await user.send(f"{member.display_name}はimposterです")
				else:
					await user.send(f"{member.display_name}は不明です")


	def find_lovers_pair(self,d_id):
		for pair in self.assigned_roles["lovers"]:
			if pair[0].id==d_id:
				return pair[1]
			elif pair[1].id==d_id:
				return pair[0]
		return None

	def find_assigned_role(self,d_id):
		for key in self.assigned_roles:
			if type(self.assigned_roles[key][0])==list:
				for tar in self.assigned_roles[key]:
					if d_id in [x.id for x in  tar]:
						return key
			elif sum([x.id==d_id for x in self.assigned_roles[key]]):
				return key
		return None

	def trans(self,word):
		return lang_set.to(self.lang,word)

	def create_embed(self,title,description,fields,color=discord.Colour.green(),inline=False):
		embed = discord.Embed(title=title,description=description,color=color)
		for name,value in fields:
			embed.add_field(name=name,value=value,inline=inline)
		return embed

	async def delete_message(self,label=False,all_=True,main=False):
		if label:
			try:
				await self.message["sub"][label].delete()
				del self.message["sub"][label]
			except Exception as e:
				print(e)
				pass
		elif all_:
			keys = copy.deepcopy(list(self.message["sub"].keys()))
			for key in keys:
				try:
					await self.message["sub"][key].delete()
					del self.message["sub"][key]
				except Exception as e:
					print(self.message["sub"].keys())
					err("DELETE_MESSAGE","メッセージの削除失敗",key)
					print(e)
		if main:
			try:
				await self.message["main"].delete()
				self.message["main"] = None
			except:
				err("DELETE_MESSAGE","メインメッセージの削除失敗")

	async def gf_member(self,d_id):
		ans = self.guild.get_member(d_id)
		if ans==None:
			ans = await self.guild.fetch_member(d_id)
		return ans

	def find_member_key(self,d_id=None,a_name=None):
		ans = None
		for td,ta in self.member:
			if td==d_id:
				return (td,ta)
		return ans


	async def reload_main(self):
		cursor = self.now_cursor
		# if self.hosting: color=discord.Colour.green(); fields=[[self.trans("state"),self.trans("**RUNNING**")]]
		# else: color=discord.Colour.red(); fields=[[self.trans("state"),self.trans("**STOPPING**")]]
		color = discord.Colour.green()
		fields = [[self.trans(key), "→ "+str(self.roles[key][0])+" "+self.trans(self.roles[key][1])] for key in self.roles]
		fields[-len(self.roles)+cursor][0] = fields[-len(self.roles)+cursor][0]+" ◀"
		fields.extend([
			#["game_mode",self.mode],
			#["amu",self.amu_id],
			#["開発","[hageron1229/teruteru-bot](https://github.com/hageron1229/teruteru-bot)"],
		])
		embed=self.create_embed(BOT_TITLE,"",fields,color)
		embed.set_thumbnail(url=IMAGE["main_icon"])
		await self.message["main"].edit(embed=embed)
		#await self.message["main"].clear_reactions()
		# 自分でスタートするからstate stoppingはとりあえずいらない
		# if self.hosting: await self.message["main"].add_reaction(self.emoji["stop"])
		# else: await self.message["main"].add_reaction(self.emoji["play"])

	async def change_name(self,nick="???"):
		return
		async for m in self.guild.fetch_members():
			member = await self.gf_member(m.id)
			if member.status!="online":
				continue
			self.changed_name.append([member,member.display_name])
			try:
				await member.edit(nick=nick)
			except:
				pass

	async def return_name(self):
		for m, nick in self.changed_name:
			try:
				await m.edit(nick=nick)
			except:
				pass
		self.changed_name = []

	async def init_game(self):
		#(d_id,a_name)
		self.member = {}
		self.imposter = {}
		self.crewmate = {}
		self.changed_name = []
		self.assigned_roles = defaultdict(list)
		self.night_count = 0
		self.dm_wating_list = set()
		self.dm_list = set()

	async def check_imposter(self):
		await self.change_name()
		#imposterの人を探す
		embed = discord.Embed(title=f'[{self.trans("Imposter Check")}]',description=self.trans("Select 〇 if you are an imposter; select ✕ if you are a crewmate"),color=discord.Colour.orange())
		embed.set_image(url=IMAGE["imposter"])
		embed.add_field(name=self.trans("voted"),value=f"0 {self.trans('people')}")
		r = await self.channel.send(embed=embed)
		self.imposter_check_receive = True
		await r.add_reaction(self.emoji["maru"])
		await r.add_reaction(self.emoji["batsu"])
		await r.add_reaction(self.emoji["stop"])
		self.message["sub"]["check_imposter"] = r

	async def vote_check_imposter(self,reaction,user):
		if self.imposter_check_receive:
			before_num = len(self.member)
			if reaction.emoji==self.emoji["maru"] or reaction.emoji==self.emoji["batsu"]:
				if user.id not in self.member:
					self.member[user.id] = user
				if reaction.emoji==self.emoji["maru"]:
					if user.id in self.crewmate:
						del self.crewmate[user.id]
					self.imposter[user.id] = user
				elif reaction.emoji==self.emoji["batsu"]:
					if user.id in self.imposter:
						del self.imposter[user.id]
					self.crewmate[user.id] = user
				if before_num<len(self.member):
					embed = self.message["sub"]["check_imposter"].embeds[0]
					embed.set_field_at(0,name=self.trans("voted"),value=str(len(self.member))+" "+self.trans("people"))
					await self.message["sub"]["check_imposter"].edit(embed=embed)
			elif reaction.emoji==self.emoji["stop"]:
				self.imposter_check_receive = False
				await self.delete_message("check_imposter")
				await self.choose_roles()

	async def start_game(self):
		await self.init_game()

		await self.delete_message()

		await self.check_imposter()

	async def choose_roles(self):
		asyncio.ensure_future(self.return_name())

		#プレイ可能か人数をチェック
		need_crew = sum([self.roles[i][0] for i in ["teruteru","madmate","spy","diviner"]])
		need_member = self.roles["lovers"][0]*2
		if need_crew>len(self.crewmate) or need_member>len(self.member):
			mes = "The number of participants is too small for the role."
			await self.channel.send(self.trans(mes))
			return

		self.role_check_list = set()
		self.stock = copy.deepcopy(list(self.member.keys()))
		self.stock_crewmate = copy.deepcopy(list(self.crewmate.keys()))
		self.stock_imposter = copy.deepcopy(list(self.imposter.keys()))

		tasks = []

		if self.roles["lovers"][0]:
			pair = self.roles["lovers"][0]
			for i in range(pair):
				#lovers = [self.member[k] for k in random.sample(self.stock,2)]
				lovers = [self.member[k] for k in random.sample(self.stock,2)]
				message = ["Lovey-dovey❤"]
				tasks.append(self.role_check(lovers[0],f"{self.trans('lovers')}: {lovers[1].display_name}\n"+self.trans(random.choice(message)),IMAGE["lovers"],add_emoji=["angel"]))
				tasks.append(self.role_check(lovers[1],f"{self.trans('lovers')}: {lovers[0].display_name}\n"+self.trans(random.choice(message)),IMAGE["lovers"],add_emoji=["angel"]))
				self.assigned_roles["lovers"].append(lovers)
				await self.delete_from_stock(lovers[0])
				await self.delete_from_stock(lovers[1])

		one_person_role = [
			["teruteru",["Let's outsmart everyone!"],		self.stock_crewmate,IMAGE["teruteru"]],
			["madmate",	["Let's find the imposter."],		self.stock_crewmate,IMAGE["madmate"]],
			["spy",		["Let's cooperate with imposter."],	self.stock_crewmate,IMAGE["spy"]],
			["diviner",	["Let's fortunate."],				self.stock_crewmate,IMAGE["diviner"]],
		]
		for role_name,message,target,image in one_person_role:
			if self.roles[role_name][0]:
				add_message = ""
				if role_name=="spy":
					add_message = "\nimposter\n→ "+"\n→ ".join([self.imposter[key].display_name for key in self.imposter])
				num = self.roles[role_name][0]
				for i in range(num):
					try:
						tar = self.member[random.sample(target,1)[0]]
					except Exception as e:
						print(e)
						await self.channel.send("人数が不足しています。\nもう一度試してください。")
						return
					tasks.append(self.role_check(tar,f"{self.trans(role_name)}: {self.trans('You')}\n"+self.trans(random.choice(message))+add_message,image))
					self.assigned_roles[role_name].append(tar)
					await self.delete_from_stock(tar)
		await asyncio.gather(*tasks)



	async def delete_from_stock(self,member):
		def in_check(arr,value):
			if value in arr:
				return arr.index(value)
			else:
				return -1

		def delete_if_in(arr,value):
			t = in_check(arr,value)
			if t!=-1:
				del arr[t]
				return True
			else:
				return False

		delete_if_in(self.stock,member.id)
		delete_if_in(self.stock_crewmate,member.id)
		delete_if_in(self.stock_imposter,member.id)

	async def role_check(self,member,message,image,add_emoji=[]):
		embed = discord.Embed(title=self.trans("ROLE"),description=message)
		embed.set_thumbnail(url=image)
		r = await member.send(embed=self.add_dm_footer(embed))
		self.dm_address[r.id] = self.channel.id
		self.dm_wating_list.add(r)
		await r.add_reaction(self.emoji["maru"])
		for e in add_emoji:
			await r.add_reaction(self.emoji[e])

	def add_dm_footer(self,embed):
		return embed
		embed.add_field(name="id", value=f"||{t_to_n(self.channel.id)}||")
		#embed.set_footer(text=f"||{self.channel.id}||")
		return embed

	async def role_check_wait(self,reaction,user):
		if len(self.dm_wating_list)==0:
			return
		if reaction.message in self.dm_wating_list:
			self.dm_wating_list.remove(reaction.message)
			self.dm_list.add(reaction.message)
		if len(self.dm_wating_list)==0:
			await self.role_check_comp()

	async def role_check_comp(self):
		comp = "Role confirmation complete."
		start = "GAME START!!"
		self.message["sub"]["confirm_roles"] = await self.channel.send(self.trans(comp)+"\n"+self.trans(start))

		#diviner
		if self.assigned_roles["diviner"]!=[]:
			embed = self.create_embed("占い師のアクション","占い師が行動するタイミングでボタンを押してください",[],discord.Colour.red())
			embed.set_thumbnail(url= IMAGE["diviner"])
			self.message["sub"]["diviner_action"] = await self.channel.send(embed=embed)
			await self.message["sub"]["diviner_action"].add_reaction(self.emoji["play"])
			await self.message["sub"]["diviner_action"].add_reaction(self.emoji["stop"])

	async def diviner_action(self):
		tars = self.assigned_roles["diviner"]
		self.wait_diviner_action = set()
		description = ""
		i = 0
		for key in self.member:
			description += f"{self.emoji_alpha[i]} : {self.member[key].display_name}\n"
			i+=1
		fields = []
		embed = self.create_embed("占い師のアクション",description,fields,discord.Colour.orange(),True)
		for member in tars:
			r = await member.send(embed=self.add_dm_footer(embed))
			self.dm_address[r.id] = self.channel.id
			self.wait_diviner_action.add(r)
			for j in range(i):
				await r.add_reaction(self.emoji_alpha[j])
