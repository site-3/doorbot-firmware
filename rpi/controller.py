# Site 3 Doorbot Controller
#
# Determines whether a fob ID belongs to a current member
# (defined in members.csv)
# and detemines whether they currently have access to the shop
# based on current time and member roles 
# (defined in roles.csv)
#
# Original code by Paul Walker (https://github.com/pauldw/door-troll-firmware)
# Edited by Kate Murphy - hi@kate.io - Jan 2016
# Edited by Thomas Guignard - tom@timtom.ca - May 2016

import serial
import time
from datetime import datetime
import csv
import re

board_port_name = "/dev/ttyAMA0"
#membership_file = "/home/pi/members.csv"
#log_file = "/home/pi/log.txt"
membership_file = "../testing/members.csv"
roles_file = "../testing/roles.csv"
log_file = "../testing/log.txt"


def is_associate_time(today):
    '''Returns True if associates have access at the passed datetime, False otherwise.'''

    # Monday access (Associate's night)
    if today.weekday() == 0 and today.hour >= 16:
        return True

    # Tuesday access (LGBTQ + Ladies's night)
    if today.weekday() == 1 and today.hour >= 18:
        return True

    # Thursday evenings (open house night)
    if today.weekday() == 3 and today.hour >= 16:
        return True

    # Weekend access
    if today.weekday() in [5,6]:
        return True

    # Default is not open
    return False

def wiegandify(_id):
    '''Performs the same 3-byte truncation that your NFC wiegand readers do.'''
    result = _id[4:6] + _id[2:4] + _id[0:2]
    result = "".join([c.capitalize() for c in result])
    result = result.lstrip('0')

    return result

def format_id(_id):
    '''Strips and pads IDs.'''
    stripped = _id.strip()
    padded = "0" * (8 - len(stripped)) + stripped
    capitalized = "".join([c.capitalize() for c in padded])
    return capitalized

def log(message):
    f = open(log_file, "a")
    f.write("[%s] %s\n" % (time.ctime(), message))
    f.close()

class Board(object):
    def __init__(self, port_name=board_port_name, baud_rate=9600):
        self.port = serial.Serial(port_name, baudrate=baud_rate)

    def unlock(self):
        self.port.write("u\n")

        if self.port.readline().strip() == "OK":
            return True
        else:
            return False

    def get_tag(self):
        '''Blocking.  Return ID if one is sent by board, None otherwise.'''
        line = self.port.readline()
        fields = line.strip().split('\t')

        if len(fields) != 2 or fields[0] != "ID":
            return None
        else:
            return fields[1]

class Members(object):
    def __init__(self, filename=membership_file):
        f = open(filename, 'rb')
        self.members = [i for i in csv.DictReader(f, delimiter=',')]

    def get_by_tag(self, tag_id):
        for m in self.members:
            #print "Checking tag ", tag_id, " against member ", m['Name']
            #print "RFID: ", m['RFID']
            #print "format_id: ", format_id(m['RFID'])
            #print "wiegandify: ", wiegandify(format_id(m['RFID']))
            if tag_id == wiegandify(format_id(m['RFID'])):
                return m
        return None

class Roles(object):
    def __init__(self, filename=roles_file):
           f = open(filename, 'rb')
           #self.roles = [i for i in csv.DictReader(f, delimiter=',')]
           #print self.roles
           
           regex=re.compile('(ALWAYS|NEVER|\w{3})(?: *(\d{1,2}:\d{2}) *- *(\d{1,2}:\d{2}))?')
           # Matches strings of the form
           # ALWAYS
           # MON 16:00-24:00
           # TUE
           # try it out at https://regex101.com/r/oT6zF2/1
           
           self.rules = {}
           
           for line in csv.DictReader(f, delimiter=','):
               plan = line['Plan']
               times = map(regex.findall, line['Open times'].split(','))
               self.rules.setdefault(plan,[]).append(times)
           print self.rules
           
    def get_by_plan(self, plan):
        return self.rules[plan]

def run():
    b = Board()

    log("started.")

    while True:
        tag = b.get_tag()
        m = Members()
        member = m.get_by_tag(tag)
        now = datetime.now()

        log("Tag scanned: %s %s" % (tag, wiegandify(tag)))

        if member == None:
            log("Could not find member with tag %s." % (tag))
            continue

        if (member['Plan'] in ['Core', 'Distance', 'Grouped', 'Free']):
            log("Granted access to %s because they are a paid core member" % member['Email'])
            b.unlock()
            continue
        elif member["Plan"] == "Associate":
            if is_associate_time(now):
                log("Granted access to %s because they are an associate" % member['Email'])
                b.unlock()
            else:
                log("Refused access to %s because it is outside allowed associate hours" % member['Email'])
            continue

        log("Refused access to %s" % member['Email'])


def testauth(sampletag):
    # Function used to test the authentication code
    
    tag = sampletag   
    members = Members()
    roles = Roles()
    member = members.get_by_tag(tag)
    now = datetime.now()

    log("Tag scanned: %s %s" % (tag, wiegandify(tag)))
    
    print "Identified member ", member['Name'], " of type ", member['Plan']
    print roles.get_by_plan(member['Plan'])
    print roles.rules[member['Plan']][0][0][0][0]

if __name__ == "__main__":
    #run()
    testauth('BCD64')
