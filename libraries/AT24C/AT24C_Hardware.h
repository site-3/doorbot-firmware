/*
    AT24C_Hardware.h
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

// EEPRom Bank definitions (mandatory)
// The following definition change some library parameters, so need be set
// BEFORE the library include.
// Select one (depends by your hardware)
// Note that you must select the corresponding device storage size, 
// regardless if you are sing AT24Cxx chip or LC24xxx.

//#define __AT24C1024__     // 128k device
//#define __AT24C128__      // 16k device
#define __AT24C256__        // 32K device