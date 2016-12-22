# -*- coding=utf-8 -*-
import requests
import json
import time
# import multiprocessing as mp
import threading as th
import ConfigParser
import fbchat
import datetime
import os

INIT = './btcnotifier.ini'
BTCURL = 'http://api.coindesk.com/v1/bpi/currentprice.json'

def job_watch_btc(bot, period_sec):
    while True:
        resp = requests.get(BTCURL)
        try:
            curr_price = json.loads(resp.content)['bpi']['USD']['rate_float']
            timestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            bot.curr_price = curr_price
            bot.curr_price_time = timestr
            
            print '[%s] price:' % timestr, curr_price
            # print 'bot(parsing):', bot
            # bot.print_listeners()
            
            for (uid, updown, price, done) in bot.iter_listeners(True):
                # print 'iter:', (uid, updown, price, done)
                if (updown == 'up' and curr_price > price) or \
                        (updown == 'down' and curr_price < price):
                    # print 'go to do notify'
                    bot.notify(uid, updown, curr_price, price)
                    # print 'done do notify'
        except Exception as e:
            print 'except:', str(e)
            pass
        time.sleep(period_sec)


def job_listenbot(bot):
    print 'listening'
    # bot.listen()    

def init_bot():
    bot = BTCBot('dolala1357@gmail.com', 'gg1qaz2wsx')
    return bot


class BTCBot(fbchat.Client):

    def __init__(self,email, password, debug=True, user_agent=None):
        fbchat.Client.__init__(self,email, password, debug, user_agent)
        self.listeners_file = './listeners.list'
        self.listeners = self._load_listeners()
        self.curr_price = 0.
        self.curr_price_time = ''

    def on_message(self, mid, author_id, author_name, message, metadata):
        self.markAsDelivered(author_id, mid) #mark delivered
        self.markAsRead(author_id) #mark read

        print("%s said: %s"%(author_id, message))
        # print 'bot:', self

        #if you are not the author, echo
        if str(author_id) != str(self.uid):
            replymsg = self._handle(author_id, message)
            if replymsg:
                self.send(author_id, replymsg)

    def iter_listeners(self, only_not_done=False):
        for uid in self.listeners:
            for (updown, price, done) in self.listeners[uid]:
                if only_not_done and done:
                    continue
                yield (uid, updown, price, done)

    def notify(self, uid, updown, curr_price, price):
        print 'notify:', uid, updown, curr_price, price
        msg = '比特幣現價 %f. (%s, %d)' % (curr_price, updown, price)
        self.send(uid, msg)
        for i,listen in enumerate(self.listeners[uid]):
            if listen[0] == updown and listen[1] == price:
                self.listeners[uid][i][2] = True
        
        self._write_listeners()


    def _handle(self, uid, msg):
        # print 'bot(handle):', self
        if msg.startswith('/up'):
            try:
                price = int(msg.split(' ')[1])
                self._add_listener(uid, 'up', price)
                return 'Added: %s, %s, %d' % (uid, 'up', price)
            except:
                return 'wrong format. (/up price)'
        elif msg.startswith('/down'):
            try:
                price = int(msg.split(' ')[1])
                self._add_listener(uid, 'down', price)
                return 'Added: %s, %s, %d' % (uid, 'down', price)
            except:
                return 'wrong format. (/down price)'

        elif msg.startswith('/now'):
            return str(self.curr_price) + ' @ ' + self.curr_price_time
            
        else:
            return "Doesn't mean anythin to me."
    
    def _load_listeners(self):
        if not os.path.exists(self.listeners_file):
            open(self.listeners_file, 'w+').close()

        d = {}
        with open(self.listeners_file, 'r') as f:
            for l in f:
                print 'line: %s' % l.strip()
                if not l.strip():
                    continue
                uid, updown, price, done = l.strip().split(',')
                price = int(price)
                done = bool(int(done))
                if uid not in d:
                    d[uid] = []
                d[uid].append([updown, price, done])

        conf = d
        return conf

    def _add_listener(self, uid, updown, price):
        if uid not in self.listeners:
            self.listeners[uid] = []
        self.listeners[uid].append([updown, price, False])
        self._write_listeners()

    def _write_listeners(self):
        print 'write_listeners',
        self.print_listeners()
        with open(self.listeners_file, 'w+') as f:
            for uid in self.listeners:
                for (updown, price, done) in self.listeners[uid]:
                    print>>f, '%s,%s,%d,%d' % (uid, updown, price, int(done))

    def print_listeners(self):
        print self.listeners
    

def main():
    config = ConfigParser.ConfigParser()
    config.read(INIT)
    
    email = config.get('Basic', 'email')
    password = config.get('Basic', 'password')
    bot = BTCBot(email, password)

    # the thread is for periodically parsing BTC price
    period_sec = config.getfloat('Basic', 'btc_period_sec')
    t_btc = th.Thread(target=job_watch_btc, args=(bot, period_sec))
    t_btc.daemon = True
    t_btc.start()

    # block here: listen to messages
    bot.listen()


if __name__ == '__main__':
    main()
