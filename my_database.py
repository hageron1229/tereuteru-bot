from my_log import *

import time
import sqlite3 as sq
from pprint import pprint

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