#include "Arduino.h"
#include "WiFiConfig.h"
#include "MQTTConfig.h"
#include "esp_http_server.h"
#include "Monitor.h"
#include "Controlls.h"
#include <ESP32Servo.h>

#define NotiStuck_PIN 5 // คุมแจ้งเตือน
#define SERVO_PIN 14  // ขาสัญญาณที่ใช้ควบคุมเซอร์โว

Preferences preferences;
Servo myServo;

void start_servo() {
    myServo.attach(SERVO_PIN);
    myServo.write(0);
    Serial.println("Servo Reset to 0 Degrees");
    delay(5000);
}

void dropGabage(){
  myServo.attach(SERVO_PIN);
  myServo.write(180);
  delay(5000);
  myServo.write(0);
  delay(5000);
}

void dropGage_max(){
  myServo.attach(SERVO_PIN);
  myServo.write(50);
  delay(5000);
  myServo.write(0);
  delay(5000);
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("Starting setup...");
    
    myServo.attach(SERVO_PIN);
    start_servo();

    setup_monitor();
    displayText("Connecting to wifi...");
    setup_wifi();
    setup_mqtt();
    reconnectMQTT();
    setup_Controlls();
    
    displayText("Loading Data...");
    
    check_All_Level(); 

    sendMQTTMessageStr(mqtt_start, "start"); 
    displayClear();
    sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
    pinMode(NotiStuck_PIN, OUTPUT);
    digitalWrite(NotiStuck_PIN, HIGH);
    LedOn();
}

void loop() {
    check_wifi();


    if (!client.connected()) {
        reconnectMQTT();
        displayClear();
    }
    client.loop();

    if (stuck == true){
      digitalWrite(NotiStuck_PIN, LOW);
      displayClear();
      displayText("Oject Stuck !!");
      delay(1000);
      displayClear();
      LedOFF();
      return;
    }else{
      digitalWrite(NotiStuck_PIN, HIGH);
      LedOn();
    }
    delay(1000);
    // Serial.println("test penraiwa");
    displayBMP("/bottle2.bmp", 5, 20, bin_level_bottle);
    displayBMP("/can2.bmp", 160, 20, bin_level_can);
    displayBMP("/papercup2.bmp", 5, 150, bin_level_papercup);
    displayBMP("/other2.bmp", 160, 150, bin_level_others);
    
    // //BackDoor();

    if (detected != "none") {
        Serial.print("Detected message: ");
        Serial.println(detected);

        //*******//
        //*ขวดน้ำ*//
        //*******//

        if (detected == "bottle") { 
          if (bin_level_bottle >= max_level) {
            displayClear();
            displayFound("/bottle2.bmp", 40, 80, "Full !!");
            delay(2000);
            dropGage_max();
            check_level();
            bin_level_bottle = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;
            displayClear();
            detected = "none";
            
          } else if (bin_level_bottle >= min_level && bin_level_bottle < max_level) {
            displayClear();
            displayFound("/bottle2.bmp", 40, 80, "Almost full");
            detected = "none";
            moveToTrashType("bottle");
            delay(2000);
            check_level();
            bin_level_bottle = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;
            dropGabage();
            displayClear();
          }else{
            displayClear();
            displayFound("/bottle2.bmp", 40, 80, "BOTTLE");
            detected = "none";
            moveToTrashType("bottle");
            delay(2000);
            check_level();
            bin_level_bottle = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;
            dropGabage();
            displayClear();
          }
            
        //********//
        //*กระป๋อง*//
        //********//

        } else if (detected == "can") {
            if (bin_level_can >= max_level) {
            displayClear();
            displayFound("/can2.bmp", 40, 80, "Full !!");
            delay(2000);
            dropGage_max();
            check_level();
            bin_level_can = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;
            displayClear();
            detected = "none";
          } else if (bin_level_can >= min_level && bin_level_can < max_level) {
            displayClear();
            displayFound("/can2.bmp", 40, 80, "Almost full");
            detected = "none";
            moveToTrashType("can");
            delay(2000);
            check_level();
            bin_level_can = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;
            dropGabage();
            displayClear();
          }else{
            displayClear();
            displayFound("/can2.bmp", 40, 80, "CAN");
            detected = "none";
            moveToTrashType("can");
            delay(2000);
            check_level();
            bin_level_can = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;
            dropGabage();
            displayClear();
          }

        //***********//
        //*แก้วกระดาษ*//
        //***********//

        } else if (detected == "papercup") {
            if (bin_level_papercup >= max_level) {
            displayClear();
            displayFound("/papercup2.bmp", 40, 80, "Full !!");
            delay(2000);
            dropGage_max();
            check_level();
            bin_level_papercup = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;
            displayClear();
            detected = "none";
          } else if (bin_level_papercup >= min_level && bin_level_papercup < max_level) {
            displayClear();
            displayFound("/papercup2.bmp", 40, 80, "Almost full");
            detected = "none";
            moveToTrashType("papercup");
            delay(2000);
            check_level();
            bin_level_papercup = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;
            dropGabage();
            displayClear();
          }else{
            displayClear();
            displayFound("/papercup2.bmp", 40, 80, "PAPPERCUP");
            detected = "none";
            moveToTrashType("papercup");
            delay(2000);
            check_level();
            bin_level_papercup = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0; 
            dropGabage();
            displayClear();
          }
          
        //*******//
        //**อื่นๆ**//
        //*******//

        } else if (detected == "non_object") {
            if (bin_level_others >= max_level) {
            displayClear();
            displayFound("/other2.bmp", 40, 80, "Full !!");
            delay(2000); 
            dropGage_max();
            check_level();
            bin_level_others = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;
            displayClear();
            detected = "none";
          } else if (bin_level_others >= min_level && bin_level_others < max_level) {
            displayClear();
            displayFound("/other2.bmp", 40, 80, "Almost full");
            detected = "none";
            moveToTrashType("non_object");
            delay(2000);
            check_level();
            bin_level_others = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;  
            dropGabage();
            displayClear();
          }else{  
            displayClear();
            displayFound("/other2.bmp", 40, 80, "OTHER");
            detected = "none";
            moveToTrashType("non_object");
            delay(2000);
            check_level();
            bin_level_others = levelValue;
            sendBinLevelData(bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others);
            levelValue = 0;
            dropGabage();
            displayClear(); 
          }
          
            
        }
        
        detected = "none";
        Serial.print("check detect :"+detected);
        delay(3000);
        sendMQTTMessageStr(mqtt_run,"success");
        }
  }

