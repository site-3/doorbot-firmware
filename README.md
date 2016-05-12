# Doorbot Firmware

## Work in progress !
Code in the `flexible-roles` branch is still being tested and is not functional for now.
Ultimately, it will allow custom access rules to be set for individual members, as well as a way
to modify base rules for member types without having to change the code.

## General description

Firmware for the Open Access Standard Rev4 Board used for the Site 3 Doorbot.

See http://www.accxproducts.com/wiki/index.php?title=Open_Access_4.0 for the original board information.

You need to copy the directories in `/libraries` to your Arduino IDE library folder.

Note that using the same reader, and NFC IDs with 4-byte IDs, you will only get three bytes from the Wiegand reader, and they will be in this pattern:

`B1 B2 B3 B4 -> B3 B2 B1`

So 0x12345678 will become 0x563412.

Based on Paul Walker's [code](https://github.com/pauldw/door-troll-firmware).
