/* User preferences file - Modify this header to use the correct options for your 
 * installation. 
 * Be sure to set the passwords/etc, as the defaul is "1234"
 */ 

/* Hardware options
 *
 */
#define MCU328         // Set this if using any boards other than the "Mega"
#define HWV3STD        // Use this option if using Open access v3 Standard board
#define MCPIOXP        //  Set this if using the v3 hardware with the MCP23017 i2c IO chip
#define AT24EEPROM     //  Set this if you have the At24C i2c EEPROM chip installed

#define READER2KEYPAD 0 // Set this if your second reader has a keypad                              
                                        
#define DEBUG 2                         // Set to 4 for display of raw tag numbers in BIN, 3 for decimal, 2 for HEX, 1 for only denied, 0 for never.               
#define VERSION 1.36
#define UBAUDRATE 9600                 // Set the baud rate for the USB serial port

#define gonzo   0xFFFFFFFF                  // Name and badge number in HEX. We are not using checksums or site ID, just the whole
#define snake   0xFFFFFFFF                  // output string from the reader.
#define satan   0xFFFFFFFF
const long superUserList[] = { gonzo, snake, satan};  // Super user table (cannot be changed by software)

#define PRIVPASSWORD 0x1234             // Console "priveleged mode" password

#define DOORDELAY 5000                  // How long to open door lock once access is granted. (2500 = 2.5s)
#define SENSORTHRESHOLD 100             // Analog sensor change that will trigger an alarm (0..255)
#define KEYPADTIMEOUT 5000              // Timeout for pin pad entry. Users on keypads can enter commands after reader swipe.
#define CARDFORMAT 1                    // Card format
                                        // 0=first 25 raw bytes from card
                                        // 1=First and second parity bits stripped (default for most systems)
                                        
