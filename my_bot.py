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

async def bot_init(client,message):
	ans = BOT()
	await ans.init_(client,message)
	log("botを初期化")
	return ans

class BOT:
	def __init__(self):
		pass

	async def init_(self,client,message):
		self.last_run_time = time.time()
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
		}
		await self.init_game()

		#メインメッセージの設定
		fields = [[self.trans("state"),self.trans("**RUNNING**")]]+[[self.trans(key), str(self.roles[key][0])+" "+self.trans(self.roles[key][1])] for key in self.roles]
		fields.extend([
			#["game_mode",self.mode],
			#["amu",self.amu_id],
			#["開発","[hageron1229/teruteru-bot](https://github.com/hageron1229/teruteru-bot)"],
		])
		embed = self.create_embed(BOT_TITLE,"",fields)
		self.message["main"] = await self.channel.send(embed=embed)
		await self.message["main"].add_reaction(self.emoji["stop"])

	async def del_(self):
		pass

	async def on_message(self,message):
		self.last_run_time = time.time()
		if message.content.startswith(cmd_prefix+" "):
			arg = message.content.split(cmd_prefix+" ")[1].split()
			if arg[0]=="start":
				await self.start_game()
			elif arg[0]=="settings":
				try:
					self.roles[arg[1]][0] = int(arg[2])
				except:
					pass
				finally:
					await self.reload_main()

	async def on_reaction_add(self,reaction,user):
		self.last_run_time = time.time()
		if reaction.message.author==self.client.user:
			if self.message["main"]==reaction.message:
				if reaction.emoji==self.emoji["play"]:
					self.hosting = True
				elif reaction.emoji==self.emoji["stop"]:
					self.hosting = False
				await self.reload_main()
			elif self.imposter_check_receive:
				asyncio.ensure_future(self.vote_check_imposter(reaction,user))
				try:
					await reaction.remove(user)
				except:
					pass

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
				del self.message["sub"][key]
			except:
				pass
		elif all_:
			keys = copy.deepcopy(list(self.message["sub"].keys()))
			for key in keys:
				try:
					await self.message["sub"][key].delete()
					del self.message["sub"][key]
				except:
					err("DELETE_MESSAGE","メッセージの削除失敗",key)
		if main:
			try:
				await self.message["main"].delete()
				self.message["main"] = None
			except:
				err("DELETE_MESSAGE","メインメッセージの削除失敗")

	async def gf_member(self,d_id):
		ans = self.guild.get_member(d_id)
		if ans==None:
			ans = self.guild.fetch_member(d_id)
		return ans

	def find_member_key(self,d_id=None,a_name=None):
		ans = None
		for td,ta in self.member:
			if td==d_id:
				return (td,ta)
		return ans


	async def reload_main(self):
		if self.hosting: color=discord.Colour.green(); fields=[[self.trans("state"),self.trans("**RUNNING**")]]
		else: color=discord.Colour.red(); fields=[[self.trans("state"),self.trans("**STOPPING**")]]
		fields.extend([[self.trans(key), str(self.roles[key][0])+" "+self.trans(self.roles[key][1])] for key in self.roles])
		fields.extend([
			#["game_mode",self.mode],
			#["amu",self.amu_id],
			#["開発","[hageron1229/teruteru-bot](https://github.com/hageron1229/teruteru-bot)"],
		])
		await self.message["main"].edit(embed=self.create_embed(BOT_TITLE,"",fields,color))
		await self.message["main"].clear_reactions()
		if self.hosting: await self.message["main"].add_reaction(self.emoji["stop"])
		else: await self.message["main"].add_reaction(self.emoji["play"])

	async def change_name(self,nick="???"):
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
		self.dm_wating_list = []

	async def check_imposter(self):
		await self.change_name()
		#imposterの人を探す
		embed = discord.Embed(title=f'[{self.trans("Imposter Check")}]',description=self.trans("Select 〇 if you are an imposter; select ✕ if you are a crewmate"),color=discord.Colour.orange())
		embed.set_image(url="http://drive.google.com/uc?export=view&id=114-NfgzzHkZjzwV_-759VfQp_8KfAEO7")
		embed.add_field(name=self.trans("voted"),value=f"0 {self.trans('people')}")
		r = await self.channel.send(embed=embed)
		self.imposter_check_receive = True
		await r.add_reaction(self.emoji["maru"])
		await r.add_reaction(self.emoji["batsu"])
		await r.add_reaction(self.emoji["stop"])
		self.message["sub"]["check_imposter"] = r

	async def vote_check_imposter(self,reaction,user):
		if self.imposter_check_receive and reaction.message==self.message["sub"]["check_imposter"]:
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
		self.stock = copy.deepcopy(list(self.member.keys()))
		self.stock_crewmate = copy.deepcopy(list(self.crewmate.keys()))
		self.stock_imposter = copy.deepcopy(list(self.imposter.keys()))
		if self.roles["lovers"][0]:
			pair = self.roles["lovers"][0]
			for i in range(pair):
				lovers = [self.member[k] for k in random.sample(self.stock,2)]
				message = ["Lovey-dovey❤"]
				asyncio.ensure_future(self.role_check(lovers[0],f"{self.trans('lovers')}: {lovers[1]['a_name']}\n"+self.trans(random.choice(message))))
				asyncio.ensure_future(self.role_check(lovers[1],f"{self.trans('lovers')}: {lovers[0]['a_name']}\n"+self.trans(random.choice(message))))
				self.assigned_roles["lovers"].append(lovers)
				await self.delete_from_stock(lovers[0])
				await self.delete_from_stock(lovers[1])

		if self.roles["teruteru"][0]:
			num = self.roles["teruteru"][0]
			for i in range(num):
				tar = self.member[random.sample(self.stock_crewmate,1)[0]]
				message = ["Let's outsmart everyone."]
				asyncio.ensure_future(self.role_check(tar,f"{self.trans('teruteru')}: {self.trans('You')}\n"+self.trans(random.choice(message))))
				self.assigned_roles["teruteru"].append(tar)
				await self.delete_from_stock(tar)

		if self.roles["madmate"][0]:
			num = self.roles["madmate"][0]
			for i in range(num):
				tar = self.member[random.sample(self.stock_crewmate,1)[0]]
				message = ["Let's find the imposter."]
				asyncio.ensure_future(self.role_check(tar,f"{self.trans('madmate')}: {self.trans('You')}\n"+self.trans(random.choice(message))))
				self.assigned_roles["madmate"].append(tar)
				await self.delete_from_stock(tar)

		if self.roles["spy"][0]:
			num = self.roles["spy"][0]
			for i in range(num):
				tar = self.member[random.sample(self.stock_crewmate,1)[0]]
				message = ["Let's cooperate with imposter."]
				asyncio.ensure_future(self.role_check(tar,f"{self.trans('spy')}: {self.trans('You')}\n"+self.trans(random.choice(message))))
				self.assigned_roles["spy"].append(tar)
				await self.delete_from_stock(tar)

		if self.roles["diviner"][0]:
			num = self.roles["diviner"][0]
			for i in range(num):
				tar = self.member[random.sample(self.stock_crewmate,1)[0]]
				message = ["Let's fortunate."]
				asyncio.ensure_future(self.role_check(tar,f"{self.trans('diviner')}: {self.trans('You')}\n"+self.trans(random.choice(message))))
				self.assigned_roles["diviner"].append(tar)
				await self.delete_from_stock(tar)

	async def delete_from_stock(self,member):
		try:
			del self.stock[member]
		except:
			pass
		try:
			del self.stock_crewmate[member]
		except:
			pass
		try:
			del self.stock_imposter[member]
		except:
			pass

	async def role_check(self,member,message):
		r = await member.send(message)
		self.dm_wating_list.append(r)
		await r.add_reaction(self.emoji["maru"])