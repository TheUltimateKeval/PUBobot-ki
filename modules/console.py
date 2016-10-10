#!/usr/bin/python2
# encoding: utf-8

from threading import Thread
from multiprocessing import Queue
import sys, os, datetime, readline

from modules import bot, client, config

class ConsoleCompleter(object):  # Custom completer

	def __init__(self):
		self.commands = sorted(["help", "say", "exec", "quit", "status", "notice", "reset_players", "disable_pickups", "pickups", "stats"])
		self.modules = sorted(["bot", "client", "config"])

	def complete(self, text, state):
		if state == 0:  # on first trigger, build possible matches
			texttup = text.split(' ')
			tuplen = len(texttup)
			if tuplen == 0:
				self.matches = self.commands[:]
			elif tuplen == 1:
				self.matches = [s for s in self.commands if s and s.startswith(text)]
			elif tuplen == 2:
				if texttup[0] in ["say", "disable_pickups"]:
					chans = sorted([c.name for c in bot.channels])
					if texttup[1] == '':
						chans = [texttup[0]+" "+c+"#" for c in chans]
						self.matches = chans[:]
					else:
						self.matches = [texttup[0]+" "+s for s in chans if s and s.startswith(' '.join(texttup[1:len(texttup)]))]
		# return match indexed by state
		try:
			return self.matches[state]
		except IndexError:
			return None

def init():
	global thread, log, userinput_queue, alive

	alive = True
	#init log file
	if not os.path.exists(os.path.abspath("logs")):
	  os.makedirs('logs')
	log = open(datetime.datetime.now().strftime("logs/log_%Y-%m-%d-%H:%M"),'w')
	
	userinput_queue = Queue()

	#init user console
	thread = Thread(target = userinput, name = "Userinput")
	thread.daemon = True
	thread.start()

		
def userinput():
	completer = ConsoleCompleter()
	readline.set_completer(completer.complete)
	readline.set_completer_delims('')
	readline.parse_and_bind("tab: complete")
	while 1:
		inputcmd=input()
		userinput_queue.put(inputcmd)

def run():
	try:
		cmd = userinput_queue.get(False)
		display("CONSOLE| /"+cmd)
		try:
			l = cmd.split(" ", 1)
			if l[0] == "help":
				display("CONSOLE| "+help)
			elif l[0] == "notice":
				for i in bot.channels:
					client.notice(i.channel, l[1])
			elif l[0] == "say":
				channel, text = l[1].split("#", 1)
				for i in bot.channels:
					if i.name == channel:
						client.notice(i.channel, text)
						return
			elif l[0] == "disable_pickups":
				channel = rstrip("#")
				for i in bot.channels:
					if i.name == channel:
						config.delete_channel(i.channel)
			elif l[0] == "status":
				display("CONSOLE| Total pickup channels: {0}. {1} messages to send waiting in queue.".format(len(bot.channels), len(client.send_queue)))
			elif l[0] == "pickups":
				channels = []
				for c in bot.channels:
					pickups=[]
					for p in c.pickups:
						if p.players != []:
							pickups.append('[{0} ({1}/{2})]'.format(p.name, len(p.players), p.maxplayers))
					if pickups != []:
						channels.append("{0} {1}".format(c.name, " ".join(pickups)))
				display("All pickups: {0}".format(" | ".join(channels)))
			elif l[0] == "stats":
				for c in bot.channels:
					display("STATS| {0}: {1}".format(c.name, c.stats.stats()))
			elif l[0] == "channels":
				display("CONSOLE| Pickup channels: {0}".format(" | ".join([i.name for i in bot.channels])))
			elif l[0] == "exec":
				exec(l[1])
			elif l[0] == "reset_players":
				comment = False
				if len(l)>1:
					comment = l[1]
				for i in bot.channels:
					i.reset_players(comment=l[1])
			elif l[0] == "quit":
				terminate()
		except Exception as e:
			display("CONSOLE| ERROR: "+str(e))
	except:
		pass
			
def display(data):
	text = str(data)
	text=datetime.datetime.now().strftime("(%H:%M:%S)")+text # add date and time
	linebuffer=readline.get_line_buffer()
	sys.stdout.write("\r\n\033[F\033[K"+text+'\r\n>'+linebuffer)
	log.write(text+'\r\n')

def terminate():
	global alive
	bot.terminate()
	log.close()
	print("Waiting for connection to close...")
	alive = False
	
help = """Commands:
  help - display this message.
  notice %text% - say %text% on all pickup channels.
  say %channel% %text% - say %text% on %channel%.
  disable_pickups %channel% - disable pickups on %channel%.
  status - display overall status.
  channels - list of all pickup channels.
  pickups - list of all active pickup queues.
  stats - list of overall stats of all channels.
  exec %code% - exec a python code.
  reset_players [comment] - reset players on all channels and highlight them.
  quit - save and quit."""
