from my_log import *

class DB:
	def __init__(self):
		log("DBに接続")

	def register(self,guild_id,activation_code):
		log("DB",f"{activation_code}を{guild_id}に登録")

	def unregister(self,guild_id,activation_code):
		log("DB",f"{activation_code}を{guild_id}から解除")

	def can_play(self,guild_id):
		log("DB",f"{guild_id}が利用可能かcheck")