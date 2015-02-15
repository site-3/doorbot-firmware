/*
 * Open Source RFID Access Controller - v3 Standard Beta hardware
 *
 * 10/23/2013 Version 1.36
 * Last build test with Arduino v1.05
 * Arclight - arclight@23.org
 * Danozano - danozano@gmail.com
 *
 * Notice: This is free software and is probably buggy. Use it at
 * at your own peril.  Use of this software may result in your
 * doors being left open, your stuff going missing, or buggery by
 * high seas pirates. No warranties are expressed on implied.
 * You are warned.
 *
 *
 * For latest downloads,  see the Wiki at:
 * http://www.accxproducts.com/wiki/index.php?title=Open_Access_4.0
 *
 * For the SVN repository and alternate download site, see:
 * http://code.google.com/p/open-access-control/downloads/list
 *
 * Latest update puts configuration variables in user.h
 * This version supports the new Open Access v4 hardware.
 * 
 *
 * This program interfaces the Arduino to RFID, PIN pad and all
 * other input devices using the Wiegand-26 Communications
 * Protocol. It is recommended that the keypad inputs be
 * opto-isolated in case a malicious user shorts out the 
 * input device.
 * Outputs go to a Darlington relay driver array for door hardware/etc control.
 * Analog inputs are used for alarm sensor monitoring.  These should be
 * isolated as well, since many sensors use +12V. Note that resistors of
 * different values can be used on each zone to detect shorting of the sensor
 * or wiring.
 *
 * Version 4.x of the hardware implements these features and emulates an
 * Arduino Duemilanova.
 * The "standard" hardware uses the MC23017 i2c 16-channel I/O expander.
 * I/O pins are addressed in two banks, as GPA0..7 and GPB0..7
 *
 * Relay outpus on digital pins:  GPA6, GPA7, GPB0, GPB1
 * DS1307 Real Time Clock (I2C):  A4 (SDA), A5 (SCL)
 * Analog pins (for alarm):       A0,A1,A2,A3 
 * Digital input in (tamper):     D9
 * Reader 1:                      D2,D3
 * Reader 2:                      D4,D5
 * RS485 TX enable / RX disable:  D8
 * RS485 RX, TX:                  D6,D7
 * Reader1 LED:                   GPB2
 * Reader1 Buzzer:                GPB3
 * Reader2 LED:                   GPB4 
 * Reader2 Buzzer:                GPB5
 * Status LED:                    GPB6
 
 * LCD RS:                        GPA0
 * LCD EN:                        GPA1
 * LCD D4..D7:                    GPA2..GPA5
 
 * Ethernet/SPI:                  D10..D1313  (Not used, reserved for the Ethernet shield)
 * 
 * Quickstart tips: 
 * Set the console password(PRIVPASSWORD) value to a numeric DEC or HEX value.
 * Define the static user list by swiping a tag and copying the value received into the #define values shown below 
 * Compile and upload the code, then log in via serial console at 57600,8,N,1
 *
 */
#include "user.h"         // User preferences file. Use this to select hardware options, passwords, etc.
#include <Wire.h>         // Needed for I2C Connection to the DS1307 date/time chip
#include <avr/pgmspace.h> // Allows data to be stored in FLASH instead of RAM

#include <EEPROM.h>       // Needed for saving to non-voilatile memory on the Arduino.
#include <DS1307.h>             // DS1307 RTC Clock/Date/Time chip library
#include "wiegand.h"          // Wiegand 26 reader format libary
#include <PCATTACH.h>           // Pcint.h implementation, allows for >2 software interupts.
#include <Adafruit_MCP23017.h>  // Library for the MCP23017 i2c I/O expander
#include <E24C1024.h>           // AT24C i2C EEPOROM library

#define MIN_ADDRESS 0           // For EEPROM
#define MAX_ADDRESS 4096        // 1x32K device

#define EEPROM_ALARM 0                  // EEPROM address to store alarm triggered state between reboots (0..511)
#define EEPROM_ALARMARMED 1             // EEPROM address to store alarm armed state between reboots
#define EEPROM_ALARMZONES 20            // Starting address to store "normal" analog values for alarm zone sensor reads.

#define EEPROM_FIRSTUSER 24
#define EEPROM_LASTUSER 1024
#define NUMUSERS  ((EEPROM_LASTUSER - EEPROM_FIRSTUSER)/5)  //Define number of internal users (200 for UNO/Duemillanova)

// Pin Mappings
#ifdef HWV3STD                          // Use these pinouts for the v3 Standard hardware
#define DOORPIN       6                // Define the pin for electrified door 1 hardware. (MCP)
#define ALARMSTROBEPIN 8                // Define the "non alarm: output pin. Can go to a strobe, small chime, etc. Uses GPB0 (MCP pin 8).
#define ALARMSIRENPIN  9                // Define the alarm siren pin. This should be a LOUD siren for alarm purposes. Uses GPB1 (MCP pin9).
#define READERGRN     10
#define READERBUZ     11
#define RS485ENA        6               // Arduino Pin D6
#define STATUSLED       14              // MCP pin 14
#define RZERO          2
#define RONE           3
#endif

uint8_t readerPins[] = {RZERO, RONE}; // Reader 1 pin definition

const uint8_t analogsensorPins[] = {0, 1, 2, 3}; // Alarm Sensors connected to other analog pins

/* Global Boolean values */
boolean door_locked = true;                       // Keeps track of whether the doors are supposed to be locked right now
boolean door_chime = false;                        // Keep track of when door chime last activated
boolean door_closed = false;                       // Keep track of when door last closed for exit delay
boolean sensor[4] = {false};                      //  Keep track of tripped sensors, do not log again until reset.

/* Global Timers */
unsigned long door_relock_timer = 0;                 // Keep track of when door is supposed to be relocked
unsigned long alarm_delay = 0;                     // Keep track of alarm delay. Used for "delayed activation" or level 2 alarm.
unsigned long alarm_siren_timer=0;                // Keep track of how long alarm has gone off
unsigned long console_fail_timer=0;               // Console password timer for failed logins
unsigned long sensor_delay[2] = {0};             // Used with sensor[] above, but sets a timer for 2 of them. Useful for logging
                                                // motion detector hits for "occupancy check" functions.
                                                
#define numUsers (sizeof(superUserList)/sizeof(long))                  // User access array size (used in later loops/etc)
#define NUMDOORS (sizeof(doorPin)/sizeof(uint8_t))
#define numAlarmPins (sizeof(analogsensorPins)/sizeof(uint8_t))

/* Global RTC clock variables. Can be set using DS1307.getDate function. */
uint8_t second;
uint8_t minute;
uint8_t hour;
uint8_t dayOfWeek;
uint8_t dayOfMonth;
uint8_t month;
uint8_t year;

uint8_t alarm_activated = EEPROM.read(EEPROM_ALARM);                   // Read the last alarm state as saved in eeprom.
uint8_t alarm_armed = EEPROM.read(EEPROM_ALARMARMED);                  // Alarm level variable (0..5, 0==OFF) 

uint8_t consoleFail = 0;                          // Tracks failed console logins for lockout

// Global values for the Wiegand RFID readers
volatile long reader = 0;                      // Reader buffer
long readerdec = 0;                            // Separate value for decoded reader values
volatile int reader_count = 0;                 // Reader received bits counter

// Serial terminal buffer (needs to be global)
char inString[64] = {0};                                         // Size of command buffer (<=128 for Arduino)
uint8_t inCount = 0;
boolean privmodeEnabled = false;                               // Switch for enabling "priveleged" commands

// Create an instance of the various C++ libraries we are using.
DS1307 ds1307;        // RTC Instance
WIEGAND26 wiegand26;  // Wiegand26 (RFID reader serial protocol) library
Adafruit_MCP23017 mcp;
PCATTACH pcattach;    // Software interrupt library

void setup() 
{
  Wire.begin();   // start Wire library as I2C-Bus Master
  mcp.begin();      // use default address 0

  pinMode(2, INPUT);                // Initialize the Arduino built-in pins
  pinMode(3, INPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  mcp.pinMode(DOORPIN, OUTPUT); 
  pinMode(6, OUTPUT);

  for(int i = 0; i <= 15; i++)        // Initialize the I/O expander pins
  {
    mcp.pinMode(i, OUTPUT);
  }

  digitalWrite(RS485ENA, HIGH);           // Set the RS485 chip to HIGH (not asserted)

  // Attach pin change interrupt service routines from the Wiegand RFID readers
  pcattach.PCattachInterrupt(readerPins[0], callReader1Zero, CHANGE); 
  pcattach.PCattachInterrupt(readerPins[1], callReader1One,  CHANGE);  

  // Clear and initialize readers
  wiegand26.initReader(); // Set up Reader 1 and clear buffers.

  mcp.digitalWrite(DOORPIN, LOW); // Sets the relay outputs to LOW (relays off)
  mcp.digitalWrite(ALARMSTROBEPIN, LOW);
  mcp.digitalWrite(ALARMSIRENPIN, LOW);   

  Serial.begin(UBAUDRATE); // Set up Serial output at 8,N,1,UBAUDRATE
  log_reboot();

  /* Set up the MCP23017 IO expander and initialize. */
  mcp.digitalWrite(STATUSLED, LOW);           // Turn the status LED green
}

/* Takes care of re-locking the door as time passes. */
void door_relock_tick()
{
  if(((millis() - door_relock_timer) >= DOORDELAY) && (door_relock_timer != 0))
  { 
    lock_door();
    door_relock_timer = 0;                             
  }
}

/* Checks the reader for data and then acts on it. */
void reader_tick()
{
  long decoded;
  
  if(reader_count >= 26) {                              // When tag presented to reader1 (No keypad on this reader)
    decoded = decode_card(reader);                     // Format the card data (format can be defined in user.h)
    log_tag(decoded);                      // Write log entry to serial port
    chirp_reader(1);
    
    reader = 0;
    reader_count = 0;    
    wiegand26.initReader();                     // Reset for next tag scan
  }
}

void loop()
{                         
  serial_tick();
  door_relock_tick();
  reader_tick();
}

/* Chirp the siren pin or strobe to indicate events. */
void chirp_reader(uint8_t chirps)
{
  for(uint8_t i = 0; i < chirps; i++) {
    mcp.digitalWrite(READERBUZ, HIGH);
    delay(100);
    mcp.digitalWrite(READERBUZ, LOW);
    delay(200);                              
  }
}

void unlock_door_temporarily()
{
  door_relock_timer = millis();  // Set the door to be locked after some time has passed
  unlock_door();
}

/* Send an unlock signal to the door and light the reader LED. */
void unlock_door() 
{ 
  mcp.digitalWrite(DOORPIN, HIGH);
  mcp.digitalWrite(READERGRN, HIGH);
}

/* Send a lock signal to the door and extinguish the reader LED. */
void lock_door() 
{
  mcp.digitalWrite(DOORPIN, LOW);
  mcp.digitalWrite(READERGRN, LOW);
}

void log_reboot() {                                  //Log system startup
  Serial.print("READY\n");
}

void log_tag(long tag) {
  Serial.print("ID\t");
  Serial.print(tag, HEX);
  Serial.print("\n");
}

long decode_card(long input)
{
  if(CARDFORMAT == 0) {
    return(input);
  } else if(CARDFORMAT == 1) {
    bool parityHigh;
    bool parityLow;
    parityLow = bitRead(input,0);
    parityHigh = bitRead(input,26);
    bitWrite(input, 25, 0);        // Set highest (parity bit) to zero
    input = (input >> 1);            // Shift out lowest bit (parity bit)

    return(input);
  }
}

void log_ok()
{
  Serial.print("OK\n");
}

void log_err()
{
  Serial.print("ERR\n");
}

void process_command(char cmd) 
{
  switch(cmd) {
    case 'u':
      unlock_door_temporarily();
      log_ok();
      break;
    default:
      log_err();
      break;
  }
}

/* Honors one-character-then-newline commands like "u\n". */
void serial_tick() 
{                                               
  static char last_ch;
  static char ch;
  
  if (Serial.available()) {                                       
    ch = Serial.read();                                            
    if( ch == '\n' && last_ch != '\n' && last_ch != '\0') {
      process_command(last_ch);
    } else {
      last_ch = ch; 
    }
  }
}                                      

void callReader1Zero(){
  wiegand26.readerZero();
}

void callReader1One(){
  wiegand26.readerOne();
}
