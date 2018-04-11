import sqlite3
import datetime

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

		cur = self.db.cursor()

		if not username:
			cur.execute('SELECT username, created, daysvalid, requestedby FROM users')
		else:
			cur.execute('SELECT username, created, daysvalid, requestedby FROM users WHERE username=:username', {'username':username})

		return cur.fetchall()

d = database()
d.setup()
user = {'username':'testing', 'created':datetime.datetime.now(), 'daysvalid':'10', 'requestedby':'1.1.1.1'}
d.add_user(user)
print d.get_user()
d.close()
