#ifndef CONTROLLS_H
#define CONTROLLS_H
#include "Arduino.h"
#include <ESP32Servo.h>

extern long levelValue;
extern int bin_level_bottle;   
extern int bin_level_can;       
extern int bin_level_papercup;  
extern int bin_level_others; 
extern int backdoor;

void setup_Controlls();
void check_level();
void check_All_Level();
void BackDoor();
void LedOn();
void LedOFF();
void moveToTrashType(String detected);
void stopMotor();
void GreenOn();
void GreenOFF();

#endif