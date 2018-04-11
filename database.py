import sqlite3
import datetime
import json

class database():

	db = sqlite3.connect(':memory:')

	def setup(self):
		with self.db:
			self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, created DATETIME, daysvalid INTEGER, requestedby TEXT)')

	def close(self):
		self.db.close()

	def add_user(self,user):
		with self.db:
			self.db.execute('INSERT INTO users(username,created,daysvalid,requestedby) VALUES(:username,:created,:daysvalid,:requestedby)',
				{'username':user['username'], 'created':user['created'], 'daysvalid':user['daysvalid'], 'requestedby':user['requestedby']})

	def get_user(self,username=None):
		self.db.row_factory = lambda C, R: { c[0]: R[i] for i, c in enumerate(C.description) }
		cur = self.db.cursor()

		if not username:
			cur.execute('SELECT id, username, created, daysvalid, requestedby FROM users')
		else:
			cur.execute('SELECT username, created, daysvalid, requestedby FROM users WHERE username=:username', {'username':username})

		result = cur.fetchall()

		return result

d = database()
d.setup()
user = {'username':'testing', 'created':datetime.datetime.now(), 'daysvalid':'10', 'requestedby':'1.1.1.1'}
d.add_user(user)
d.add_user(user)
d.add_user(user)
d.add_user(user)
print json.dumps(d.get_user(),indent=4)
d.close()
