#include "wiegand.h"

extern byte readerPins[];          // Reader 1 connected to pins 4,5
extern long reader;
extern int  reader_count;

WIEGAND26::WIEGAND26(){
}

WIEGAND26::~WIEGAND26(){
}

void WIEGAND26::initReader(void) {
  for(byte i=0; i<2; i++){
    pinMode(readerPins[i], OUTPUT);
    digitalWrite(readerPins[i], HIGH); // enable internal pull up causing a one
    digitalWrite(readerPins[i], LOW); // disable internal pull up causing zero and thus an interrupt
    pinMode(readerPins[i], INPUT);
    digitalWrite(readerPins[i], HIGH); // enable internal pull up
  }
  delay(10);
  reader_count=0;
  reader=0;
}

void  WIEGAND26::readerOne() {
  if(digitalRead(readerPins[1]) == LOW){
    reader_count++;
    reader = reader << 1;
    reader |= 1;
  }
}

void  WIEGAND26::readerZero() {
  if(digitalRead(readerPins[0]) == LOW){
    reader_count++;
    reader = reader << 1;   
  }
}
