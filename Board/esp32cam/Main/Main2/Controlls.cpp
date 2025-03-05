#include "Controlls.h"
#include <ESP32Servo.h>

Servo myServo;

bool door = false; // false = ปิด, true = เปิด

#define SERVO_PIN 13  

void doorStart(){
  myServo.write(120);
}

void doorClose() {
  if (!door) { 
    Serial.println("Door is already closed.");
  }else{
    for (int pos = 15; pos <= 120; pos += 3) {
      myServo.write(pos);
      delay(57); 
    }
  }
  door = false; 
  Serial.println("Door is Close");
}

void doorOpen() {
  if (door) { 
    Serial.println("Door is already open.");
  }else{
    for (int pos = 120; pos >= 15; pos -= 3) {
      myServo.write(pos);
      delay(57); 
    }
  }

  door = true; 
  Serial.println("Door is Open");
}




void setup_Controlls() {
    myServo.attach(SERVO_PIN);
}

long microsecondsToCentimeters(long microseconds) {
    return microseconds / 29 / 2;
}
