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
# Edited by Thomas Guignard - tom@timtom.ca - May 2016 & Dec 2018

import serial
import time
from datetime import datetime, timedelta
import csv
import re

board_port_name = "/dev/ttyAMA0"
membership_file = "/home/pi/members.csv"
log_file = "/home/pi/log.txt"
roles_file = "/home/pi/rules.csv"

# Set this to True during debugging, and to False during normal operation, to manage log size
verbose_log = True

# This function checks if a given time is within the rules
# Rules are specified as a list of strings, of the following format
#   ALWAYS                    : Access is always granted (e.g. for core members)
#   NEVER                     : Access is never granted (e.g. for banned members)
#   MON                       : Access can be granted to a whole day (e.g. MON for every Monday)
#   MON 16:00-24:00           : Access can be granted to a specified time interval (in 24 hour format)
def check_access(rules, time=datetime.now()):
    days = {
    0 : "MON",
    1 : "TUE",
    2 : "WED",
    3 : "THU",
    4 : "FRI",
    5 : "SAT",
    6 : "SUN"
    }
    
    # Don't grant access by default
    result = False
    
    if rules[0][0][0] == 'ALWAYS':
        # Access is always granted for that person
        reason = "access is always granted"
        result = True
    elif rules[0][0][0] == 'NEVER':
        # Access is never granted for that person
        reason = "access is never granted"
        result = False
    else:
        # Day and time rules are associated with that person
        # Process rules
        thisday = time.weekday()
        thishour = time.hour
        thisminute = time.minute
        
        for rule in rules:
            # Check day
            if rule[0][0] == days[thisday]:
                # Day matches
                if not rule[0][1]:
                    # If times are not specified, access is granted for that whole day
                    result = True
                else:
                    # If times are specified, check that we are within the interval
                    starthour, startminute = map(int, rule[0][1].split(':'))
                    endhour, endminute = map(int, rule[0][2].split(':'))
                    
                    if (starthour*60+startminute <= thishour*60+thisminute <= endhour*60+endminute):
                        result = True
        
        if (result):
            if (verbose_log):
                reason = "%s (%s) is during allowed hours %s" % (time, days[thisday], rules)
            else:
                reason = "it is during allowed hours"
        else:
            if (verbose_log):
                reason = "%s (%s) is not during allowed hours %s" % (time, days[thisday], rules)
            else:
                reason = "it is outside allowed hours"
                
    return result, reason

# This function processes an access rule string
# Extracting day of the week, start and end time
def process_rules(times):
    regex=re.compile('(ALWAYS|NEVER|MON|TUE|WED|THU|FRI|SAT|SUN)(?: *(\d{1,2}:\d{2}) *- *(\d{1,2}:\d{2}))?')
    # Matches strings of the form
    # ALWAYS
    # MON 16:00-24:00
    # TUE
    # try it out at https://regex101.com/r/oT6zF2/1
    
    return map(regex.findall, times.split(','))

# These functions are used to process the keyfob IDs
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

# This function writes a timestamped line in the logfile
def log(message):
    f = open(log_file, "a")
    f.write("[%s] %s\n" % (time.ctime(), message))
    f.close()


# This class is used to communicate with the Arduino board 
# that processes the RFID reader
# as well as the door latch.
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


# This class uses the membership CSV file to handle the list of members
# the get_by_tag method will return the member info corresponding to a keyfob
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

# This class uses the roles CSV file to handle the access rules associated with
# the different membership plans.
# The doorcheck_by_plan method will check if a given plan gives access
# at the specified time.
class Roles(object):
    def __init__(self, filename=roles_file):
           f = open(filename, 'rb')
           
           self.rules = {}
           
           for line in csv.DictReader(f, delimiter=','):
               plan = line['Plan']
               times = line['Open times']
               
               self.rules[plan] = process_rules(times)
    
    def get_by_plan(self, plan):
        return self.rules[plan]
    
    def doorcheck_by_plan(self, plan, time=datetime.now()):
        return check_access(self.rules[plan], time)
    
    def doorcheck_by_rules(self, string, time=datetime.now()):
        return check_access(process_rules(string), time)


# # # # THIS IS THE MAIN FUNCTION # # # #
# It runs all the time during normal operation
def run():
    b = Board()

    log("started.")

    while True:
        tag = b.get_tag()
        m = Members()
        roles = Roles()
        member = m.get_by_tag(tag)
        now = datetime.now()

        log("Tag scanned: %s %s" % (tag, wiegandify(tag)))

        if member == None:
            log("Could not find member with tag %s." % (tag))
            continue
        
        # Check the rules for this member
        if (member['Custom access']):
            has_access, reason = roles.doorcheck_by_rules(member['Custom access'])
            log("Custom rules have been defined for %s. Overriding default %s rules." % (member['Name'], member['Plan']))
        else:
            has_access, reason = roles.doorcheck_by_plan(member['Plan'])
        
        # Check that this member is still active
        if (member['Expiry']):
            if (datetime.strptime(member['Expiry'], "%Y-%m-%d") + timedelta(1) < datetime.today()):
                # Membership expires at 23:59:59 of the day indicated in the 'Expiry' column
                has_access = False
                reason = "their access expired on %s at 23:59:59" % member['Expiry']
        
        # Grant access
        if (has_access):
            b.unlock()
            log("Granted access to %s (of type %s) because %s" % (member['Name'], member['Plan'], reason))
        else:
            log("Denied access to %s (of type %s) because %s" % (member['Name'], member['Plan'], reason))


# This is used to test this script without using the actual board, RFID reader or door lock.
def testauth(sampletag):
    # Function used to test the authentication code
    
    tag = sampletag   
    members = Members()
    roles = Roles()
    member = members.get_by_tag(tag)

    log("Tag scanned: %s %s" % (tag, wiegandify(tag)))
    
    # Check the rules for this member
    if (member['Custom access']):
        has_access, reason = roles.doorcheck_by_rules(member['Custom access'])
        log("Custom rules have been defined for %s. Overriding default %s rules." % (member['Name'], member['Plan']))
    else:
        has_access, reason = roles.doorcheck_by_plan(member['Plan'])
    
    # Check that this member is still active
    if (member['Expiry']):
        if (datetime.strptime(member['Expiry'], "%Y-%m-%d") + timedelta(1) < datetime.today()):
            # Membership expires at 23:59:59 of the day indicated in the 'Expiry' column
            has_access = False
            reason = "their access expired on %s at 23:59:59" % member['Expiry']
    
    # Grant access
    if (has_access):
        print "Sesame!"
        log("Granted access to %s (of type %s) because %s" % (member['Name'], member['Plan'], reason))
    else:
        print "Go away"
        log("Denied access to %s (of type %s) because %s" % (member['Name'], member['Plan'], reason))
    

# This will determine which function to run when the script is called.
# For normal operation, it should fire the run() function.
if __name__ == "__main__":
    run()
    