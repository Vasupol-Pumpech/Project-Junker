#include "MQTTConfig.h"
#include "WiFiConfig.h"
// ข้อมูล MQTT
const char* mqtt_server = "xxx";
const int mqtt_port = 8883;
const char* mqtt_username = "junker";
const char* mqtt_password = "xxx";

const char* mqtt_camera = "junker/1/camera";
const char* mqtt_SendReady = "junker/1/ready";
const char* mqtt_Stuck = "junker/1/stuck";

//sub
const char* mqtt_run = "junker/1/run";
const char* mqtt_backdoor = "junker/1/backdoor";
const char* mqtt_start = "junker/1/start";

bool dropGrabage = false;
bool backdoor = false;
bool start = false;

WiFiClientSecure espClient;
PubSubClient client(espClient);

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (unsigned int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    if (String(topic) == mqtt_run) {
        if (message == "success") {
            Serial.println("Success received!");
            dropGrabage = true;
        }
    }else if(String(topic) == mqtt_backdoor){
      if (message == "open") {
            Serial.println("backdoor received!");
            backdoor = true;
        }
        if (message == "close") {
            Serial.println("backdoor received!");
            backdoor = false;
        }
    }else if (String(topic) == mqtt_start){
      start = true;
    }
}


void setup_mqtt() {
    client.setServer(mqtt_server, mqtt_port);
    client.setKeepAlive(60); 
    espClient.setInsecure();
    client.setCallback(mqtt_callback);
}

void reconnectMQTT() {
    while (!client.connected()) {
        if (WiFi.status() != WL_CONNECTED) {  
            return;
        }

        Serial.print("Connecting to MQTT...");
        if (client.connect("ESP32Client_2", mqtt_username, mqtt_password)) {
            Serial.println("✅ MQTT Connected!");
            client.subscribe(mqtt_backdoor);
            client.subscribe(mqtt_run);
            client.subscribe(mqtt_start);
        } else {
            Serial.print("❌ Failed, rc=");
            Serial.print(client.state());
            Serial.println(" Try again in 5 seconds");
            delay(5000);
        }
    }
}


// ฟังก์ชันสำหรับส่งข้อความแบบ String
void sendMQTTMessageStr(const char* topic, const char* message) {
    if (!client.connected()) {
        reconnectMQTT();
    }
    client.publish(topic, message); // ส่งข้อความ String
}



