#!/usr/bin/env python
# standard modules
import argparse, os, csv, re, itertools
# personalized modules
try:
				import mySMTP 
except ImportError as e:
#plaintext passwords aren't smart. I should figure out how to change this to not plaintext
				print '''mySMTP is something done on a per user basis and can be as simple as:
import smtplib

sender = <your address>
def newServer():
				smtplib.SMTP(<server address with port>)
				username = <your username>
				password = <your password>
				server.ehlo()
				server.starttls()
				server.login(username,password)
				return server
				'''
				raise e

from email.mime.text import MIMEText

class statuspage:
				def unsubmitted(self):
								return [x for x in self.status if (not x[1] == 'Turn played' and not x[1] == 'Eliminated')]

				def gameName(self):
								headerline = re.findall(r'<tr>\n<td \S+ \S+>(.*)</td>\n</tr>',self.text,re.MULTILINE)[0]
								return re.search('(\S+), turn ',headerline).group(1)

				def currentTurn(self):
								headerline = re.findall(r'<tr>\n<td \S+ \S+>(.*)</td>\n</tr>',self.text,re.MULTILINE)[0]
								return re.search(r'turn ([0-9]+)',headerline).group(1)

				def remainingNations(self):
								return [x[0] for x in self.status if x[1] != 'Eliminated']

				def __init__(self, _path):
								try:
												self.path = _path
												with open(_path,'r') as file_:
																self.text = file_.read()
								except Exception as e:
												print str(e)
								self.rawparse = re.findall(r'<td class="\S+">(.*)</td>',self.text,re.MULTILINE) 	
								self.status = [x for x in zip(self.rawparse[0:len(self.rawparse):2],self.rawparse[1:len(self.rawparse):2])]
								self.turn = self.currentTurn()
								self.gamename = self.gameName()

if __name__ == '__main__':
				parse = argparse.ArgumentParser()
				parse.add_argument("player_list",help="full path to tab separated file of <side> | <email>\nsuch that player_list:<side> <--> statuspage:<side>")
				parse.add_argument("statuspage",help="full path to standard status page output from Dominions4 server")
				parse.add_argument("--action",help="""newturn - email players about the new turn\n
chastise last player to move
remind all players who haven't moved
globalchastise the last player to move""",choices=['newturn','chastise','remind','globalchastise'],default='chastise')
				parse.add_argument("--limiter",help="How many times to chastise people a given turn",type=int,default=3)
				parse.add_argument("--debug",help="for active development work",type=int,default=0)
				#parsed = parse.parse_args("--action chastise /home/pi/dominions4/savedgames/taislitterbox/playerlist.txt /var/www/index.html".split())
				parsed = parse.parse_args()

				# eat the player_list
				with open(parsed.player_list,'r') as player_list_file:
								player_lookup = dict(list(csv.reader(player_list_file,delimiter='\t')))

				# eat status page
				curstatuspage = statuspage(parsed.statuspage)

				# optional eat insults

				try:
								with open(os.path.join(os.path.dirname(curstatuspage.path),curstatuspage.gamename),'r') as tracking_file:
												notifications = list(csv.reader(tracking_file,delimiter='\t'))
				except:
								notifications = list()
				
				if parsed.action=='chastise':
								unsubmitted = curstatuspage.unsubmitted()
								if len(unsubmitted)==1:
												msg = MIMEText("You're the only one who hasn't played your turn!")
												msg['Subject'] = '[AUTOMATED] %s - STOP HAVING A LIFE AND PLAY YOUR DOMINIONS TURN' % (curstatuspage.gamename)
												msg['From']=mySMTP.sender
												msg['To']=player_lookup[unsubmitted[0][0]]
												msg['CC']=mySMTP.sender
												if notifications.count([curstatuspage.turn,msg['To']]) < parsed.limiter:
																try:
																				server = mySMTP.newServer()
																				if parsed.debug: server.sendmail(mySMTP.sender, [mySMTP.sender], msg.as_string())
																				else: server.sendmail(mySMTP.sender, [msg['To']], msg.as_string())
																finally:
																				server.quit()

																notifications.append([curstatuspage.turn,msg['To']])
																with open(os.path.join(os.path.dirname(curstatuspage.path),curstatuspage.gamename),'w') as tracking_file:
																				trackwriter = csv.writer(tracking_file,delimiter='\t')
																				trackwriter.writerows(notifications)

				elif parsed.action=='globalchastise':
								unsubmitted = curstatuspage.unsubmitted()
								if len(unsubmitted)==1:
												msg = MIMEText("You're the only one who hasn't played your turn!")
												msg['Subject'] = '[AUTOMATED] %s - STOP HAVING A LIFE AND PLAY YOUR DOMINIONS TURN' % (curstatuspage.gamename)
												msg['From']=mySMTP.sender
												msg['To']=player_lookup[unsubmitted[0][0]]
												msg['CC']=mySMTP.sender
												if notifications.count([curstatuspage.turn,msg['To']]) < parsed.limiter:
																try:
																				server = mySMTP.newServer()
																				server.sendmail(mySMTP.sender, list(player_lookup.values()), msg.as_string())
																finally:
																				server.quit()

																notifications.append([curstatuspage.turn,msg['To']])
																with open(os.path.join(os.path.dirname(curstatuspage.path),curstatuspage.gamename),'w') as tracking_file:
																				trackwriter = csv.writer(tracking_file,delimiter='\t')
																				trackwriter.writerows(notifications)

				elif parsed.action=='newturn':
								msg = MIMEText("The seasons have passed - a new turn dawns!")
								msg['Subject']="[AUTOMATED] %s - New Turn (%d)" % (curstatuspage.gamename,int(curstatuspage.turn)+1)
								msg['From']=mySMTP.sender
								msg['To']=",".join([player_lookup[nation] for nation in curstatuspage.remainingNations()])
								try:
												server = mySMTP.newServer()
												if parsed.debug: 
																print mySMTP.sender, [msg['To']], msg.as_string()
																server.sendmail(mySMTP.sender, [mySMTP.sender], msg.as_string())
												else: server.sendmail(mySMTP.sender, [player_lookup[nation] for nation in curstatuspage.remainingNations()], msg.as_string())
								finally:
												server.quit()

				elif parsed.action=='finalturn':
								msg = MIMEText("The seasons have passed for a final time. A new God-king rises!")
								msg['Subject']="[AUTOMATED] %s - End (%d)" % (curstatuspage.gamename,int(curstatuspage.turn))
								msg['From']=mySMTP.sender
								msg['To']=",".join(player_lookup.values())
								try:
												server = mySMTP.newServer()
												if parsed.debug: server.sendmail(mySMTP.sender, [mySMTP.sender], msg.as_string())
												else: server.sendmail(mySMTP.sender, list(player_lookup.values()), msg.as_string())
								finally:
												server.quit()

				elif parsed.action=='remind':
								unsubmitted = curstatuspage.unsubmitted()
								msg = MIMEText("This is a friendly reminder that you need to play your Dominions 4 turn:" + ("\n%s"*len(unsubmitted)) % (tuple(x[0] for x in unsubmitted)))
								msg['Subject']="[AUTOMATED] %s - Reminder - Turn (%s)" % (curstatuspage.gamename,curstatuspage.turn)
								msg['From']=mySMTP.sender
								msg['To']=",".join([player_lookup[x[0]] for x in unsubmitted])
								try:
												server = mySMTP.newServer()
												if parsed.debug:
																print mySMTP.sender, [msg['To']], msg.as_string()
																server.sendmail(mySMTP.sender, [mySMTP.sender], msg.as_string())
												else: server.sendmail(mySMTP.sender, [player_lookup[x[0]] for x in unsubmitted], msg.as_string())
								finally:
												server.quit()

				# if one_turn_unsubmitted
				# if turn ended
				# --if turn was missed
				#last_submission('romanticfool@gmail.com')
