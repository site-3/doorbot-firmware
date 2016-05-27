# Doorbot Firmware

This repository contains the code necessary to run the Site 3 Doorbot.

The doorbot is made of two different boards:
* an Arduino that runs the RFID tag reader and the door latch
* a Raspberry Pi that runs a Python script to match the RFID tags with the member database
  and determine if access should be given.

Based on Paul Walker's [code](https://github.com/pauldw/door-troll-firmware).

## Arduino firmware

See http://www.accxproducts.com/wiki/index.php?title=Open_Access_4.0 for the original board information.

You need to copy the directories in `/libraries` to your Arduino IDE library folder.

Note that using the same reader, and NFC IDs with 4-byte IDs, you will only get three bytes from the Wiegand reader, and they will be in this pattern:

`B1 B2 B3 B4 -> B3 B2 B1`

So 0x12345678 will become 0x563412.

## Python controller

The code that checks the member database and determine whether access should be given after a tag has been read
is in the `rpi` directory. It is run on the Raspberry Pi.

### Members database
Members are defined in a `members.csv` file that should at least include the following columns:
* Name - Can be any text
* Plan - The plan types and associated access rules are defined in `roles.csv`, see below.
* RFID - Member fob information
* Custom access (optional) - Custom rules defined here will **override** the default rules associated with that member's
  plan.
Additional columns (e.g. Email), will be ignored by the controller.
Note that if the custom access rule includes multiple days, those will be separated by commas. Thus the custom rule
needs to be delimited by double quotes in the CSV to avoid confusion.

Example:
```
Name  , Plan      , RFID     , Custom access
Alice , Core      , 66cd0b11 ,
Bob   , Associate , 245d22fe ,
Carl  , Associate , 234fe35a , "WED 8:00-16:00,FRI"
```

### Plans and access rules database
Default access rules associated with the different plans are defined in a `roles.csv` file that should
at least include the following columns:
* Plan - The plan type. Should correspond to the values entered in the members database (see above).
* Open times - Default access rules associated with that plan.

Rules are specified as a list of strings, of the following format
 * `ALWAYS` : Access is always granted (e.g. for core members)
 * `NEVER` : Access is never granted (e.g. for banned members)
 * `MON` : Access can be granted to a whole day (e.g. MON for every Monday).
   Days can be `MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT` or `SUN`.
 * `MON 16:00-24:00` : Access can be granted to a specified time interval (in 24 hour format)
Note that if a rule includes multiple days, those will be separated by commas. Thus the rule
needs to be delimited by double quotes in the CSV to avoid confusion.

Example:
```
Plan      , Open times
Core      , ALWAYS
Associate , "MON 16:00-24:00, TUE 18:00-24:00, THU 16:00-24:00, SAT, SUN"
```

### Testing
Whenever a change is made in either the `members.csv` or `roles.csv` files,
it's a good idea to test those file to see if all access rules are understood by the controller.
The `rpi/doorbot-test.py` script can be used to do so.

Usage:
```
$ python doorbot-test.py <files-to-test>
```
Example:
```
$ python rpi/doorbot-test.py testing/members.csv testing/roles.csv missing-file.csv testing/log.txt 
ERROR: Custom access rule on line 4 of file testing/members.csv is invalid.
ERROR: Missing or invalid rule on line 5 of file testing/roles.csv
ERROR: Missing or invalid rule on line 6 of file testing/roles.csv
ERROR: can't find file missing-file.csv
ERROR: testing/log.txt doesn't look to be a proper membership or rules file.
```
