#include "Controlls.h"
#include "Monitor.h"
#include "MQTTConfig.h"
#include <Arduino.h>


#define LED 17 
#define MOTOR_IN1 27  // ควบคุมทิศทาง 
#define MOTOR_IN2 16  // ตั้ง LOW ตลอด 

#define LIMIT_BOTTLE  32   // Limit Switch ตำแหน่ง 0° (Bottle)
#define LIMIT_CAN 33       // Limit Switch ตำแหน่ง 90° (Can)
#define LIMIT_PAPERCUP 25  // Limit Switch ตำแหน่ง 180° (Paper Cup)
#define LIMIT_OTHER 26   // Limit Switch ตำแหน่ง 270° (Other)

#define LIMIT_STOP 19   // Limit Stop ของ backdoor open

#define pingPin 22 // ขา Trigger
#define inPin  21   // ขา Echo

long duration, cm, levelValue;
int currentPosition = 1;

int bin_level_bottle = 0;   
int bin_level_can = 0;       
int bin_level_papercup = 0;  
int bin_level_others = 0;    

bool backdoor = false;
bool backdoor_state = false;

int SENSOR_OFFSET = 1;  
int TANK_MAX = 44;     


void setup_Controlls() {
  pinMode(LED, OUTPUT);
  LedOFF();
  pinMode(pingPin, OUTPUT);
  pinMode(inPin, INPUT);
  
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  
  digitalWrite(MOTOR_IN2, LOW);  
  
  pinMode(LIMIT_BOTTLE, INPUT_PULLUP);
  pinMode(LIMIT_CAN, INPUT_PULLUP);
  pinMode(LIMIT_PAPERCUP, INPUT_PULLUP);
  pinMode(LIMIT_OTHER, INPUT_PULLUP);
  pinMode(LIMIT_STOP, INPUT_PULLUP);
  
  stopMotor();  // ให้มอเตอร์หยุดเมื่อเริ่มต้น
}


void LedOn(){
  digitalWrite(LED, LOW);
}

void LedOFF(){
  digitalWrite(LED, HIGH);
}


void moveMotor() {
    // pinMode(MOTOR_PWM, OUTPUT);
    pinMode(MOTOR_IN1, OUTPUT);
    pinMode(MOTOR_IN2, OUTPUT);

    digitalWrite(MOTOR_IN1, HIGH);
    digitalWrite(MOTOR_IN2, LOW);
    // analogWrite(MOTOR_PWM, 255);  
}

void stopMotor() {
    // pinMode(MOTOR_PWM, OUTPUT);
    pinMode(MOTOR_IN1, OUTPUT);
    pinMode(MOTOR_IN2, OUTPUT);
    
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);
    // analogWrite(MOTOR_PWM, 0);
}

long microsecondsToCentimeters(long microseconds) {
    return microseconds / 29 / 2;
}

void BackDoor() {
  bool limit_state = digitalRead(LIMIT_STOP);

  if (limit_state == LOW && backdoor_state) {  
    // เมื่อกดสวิตช์ถูกกด
    backdoor = false;
    Serial.println("BackDoor Close");
    sendMQTTMessageStr(mqtt_backdoor, "close");
    backdoor_state = false; 
  } 
  else if (limit_state == HIGH && !backdoor_state) {  
    // เมื่อกดสวิตช์ไม่ถูกกด
    backdoor = true;
    Serial.println("BackDoor Open");
    sendMQTTMessageStr(mqtt_backdoor, "open");
    backdoor_state = true; 
  }
}



void moveToTrashType(String detected) {
  int targetPosition;

  if (detected == "bottle") { 
    targetPosition = 0;
  } else if (detected == "can") {
    targetPosition = 90;
  } else if (detected == "papercup") {
    targetPosition = 180;
  } else if (detected == "non_object") {
    targetPosition = 270;
  } else {
    Serial.println("Invalid trash type!");
    return; 
  }

  Serial.print("Moving to ");
  Serial.println(detected);

  moveMotor();

  unsigned long startTime = millis(); 
  while (true) {

    Serial.print("wait : ");
    Serial.println(detected);

    client.loop();

    if (targetPosition == 0 && digitalRead(LIMIT_BOTTLE) == LOW) break;
    if (targetPosition == 90 && digitalRead(LIMIT_CAN) == LOW) break;
    if (targetPosition == 180 && digitalRead(LIMIT_PAPERCUP) == LOW) break;
    if (targetPosition == 270 && digitalRead(LIMIT_OTHER) == LOW) break;

    if (millis() - startTime > 60000) {
        break;
    }

    delay(500); 
}
  startTime = 0;
  stopMotor();  
  currentPosition = targetPosition;
  Serial.print("Reached Position: ");
  Serial.println(currentPosition);
}

void check_level(){
    pinMode(pingPin, OUTPUT);
    pinMode(inPin, INPUT);
    digitalWrite(pingPin, LOW);
    delayMicroseconds(2);
    digitalWrite(pingPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(pingPin, LOW);

    duration = pulseIn(inPin, HIGH);
    cm = microsecondsToCentimeters(duration);
    if (cm > 44) {
        cm = 44;
    }
    levelValue = map(cm, 0, 44, 100, 0);
}


void check_All_Level() {
    moveToTrashType("bottle");
    delay(3000);
    check_level();
    bin_level_bottle = levelValue; 
    levelValue = 0;
    
    moveToTrashType("can");
    delay(3000);
    check_level();
    bin_level_can = levelValue; 
    levelValue = 0;
    
    moveToTrashType("papercup");
    delay(3000);
    check_level();
    bin_level_papercup = levelValue; 
    levelValue = 0;
    
    moveToTrashType("non_object");
    delay(3000);
    check_level();
    bin_level_others = levelValue; 
    levelValue = 0;

    displayClear();
}


