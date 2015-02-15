/*
    AT24C.cpp
    AT24Cxxx EEProm Library for Arduino
    Library release: 1.2 rev. c

    This library is free software; you can redistribute it and/or
    modify it under the terms of the Creative Commons GNU license

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the Creative Commons - GNU Public License for more details.
    http://www.creativecommons.org

    This library is part of the hardware project EEProm128, external EEProm
    memory bank for arduino and other kind of microcontroller supporting
    I2C bus.
    The project was initially inspired to AT24C1024B library for Arduino
    with some enhancements.

    You can find more informations, documentations and updates 
    on http://www.contesti.eu (see english language, then projects)

    The main objective of this library is the capability to work with different
    versions of AT24C EEProm models.

    Main enhancements: 
        - manage absolute addressing, up to 8 different devices. This is the maximum
            number of devices that can be pisically addressed on the board Bank.
        - added comments and documentation.
        - added #define customisation for different kind of devices
        
    (c) 2010 Enrico Miglino - enrico.miglino@ovi.com
    contesti.eu electronics
    http://www.contesti.eu/projects/bank
    http://www.contesti.eu/products/products/bank-128
    http://www.contesti.eu/opensource/bank
    
*/

// Library needed include files
#include <Wire.h>
#include "AT24C.h"
#include "AT24C_Hardware.h"

// 1st byte address
#define EEPROM_MIN_ADDRESS 0

// Mandatory: hardare device addressing (first 4 bits)
// This value is fixed for EEProm devices connected
// through I2C bus (B1010xxxx)
#define I2C_DEVICE_BITS   0x500000
// Device select shift bits during addressing calculations
#define DEVICE_SHIFT_BITS       16
// Mask to extract MSB from the calculated address
#define WORD_MASK       0xFFFF

/*
    The following parameter is strictly related to the hardware type.
    When the library decode the physical address (device_number + relative_address)
    the device number is calculated based on the number of storage bytes 
    of every device.
    
    The procedure is as follow:
    
    1) extract the device number and the relative address
    2) build the device address based on the device number
        and the other fixed adressing values (I2C_DEVICE_BITS)
    3) add the relative address to point to the needed byte
        on the phisycal device.
    4) Do the common part of the function (read or write)
        passing data to the wire library to manage I2C bus
    
    Using this method - that seems the fastest between several
    I tested - when the function identify the physical device
    recalculate the address as is is member of a 1024 bits chipset.
    
    In next revisions there is the first part of the function (working
    on the device's absolute address that can be simplified).
    
    Note on precompile pragmas
        The device type is #define(d) in AT24C_Hardware.h that don't need
        to be included in the sketch. Using this method you are sure that
        the library works addressing bytes correctly, but has the limitation
        that it suppose that you use only one device type in all your development
        process. If you work with the sam IDE with two board using
        i.e. two AT24C128 in one hardware and fou AT24C256 in another,
        you must change the define in before every compilation or move the file
        in your sketch directory (rename the original in the library !!!)
        so in every sketch you can change the value depending by the hardware
        you are connecting to your Ardino board.
*/

// Check for the kind of device we are using
// Default __AT24C1024__ DON'T use CHIP_ADDRESS
// but must be defined when no other devices are used
// (see below)
#ifdef __AT24C128__
    #define CHIP_ADDRESS            16384       // Max num of storage addresses on device
#endif

#ifdef __AT24C256__
    #define CHIP_ADDRESS            32768       // Max num of storage addresses on device
#endif

AT24C::AT24C(void)
{
   Wire.begin();
}

// To speed preprocessing and simplify the code readability, here we check
// only if the user has pre-defined a device different from the default.
// Is so, the calculation between #ifdef ... #endif is the same but
// the calue of CHIP_ADDRESS canges because it is device-dependent.
void AT24C::write(unsigned long dataAddress, uint8_t data)
{
#ifndef __AT24C1024__
    uint8_t deviceAddress = (uint8_t)(dataAddress / CHIP_ADDRESS);      // obtain the device number
    uint8_t absoluteDataAddress = (uint8_t)(dataAddress - (deviceAddress * CHIP_ADDRESS));                      // Calculate internal byte address

    // Recalculate the address as the byte address is the deviceAddress device + data addressed
    // where the device is a 1024 bits.
    deviceAddress = deviceAddress | 50;
    dataAddress = (unsigned long)((deviceAddress << 16) | absoluteDataAddress);
#endif
   Wire.beginTransmission((uint8_t)((I2C_DEVICE_BITS | dataAddress) >> DEVICE_SHIFT_BITS));
   Wire.send((uint8_t)((dataAddress & WORD_MASK) >> 8)); // MSB
   Wire.send((uint8_t)(dataAddress & 0xFF)); // LSB
   Wire.send(data);
   Wire.endTransmission();
   delay(5);
}

uint8_t AT24C::read(unsigned long dataAddress)
{
    uint8_t data = 0x00;
#ifndef __AT24C1024__
    uint8_t deviceAddress = (uint8_t)(dataAddress / CHIP_ADDRESS);      // obtain the device number
    uint8_t absoluteDataAddress = (uint8_t)(dataAddress - (deviceAddress * CHIP_ADDRESS));                      // Calculate internal byte address

    // Recalculate the address as the byte address is the deviceAddress device + data addressed
    // where the device is a 1024 bits.
    deviceAddress = deviceAddress | 50;
    dataAddress = (unsigned long)((deviceAddress << 16) | absoluteDataAddress);
#endif
    Wire.beginTransmission((uint8_t)((I2C_DEVICE_BITS | dataAddress) >> DEVICE_SHIFT_BITS));
   Wire.send((uint8_t)((dataAddress & WORD_MASK) >> 8)); // MSB
   Wire.send((uint8_t)(dataAddress & 0xFF)); // LSB
   Wire.endTransmission();
   Wire.requestFrom(0x50,1);
   if (Wire.available()) data = Wire.receive();
   return data;
}

AT24C EEPromBank;
