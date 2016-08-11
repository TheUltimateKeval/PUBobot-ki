#!/usr/bin/python2
# encoding: utf-8

import shutil, os, imp
from modules import console, bot

def init(dirname=""):
	global cfg
	
	#load config
	f = open(dirname + 'config.cfg', 'r')
	try:
		cfg = imp.load_source('data', '', f)
	except Exception as e:
		console.display("ERROR PARSING config.cfg FILE!!! {0}".format(str(e)))
		console.terminate()
	
	#search for channels
	for i in os.listdir('channels'):
		if i != 'default':
			bot.channels_list.append(i)

def new_channel(channel, admin):
	path = "channels/"+channel.id
	shutil.copytree("channels/default", path)
	c = bot.Channel(channel)
	c.cfg["ADMINID"] = admin.id
	bot.channels.append(c)

def delete_channel(channel):
	for i in bot.channels:
		if i.id == channel.id:
			bot.channels.remove(i)
			i.stats.close()
			oldpath = "channels/"+channel.id
			newpath = "trash/"+channel.id
			if os.path.exists(newpath):
				shutil.rmtree(newpath)
			shutil.move(oldpath, newpath)
			return True
	return False

def backup_channel(channel, name):
	path = "channels/{0}/stats.sql".format(channel.id)
	backup_path = "channels/{0}/backup_{1}.sql".format(channel.id, name)
	shutil.copy(path, backup_path)

def load_backup_channel(channel, name):
	backup_path = "channels/{0}/backup_{1}.sql".format(channel.id, name)
	path = "channels/{0}/stats.sql".format(channel.id)
	if os.path.exists(backup_path):
		channel.reset_players()
		channel.stats.close()
		shutil.copy(backup_path, path)
		channel.__init__(channel.channel)
		return True
	else:
		return False
