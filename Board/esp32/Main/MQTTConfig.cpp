#include "MQTTConfig.h"
#include "Controlls.h"

// ข้อมูล MQTT
const char* mqtt_server = "71df9698816a4b6ea2e24e7b6e73ac93.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_username = "junker";
const char* mqtt_password = "Bb54658668";

// public
const char* mqtt_status = "junker/1/online";
const char* mqtt_binLevel = "junker/1/binLevel";
const char* mqtt_run = "junker/1/run";
const char* mqtt_backdoor = "junker/1/backdoor";
const char* mqtt_start = "junker/1/start";

// subscribe
const char* mqtt_detected = "junker/1/detected";
const char* mqtt_Setlevel = "junker/1/level";
const char* mqtt_SendReady = "junker/1/ready";
const char* mqtt_Stuck = "junker/1/stuck";

String detected = "none";
bool ready = false;
bool stuck = false;
WiFiClientSecure espClient;
PubSubClient client(espClient);

int min_level;
int max_level;

bool readyReceived = false;
unsigned long lastReadyTime = 0;
const unsigned long readyTimeout = 30000;

// ฟังก์ชัน callback สำหรับจัดการข้อความที่ได้รับจาก MQTT
void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }

    if (String(topic) == mqtt_detected) {
        detected = message;
    } else if (String(topic) == mqtt_Setlevel) {
        // สร้าง JSON Document เพื่อแยกข้อมูล
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, message);

        if (error) {
            Serial.println("Failed to parse JSON payload");
            return;
        }

        // ดึงค่า full_threshold และ alert_threshold จาก JSON
        int new_full_threshold = doc["full_threshold"];
        int new_alert_threshold = doc["alert_threshold"];

        if (new_alert_threshold < new_full_threshold - 10 && 
            new_full_threshold >= 0 && new_full_threshold <= 100 &&
            new_alert_threshold >= 0 && new_alert_threshold <= 100) {
            
            min_level = new_alert_threshold; 
            max_level = new_full_threshold; 

            // บันทึกค่าใน Preferences
            preferences.begin("bin-level", false);  //false = r/w  true = r
            preferences.putInt("min_level", min_level);
            preferences.putInt("max_level", max_level);
            preferences.end();

            Serial.println("Updated min and max levels:");
            Serial.println("Min Level (alert_threshold): " + String(min_level));
            Serial.println("Max Level (full_threshold): " + String(max_level));
        } else {
            Serial.println("Invalid thresholds received.");
        }
    } else if (String(topic) == mqtt_SendReady){
      sendMQTTMessageStr(mqtt_status,"Online");
      ready = true;
      readyReceived = true;
      lastReadyTime = millis();
      GreenOn();
      
    } else if (String(topic) == mqtt_Stuck){
      String payloadStr = String((char*)payload);
        if (payloadStr == "stuck") {
          Serial.println("Object Stuck Detected!");
          stuck = true;
          GreenOFF();
      } else if (payloadStr == "unstuck"){
        stuck = false;
        GreenOn();
      }
    }

}

void checkReadyTimeout() {
    if (readyReceived && millis() - lastReadyTime > readyTimeout) {
        GreenOFF();
        readyReceived = false;
    }
}

void setup_mqtt() {
    client.setServer(mqtt_server, mqtt_port);
    client.setKeepAlive(60);
    client.setCallback(mqttCallback); 
    espClient.setInsecure();

    preferences.begin("bin-level", true);
    min_level = preferences.getInt("min_level", 60); 
    max_level = preferences.getInt("max_level", 90); 
    preferences.end();

    Serial.println("Loaded min and max levels from storage:");
    Serial.println("Min Level: " + String(min_level));
    Serial.println("Max Level: " + String(max_level));
}


void reconnectMQTT() {
    int count_try = 0;

    while (!client.connected()) {
        displayClear();
        Serial.println("Connecting to MQTT...");
        displayText("Connecting to MQTT...");
        if (client.connect("ESP32Client_1", mqtt_username, mqtt_password)) {
            Serial.println("MQTT connected");
            displayText("MQTT connected");
            client.subscribe(mqtt_detected);
            client.subscribe(mqtt_Setlevel);
            client.subscribe(mqtt_SendReady);
            client.subscribe(mqtt_Stuck);
            Serial.println("Subscribed to topics:");
            Serial.println(String(mqtt_detected));
            Serial.println(String(mqtt_Setlevel));
            Serial.println(String(mqtt_SendReady));
        } else {
            Serial.print("MQTT connection failed, state: ");
            Serial.println(client.state());
            delay(5000);
            count_try ++;
            if (count_try == 5){
              displayText("Can't Conneting to MQTT");
              displayText("Restarting...");
              delay(5000);
              ESP.restart();
            }
        }
    }
}

// ฟังก์ชันสำหรับส่งข้อความแบบ String
void sendMQTTMessageStr(const char* topic, const char* message) {
    if (!client.connected()) {
        reconnectMQTT();
    }
    client.publish(topic, message);
}

// ฟังก์ชันสำหรับส่งข้อความแบบ int
void sendMQTTMessageInt(const char* topic, int message) {
    if (!client.connected()) {
        reconnectMQTT();
    }
    char messageBuffer[10];
    sprintf(messageBuffer, "%d", message); 
    client.publish(topic, messageBuffer);
}

// ฟังก์ชันส่งข้อมูล binLevel ที่มีหลายค่า
void sendBinLevelData(int bin_level_bottle, int bin_level_can, int bin_level_papercup, int bin_level_others) {
    if (!client.connected()) {
        reconnectMQTT();
    }

    // สร้าง JSON string สำหรับส่งข้อมูล
    String jsonMessage = "{\"bin_level_bottle\": " + String(bin_level_bottle) +
                         ", \"bin_level_can\": " + String(bin_level_can) +
                         ", \"bin_level_papercup\": " + String(bin_level_papercup) +
                         ", \"bin_level_others\": " + String(bin_level_others) + "}";

    client.publish(mqtt_binLevel, jsonMessage.c_str());
}
