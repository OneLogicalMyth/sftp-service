import sqlite3
import datetime

class database(object):

	def __init__(self):
		self.db = sqlite3.connect('data.db')

	def setup(self):
		with self.db:
			self.db.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, created DATETIME, daysvalid INTEGER, requestedby TEXT)')
			self.db.execute('CREATE TABLE IF NOT EXISTS blacklist(id INTEGER PRIMARY KEY, ip TEXT, created DATETIME)')

	def close(self):
		self.db.close()

	def add_user(self,user):
		dt = datetime.datetime.now()
		with self.db:
			self.db.execute('INSERT INTO users(username,created,daysvalid,requestedby) VALUES(:username,:created,:daysvalid,:requestedby)',
				{'username':user['username'], 'created':dt, 'daysvalid':user['daysvalid'], 'requestedby':user['requestedby']})

	def get_user(self,username=None):
		self.db.row_factory = lambda C, R: { c[0]: R[i] for i, c in enumerate(C.description) }
		cur = self.db.cursor()

		if not username:
			cur.execute('SELECT username, created, daysvalid, requestedby FROM users')
		else:
			cur.execute('SELECT username, created, daysvalid, requestedby FROM users WHERE username=:username', {'username':username})

		result = cur.fetchall()

		return result

	def del_user(self,username):
		with self.db:
			self.db.execute('DELETE FROM users WHERE username=:username',{'username':username})

	def add_blacklist(self,ip):
		dt = datetime.datetime.now()
		with self.db:
			self.db.execute('INSERT INTO blacklist(ip, created) VALUES(:ip,:created)',{'ip':ip, 'created':dt})

	def get_blacklist(self,ip=None):
		self.db.row_factory = lambda C, R: { c[0]: R[i] for i, c in enumerate(C.description) }
		cur = self.db.cursor()

		if not ip:
			cur.execute('SELECT ip, created FROM blacklist')
		else:
			cur.execute('SELECT ip, created FROM blacklist WHERE ip=:ip', {'ip':ip})

		result = cur.fetchall()

		return result

	def del_blacklist(self,ip):
		with self.db:
			self.db.execute('DELETE FROM blacklist WHERE ip=:ip',{'ip':ip})

