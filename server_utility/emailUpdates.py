#!/usr/bin/env python
# standard modules
import sys
sys.settrace
import argparse, os, csv, re
# personalized modules
try:
    import mySMTP 
except ImportError as e:
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
chastise - last player to move
remind - all players who haven't moved
finalturn""",choices=['newturn','chastise','remind','finalturn'],default='chastise')
    parse.add_argument("--limiter",help="How many times to chastise people a given turn",type=int,default=3)
    parse.add_argument("--debug",help="for active development work",type=int,default=0)
    parsed = parse.parse_args()

    print parsed

    # eat the player_list data
    with open(parsed.player_list,'r') as player_list_file:
        player_list_filedata = list(csv.reader(player_list_file,delimiter='\t'))

    # eat the player_list data
    player_lookup = {x[0]:x[1] for x in player_list_filedata if x[1] !=
    'None'}

    # eat status page
    curstatuspage = statuspage(parsed.statuspage)

    # optional eat insults
    try:
        with open(os.path.join(os.path.dirname(curstatuspage.path),curstatuspage.gamename),'r') as tracking_file:
            notifications = list(csv.reader(tracking_file,delimiter='\t'))
    except:
        notifications = list()

    from email.mime.text import MIMEText

    def send_email(subject, text, recipients):
        if (len(recipients)== 0): 
            print("\nNo recipients!")
            return
        msg = MIMEText("{0:s}".format(_text))
        msg['Subject'] = subject
        msg['From']    = mySMTP.sender
        try:
            server = mySMTP.newServer()
            if parsed.debug: server.sendmail(mySMTP.sender, [mySMTP.sender], msg.as_string())
            else: server.sendmail(mySMTP.sender, recipients, msg.as_string())
        finally:
            server.quit()

    unsubmitted = [y for y in set(map(lambda x: player_lookup.get(x[0],'None'),
        curstatuspage.unsubmitted())) if y != 'None']

    allplayers = [y for y in set(map(lambda x: player_lookup.get(x[0],'None'),
        curstatuspage.status)) if y != 'None']


    def actionfxn(*args):
        header = '[AUTO][DOM4] {gamename:s} {turn:s} - '.format(gamename= 
                curstatuspage.gamename, turn= curstatuspage.turn) 
        return {'Subject':header+args[0], 'Body':args[1], 'Recipients':args[2]}

    actionmap = {
            'chastise':(len(unsubmitted) == 1, actionfxn("Holdup", "You're the only one who hasn't played your turn!", unsubmitted)),
            'newturn':(True, actionfxn("New Turn", "The seasons have passed - a new turn dawns!", allplayers)),
            'remind':(True, actionfxn("Reminder", "This is a friendly reminder that you need to play your Dominions 4 turn:", unsubmitted)),
            'finalturn':(True, actionfxn("Final Turn", "The seasons have passed for a final time. A new God-king rises!", allplayers)) }

    if actionmap[parsed.action][0]: send_email(actionmap[parsed.action][1])
