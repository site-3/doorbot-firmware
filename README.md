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
* **Name** - this is used to log the coming and going of members
* **Plan** - this needs to be one of the values defined in the `rules.csv` file (see below)
* **RFID** - the tag ID assigned to that member
* **Custom access**
  * if empty, shop access for that member is granted according to the access rules for the `Plan`
  * otherwise, custom access rules can be set for that member using the same format used in `rules.csv` (see below). If custom access rules are set, they _replace_ those of the `Plan` for that member. If you want to extend the default rules (e.g. add a day), you need to specify the entire set of days you want to give access to that member.
  * this can be set to `NEVER` to (temporarily) ban a member from accessing the shop
* **Expiry** - can be either empty or contain a date in the `YYYY-MM-DD` format to indicate when access to the shop expires for that member. Access will expire at 23:59 (11:59PM) on the date indicated in this field.
The file can have as many other columns as needed for other purposes (e.g. payment processing) as long as they don't duplicate the above column names.

Example:
```
Name  , Plan      , RFID     , Custom access        , Expiry
Alice , Core      , 66cd0b11 ,                      , 2018-12-31
Bob   , Associate , 245d22fe ,                      ,
Carl  , Associate , 234fe35a , "WED 8:00-16:00,FRI" ,
```

### Plans and access rules database
Default access rules associated with the different plans are defined in a `rules.csv` file that should
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
