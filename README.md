# vulnchat

v0.0.1

Dependencies:
* [sleekxmpp](http://sleekxmpp.com/) (pip install sleekxmpp)
* [jsonschema](https://pypi.python.org/pypi/jsonschema) (pip install jsonschema)

Written by: bfischl

GPLv3 applies

Vulnchat leverages SleekXMPP to simulate multiple clients for the use of traffic generation
to a vulnerable server. It is intended for use with a vulnerable XMPP server which students
can attack. The purpose of generating robust traffic is to increase the content to sift through
after a successful attack. This framework provides the ability to modify settings in a way that
allows for different vulnerabilities to allow variety and increase difficulty for students and
decrease ability to pass answers along.

Each user defined in the user csv file is given its own thread. It has its own list of actions(limited to
sending messages at this time) to take on the XMPP server. Each action (message to send) has a specified
time to be completed. Each thread follows the general process:
1. Add scheduled events for each message it is responsible for (self.scheduler.add())
1. Connect to XMPP Server, register if no registration found
1. Send messages
1. Exit when queue is empty

This software is provided as is, with no warranty and no expectation of support.


USAGE
-----
~~~python
    ./clients.py
	-h,	prints help and exit
	[-u,--ufile]	csv file containing users
	[-c,--cfile]    csv file containing conversations
	[-p,--port]     xmpp server port
	[-s,--server]   xmpp server address or hostname
~~~

Any command line argument will be used in place of the default values in settings.txt



UNDERSTANDING CONFIGS
---------------------


settings.txt contains the default settings

user.csv must contain:
* userid (unique)
* jid
* password
* useragent

conversation.csv must contain:
* messageid (unique)
* senderid  (must match a userid, above)
* destid    (must match a jid, above)
* time      (in seconds after *HHOUR*, a datetime object in settings)
* message   (string value of message to be sent)

TODO
----
1. Switch to JSON
    * Users and actions should be JSON'ed
1. Switch from "conversations" to "actions", implement more callbacks
    * ACTION - Update presence
    * ACTION - Send Message
    * ACTION - Update location
    * ACTION - Change status to "busy" or "available"
1. Implement event handler
    * Main thread receives events in JSON format and calls actions based on them
        * For example, user X's phone is destroyed. User X's scheduled actions should all be destroyed
1. Error Check on loading json files, once completed
