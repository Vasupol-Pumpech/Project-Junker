#ifndef CONTROLLS_H
#define CONTROLLS_H
#include "Arduino.h"
#include <ESP32Servo.h>

extern bool objectDetected;

void setup_Controlls();
void doorClose();
void doorOpen();
void doorStart();
long microsecondsToCentimeters(long microseconds);


#endif