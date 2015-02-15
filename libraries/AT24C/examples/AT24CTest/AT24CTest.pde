/*
  AT24C.pde
  AT24C EEPROM Test 
  
*/
#include <Arduino.h>
#include <Wire.h>

// ------------------------ IMPORTANT !!! ------------------------
// EEPRom Bank definitions (mandatory)
// The following definition change some library parameters, so need be set
// BEFORE the library include.
// Select one (depends by your hardware) in file AT24C_Hardware.h
// #define __AT24C1024__   // 128k device, max 4 units per I2C bus (512k max addresses)
// #define __AT24C128__    // 16k device, max 8 units per I2C bus (128k max addresses)
// Note: Correctly define AT24C_MAX_ADDRESS with the real phisycal addressable
// byte depending on your hardware configuration. For more informations, read the
// documentation files.
// ------------------------ IMPORTANT !!! ------------------------

#include <WProgram.h>
#include <Wire.h>
#include <AT24C.h>
#define AT24C_MIN_ADDRESS    0      // Lowest physical addressable byte
#define AT24C_MAX_ADDRESS    32768  // Highest physical addressable byte

#define WRITE_DOT  1000

unsigned long time;
unsigned long finishTime;
unsigned long errors = 0;
unsigned long address = 0;

byte loop_size;

void setup()
{
  // Make sure we aren't reading old data
  randomSeed(analogRead(0));
  loop_size = random(1, 100);
  Serial.begin(115200);
  Serial.println();
  Serial.println("AT24C Library Test");
  Serial.println();
  writeByByteTest();
  readByByteTest();
}

void loop()
{
}

void writeByByteTest()
{
  time = millis();
  errors = 0;
  Serial.println("--------------------------------");
  Serial.println("Write By Byte Test:");
  Serial.println();
  Serial.print("Writing data:");
  for (address = AT24C_MIN_ADDRESS; address < AT24C_MAX_ADDRESS; address++)
  {
    EEPromBank.write(address, (uint8_t)(address % loop_size));
    if (!(address % WRITE_DOT)) Serial.print(".");
  }
  finishTime = millis() - time;
  Serial.println("DONE");
  Serial.print("Total Time (seconds): "); 
  Serial.println((unsigned long)(finishTime / 1000));
  Serial.print("Write operations per second: "); 
  Serial.println((unsigned long)(AT24C_MAX_ADDRESS / (finishTime / 1000))); 
  Serial.println("--------------------------------");   
  Serial.println();
}

void readByByteTest()
{
  time = millis();
  errors = 0;
  Serial.println("--------------------------------");
  Serial.println("Read By Byte Test:");
  Serial.println();
  Serial.print("Reading data:");
  for (address = AT24C_MIN_ADDRESS; address < AT24C_MAX_ADDRESS; address++)
  {
    uint8_t data;
    data = EEPromBank.read(address);
    if (data != (uint8_t)(address % loop_size)) 
    {
      Serial.println();
      Serial.print("Address: ");
      Serial.print(address);
      Serial.print(" Should be: ");
      Serial.print((uint8_t)(address % loop_size), DEC);
      Serial.print(" Read val: ");
      Serial.println(data, DEC);
      errors++;
    }
    if (!(address % WRITE_DOT)) Serial.print(".");
  }
  finishTime = millis() - time;
  Serial.println("DONE");
  Serial.println();
  Serial.print("Total Test Time (secs): "); 
  Serial.println((unsigned long)(finishTime / 1000));
  Serial.print("Read operations per second: "); 
  Serial.println((unsigned long)(AT24C_MAX_ADDRESS / (finishTime / 1000))); 
  Serial.print("Total errors: "); 
  Serial.println(errors);   
  Serial.println("--------------------------------");
  Serial.println();
}
