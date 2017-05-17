import sleekxmpp as xmpp
import queue
import sys
import logging
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.util.misc_ops import setdefaultencoding
import dns

class Message:
    def __init__(self, messageid, time, dst, text):
        self.messageid = messageid
        self.time = time
        self.dst = dst
        self.text = text


class Client(xmpp.ClientXMPP):
    def __init__(self, userid, jid, displayname, password, useragent):
        """
        Initially, 
        :param userid: 
        :param jid: 
        :param displayname: 
        :param password: 
        :param useragent: 
        """
        xmpp.ClientXMPP.__init__(self,jid,password)
        self.password = password
        self.message_queue = queue.PriorityQueue()
        self.registration_status = 0
        self.connection_status = 0
        setdefaultencoding('utf8')
        logging.info("Beginning Registration")
        self.register_plugin('xep_0077')
        self.register_plugin('xep_0066')
        self.register_plugin('xep_0004')
        self.register_plugin('xep_0030')
        self['xep_0077'].force_registration = True
        self.add_event_handler("session_start", self.start, threaded=True)
        self.add_event_handler("register", self.register, threaded=True)
        self.add_event_handler("message",self.getmessage,threaded=True)

    def getmessage(self,message):
        print message
        print self.jid

    def sendmessage(self, message):
        """
        :param message: Message Instance, uses sleekxmpp call to send_message
        """
        self.send_message(mto=message.dst,mbody=message.text)

    def get_reg_status(self):
        return self.registration_status

    def get_conn_status(self):
        return self.connection_status

    def add_message(self, tmp_message):
        """
        Inserts message into this user's queue sorted by time needs to be sent
        :param tmp_message: Message object to be added to priority queue based on time 
        :return: 1 on success, 0 on fail
        """
        self.scheduler.add("Send Message",int(tmp_message.time),self.sendmessage,(tmp_message,))
        #self.message_queue.put((int(tmp_message.time), tmp_message))

    def start(self,event):

        self.send_presence()
        self.get_roster()

    def register(self, iq):

        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        try:
            resp.send(now=True)
            self.registration_status = 1
        except IqError as e:
            if e.condition != 'conflict':
                self.registration_status = 1
                self.disconnect()
                sys.exit(2)
        except IqTimeout:
            print "Timeout"
            self.disconnect()

    #def poll_message(self):
        # type: () -> object
    #    """
    #    :return: Next Message on queue or None if queue empty
    #    """
    #    try:
    #        return self.message_queue.get(block=False)
    #    except queue.Empty:
    #        return None

