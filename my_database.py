from my_log import *

import time
import sqlite3 as sq
from pprint import pprint
import string
import random

class DB:
	def __init__(self):
		dbname = "bot.db"
		self.conn = sq.connect(dbname)
		log("DBに接続")

		#activationテーブルの存在確認
		table = "activation"
		cmd = f"CREATE TABLE IF NOT EXISTS {table}(code STRING PRIMARY KEY, guild_id INTEGER, unix_time INTEGER)"
		self.exe(cmd)
		self.show()

		#未アクティベーションコード保存リスト
		table = "unactivation"
		cmd = f"CREATE TABLE IF NOT EXISTS {table}(code STRING PRIMARY KEY, valid_time INTEGER)"
		self.exe(cmd)

		#メンテ
		table = "info"
		cmd = f"CREATE TABLE IF NOT EXISTS {table}(key STRING PRIMARY KEY, value STRING)"
		self.exe(cmd)
		cmd = f"INSERT into info values('maintenance','yes')"
		try:
			self.exe(cmd)
		except Exception as e:
			print(e)


	def __del__(self):
		self.conn.close()

	def exe(self,cmd):
		cur = self.conn.cursor()
		cur.execute(cmd)
		self.conn.commit()

	def show(self,table="activation"):
		cur = self.conn.cursor()
		cur.execute(f"SELECT * FROM {table}")
		pprint(cur.fetchall())
		cur.close()

	def register(self,guild_id,activation_code):
		#未登録アクティベーションコードリストにあるかチェック
		cmd = f"SELECT * from unactivation where code='{activation_code}'"
		cur = self.conn.cursor()
		cur.execute(cmd)
		ans = cur.fetchall()
		if len(ans)==0:
			#actリストにない
			cmd = f"SELECT * from activation where code='{activation_code}' and guild_id=0"
			cur.execute(cmd)
			ans = cur.fetchall()
			if len(ans)!=0:
				#登録待ち
				cmd = f"UPDATE activation set guild_id={guild_id} where code='{activation_code}'"
				cur.execute(cmd)
				boo = True
				log("DB",f"新しいサーバーに変更")
			else:
				#多重登録
				boo = False
				log("DB",f"多重登録：{activation_code},{guild_id}")
		else:
			#リストにある

			#activationに追加
			cmd = f"INSERT into activation values('{activation_code}',{guild_id},{ans[0][1]+int(time.time())})"
			cur.execute(cmd)

			#activation codeを削除する
			cmd = f"DELETE from unactivation where code='{activation_code}'"
			cur.execute(cmd)
			boo = True
			log("DB",f"{activation_code}を{guild_id}に登録しました")
		cur.close()
		self.conn.commit()
		return boo

	def unregister(self,guild_id,activation_code):
		cur = self.conn.cursor()
		cmd = f"SELECT * from activation where code='{activation_code}' and guild_id={guild_id}"
		cur.execute(cmd)
		ans = cur.fetchall()
		if len(ans)==0:
			#ないよ
			log("DB",f"登録解除失敗")
			boo = False
		else:
			cmd = f"UPDATE activation set guild_id=0 where code='{activation_code}'"
			cur.execute(cmd)
			boo = True
			log("DB",f"{activation_code}を{guild_id}から解除")
		cur.close()
		self.conn.commit()
		return boo

	def can_play(self,guild_id):
		cur = self.conn.cursor()
		cmd = f"SELECT * from activation where guild_id='{guild_id}'"
		cur.execute(cmd)
		ans = cur.fetchall()
		if len(ans)==0:
			log("CAN_PLAY","無理")
			boo = False
		else:
			log("CAN_PLAY","プレイ可能")
			boo = True
		cur.close()
		return boo

	async def can_start(self):
		cmd = f"SELECT * from info where key='maintenance'"
		cur = self.conn.cursor()
		cur.execute(cmd)
		ans = cur.fetchall()
		if ans[0][1]=="no":
			return True
		else:
			return False

	async def set_maintenance(self,boo):
		if boo:
			cmd = 'update info set value="yes" where key="maintenance"'
		else:
			cmd = 'update info set value="no" where key="maintenance"'
		self.exe(cmd)

	async def create_activation_code(self,valid_time):
		if valid_time=="hour":
			during = 60*60
		elif valid_time=="day":
			during = 60*60*24
		elif valid_time=="week":
			during = 60*60*24*7
		elif valid_time=="month":
			during = 60*60*24*7*30
		elif valid_time=="year":
			during = 60*60*24*7*30*12
		elif valid_time=="unlimited":
			during = 60*60*24*7*30*12*100
		else:
			return "書式が間違っています"
		def issue():
			n = 10
			res = [random.choice(string.ascii_letters+string.digits) for i in range(n)]
			return "".join(res)
		while 1:
			code = issue()
			cur = self.conn.cursor()
			cmd = f"SELECT * from unactivation where code='{code}'"
			cur.execute(cmd)
			ans1 = cur.fetchall()
			cmd = f"SELECT * from activation where code='{code}'"
			cur.execute(cmd)
			ans2 = cur.fetchall()
			cur.close()
			if len(ans1)+len(ans2)==0:
				break
		self.exe(f"INSERT into unactivation values('{code}',{during})")
		return f"CODE: {code}\n期間:{valid_time}"

	async def disable_activation_code(self,code):
		cur = self.conn.cursor()
		cmd = f"SELECT * from unactivation where code='{code}'"
		cur.execute(cmd)
		ans1 = cur.fetchall()
		cmd = f"SELECT * from activation where code='{code}'"
		cur.execute(cmd)
		ans2 = cur.fetchall()
		if len(ans1)!=0:
			cur.close()
			return f"{code}はすでに有効化されています"
		elif len(ans2)!=0:
			cmd = f"DELETE from unactivation where code='{code}'"
			cur.execute(cmd)
			cur.close()
		else:
			cur.close()
			return f"{code}は設定されていません"






