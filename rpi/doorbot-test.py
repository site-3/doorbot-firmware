# Site 3 Doorbot Tester
#
# Parses a file given as argument (either membership csv file or rules csv file)
# looking for doorbot rules, attempts to interpret them and return an
# error message if any unknown rules are encountered.
#
# Usage: doorbot-test.py <files>
#
# <files> is a list of one or more files to be tested. A typical scenario
# is to test both the members.csv and the roles.csv file:
# 
# doorbot-test.py members.csv roles.csv
#
# by Thomas Guignard - tom@timtom.ca - May 2016

import sys
import csv
import os.path
import controller

allowed_rules = {"MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN", "ALWAYS", "NEVER"}

for infile in sys.argv[1:]:
    if os.path.isfile(infile):
        f = open(infile, 'rb')
        for index,line in enumerate(csv.DictReader(f, delimiter=',')):
            if 'Open times' in line:
                # Looks like this file is a rules file
                read_rules = controller.process_rules(line['Open times'])
                #print read_rules
                for rule in read_rules:
                    if len(rule) == 0:
                        print("ERROR: Missing or invalid rule on line %d of file %s" % (index+2, infile))
                        break
                    elif (rule[0][0] not in allowed_rules):
                        print("ERROR: %s is not a valid keyword on line %d of file %s" % (rule[0][0], index+2, infile))
                        break
                
            elif 'Custom access' in line:
                # Looks like this file is a membership file
                read_rules = controller.process_rules(line['Custom access'])
                for rule in read_rules:
                    if (len(rule) == 0 and not len(line['Custom access']) == 0):
                        print("ERROR: Custom access rule on line %d of file %s is invalid." % (index+2, infile))
                        break
            else:
                # Looks like this file is neither of the recognized type.
                print("ERROR: %s doesn't look to be a proper membership or rules file." % infile)
                break
    else:
        print("ERROR: can't find file %s" % infile)
        continue

