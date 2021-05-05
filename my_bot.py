from c_settings import *
from my_log import *

import copy
import random
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
		self.client = client
		self.guild = message.channel.guild
		self.channel = message.channel
		self.lang = "ja"

	async def on_message(self,message):
		pass

	async def on_reaction_add(self,reaction,user):
		pass
