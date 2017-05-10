import sys
import time
import csv
import getopt
import Queue
import threading
import logging
from datetime import datetime
from datetime import timedelta
from clientlib import Client
from clientlib import Message

___author___ = "Brad Fischl"
___license___ = "GPL"
___version___ = "0.0.1"
___maintainer___ = "Brad Fischl"
___email___ = "bradley.fischl {at} gmail"
___status___ = "Development"
loggingLevel = logging.DEBUG


def load_global(globalvars):
    with open("settings.txt", 'rb') as f:
        for line in f.readlines():
            if line.startswith('#'):
                continue
            name, arg = line.strip().lstrip('#').split('=')
            globalvars[name] = arg
    return globalvars


def load_command_line(argv, globalvars):
    try:
        opts, args = getopt.getopt(argv, "hu:c:p:s:", ["ufile=", "cfile=", "port=", "server="])
    except getopt.GetoptError:
        print 'YOU DONE MESSED UP PLEASE READ THE README AND REEVALUATE YOUR LIFE'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'python main.py [-i users.csv] [-c converstaions.csv] [-p port] [-s server]'
            sys.exit()
        elif opt in ("-u", "--ufile"):
            globalvars['UFILE'] = arg
        elif opt in ("-c", "--cfile"):
            globalvars['CFILE'] = arg
        elif opt in ("-p", "--port"):
            globalvars['PORT'] = arg
        elif opt in ("-s", "--server"):
            globalvars['SERVER'] = arg
            # Load command line options complete
    return globalvars


def to_datetime(time_string):
    """
    Converts time string back to date time val
    :param time_string: 
    :return: datetime object
    """
    return datetime.strptime(time_string.strip('\''), '%Y-%m-%d %H:%M:%S.%f')


def load_csv(infile, outdict, key):
    """
    Loads the user csv into memory, returns dict userid -> userinfo_dict
    :param infile: csv file to read, should be local
    :param outdict: dictionary to be filled with info loaded
    :param key: Used to index returned dict
    :return: outdict
    """
    with open(infile, 'rb') as f:
        reader2 = csv.DictReader(f, delimiter=',')
        for row in reader2:
            outdict[row[key]] = row
    return outdict


def do_work(q, client, globalvars):
    """ The worker thread, attempts to connect to server and port.
    Seeks to send the assigned messages in the client.message_queue at the right time
    see clientlib for more info on clients
    :param q: No idea, seems like a requirement though... 
    :param client: the specific instance for this client
    :param globalvars: a copy of the globalvars sent from main thread
    :return: return 0 on completion
    """
    timeout = 10
    failures = 0
    max_failures = 100

    while client.get_conn_status() < 1:
        if failures > max_failures:
            sys.exit(-1)
        failures += 1
        client.connect(globalvars['SERVER'], globalvars['PORT'])
        logging.critical("Client %d Cannot connect. Retrying in %d...", client.get_id, timeout)
        time.sleep(timeout)
    next_message = client.poll_message()
    while next_message is not None:
        tmp_time_delta = to_datetime(globalvars['HHOUR']) + timedelta(0, int(next_message[1].time)) - datetime.now()
        seconds_left = tmp_time_delta.total_seconds()
        while seconds_left > 0:
            time.sleep(int(seconds_left))
            tmp_time_delta = to_datetime(globalvars['HHOUR']) + timedelta(0, int(next_message[1].time)) - datetime.now()
            seconds_left = tmp_time_delta.total_seconds()
        # time to send next_message
        if client.send_message(next_message[1]) < 0:
            logging.warning("Message Failed:\t%s", next_message[1].text)
        else:
            logging.info("Message Sent:\t%s", next_message[1].text)
        next_message = client.poll_message()
    logging.info("No more messages exiting")
    return 0


def main(argv):
    """
    Reads in configs, starts loggers, starts up worker threads...see do_work()
    :param argv: command line arguments 
    :return: does not return 
    """
    logging.basicConfig(filename='clientside.log', level=loggingLevel, filemode='w')
    globalvars = {}
    # set HHOUR to now
    globalvars['HHOUR'] = str(datetime.now())

    # load settings found in settings.txt, will overwrite HHOUR if in settings.txt
    globalvars = load_global(globalvars)

    # parse command line options, will overwrite settings in settings.txt
    globalvars = load_command_line(argv, globalvars)

    # load user file .csv, format found in README
    clients = {}
    clients = load_csv(globalvars['UFILE'], clients, 'userId')

    # instantiate and load clients objects and add to a dict
    clientlist = dict()
    for key, value in clients.iteritems():
        clientlist[int(value['userId'])] = Client(value['userId'], value['lastName'], value['firstName'],
                                                  value['userAgent'])
    # load conversation file .csv, format found in README
    convos = {}
    convos = load_csv(globalvars['CFILE'], convos, 'senderId')
    # add conversations to individual user data structure
    for key, value in convos.iteritems():
        clientlist[int(key)].add_message(Message(value['time'], value['destId'], value['message']))
    logging.info("ALL CONVOS LOADED")
    # start thread per user
    q = Queue.Queue()
    thread_list = list()
    for key, client in clientlist.iteritems():
        t = threading.Thread(target=do_work, args=(q, client, globalvars))
        t.daemon = True
        t.start()
        thread_list.append(t)
        logging.debug("Thread for clientID %d started", int(key))
    logging.info("ALL THREADS STARTED")
    for t in thread_list:
        logging.debug("THREAD completed")
        t.join()

if __name__ == "__main__":
    main(sys.argv[1:])
