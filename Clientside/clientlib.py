import xmpp
import queue


class Message:
    def __init__(self, time, dst, text):
        self.time = time
        self.dst = dst
        self.text = text


class Client:
    def __init__(self, userId, lName, fName, userAgent):
        """
        Initializes Client class using
        :param userId: Unique UserID 
        :param lName: Last Name
        :param fName: First Name
        :param userAgent: userAgent String to Use
        """
        self.userId = userId
        self.lName = lName
        self.fName = fName
        self.userAgent = userAgent
        self.message_queue = queue.PriorityQueue()
        self.connection_status = 0
        self.xmppclient = None

    def get_conn_status(self):
        return self.connection_status

    def get_id(self):
        return int(self.userId)

    def add_message(self, tmp_message):
        """
        Inserts message into this user's queue sorted by time needs to be sent
        :param tmp_message: Message object to be added to priority queue based on time 
        :return: 1 on success, 0 on fail
        """
        self.message_queue.put((int(tmp_message.time), tmp_message))

    def connect(self, server, port):
        """
        :param server: The Server orxmpp IP address string to connect to
        :param port: string of port to connect to
        :return: 0 on success, -1 on fail
        """
        self.xmppclient = xmpp.Client(server, debug=[])
        if not self.xmppclient.connect(server=(server, port), use_srv=False):
            return -1
        else:
            self.connection_status = 1
            return 0

    def poll_message(self):
        # type: () -> object
        """
        :return: Next Message on queue or None if queue empty
        """
        try:
            return self.message_queue.get(block=False)
        except queue.Empty:
            return None

    def send_message(self, message):
        """
        :param message: string message to send
        :return: 1-delivered, 0-failed
        """
        print message.text
