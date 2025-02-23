#include "Controlls.h"
#include <ESP32Servo.h>

Servo myServo;

   
#define SERVO_PIN 13  


void doorClose() {
  myServo.write(120);
  Serial.println("Door is Close");
}

void doorOpen() {
  myServo.write(15);
  Serial.println("Door is Open");
}

void setup_Controlls() {
    myServo.attach(SERVO_PIN);
}

long microsecondsToCentimeters(long microseconds) {
    return microseconds / 29 / 2;
}
