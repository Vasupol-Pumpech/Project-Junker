  #ifndef MQTT_CONFIG_H
#define MQTT_CONFIG_H

#include <WiFiClientSecure.h>
#include <PubSubClient.h>

// ข้อมูล MQTT
extern const char* mqtt_server;
extern const int mqtt_port;
extern const char* mqtt_username;
extern const char* mqtt_password;
extern const char* mqtt_SendReady;
extern const char* mqtt_camera;
extern const char* mqtt_Stuck;

extern bool backdoor;
extern bool start;
// ประกาศฟังก์ชันที่เกี่ยวกับ MQTT
void setup_mqtt();
void reconnectMQTT();
void sendMQTTMessageStr(const char* topic, const char* message); // ส่งข้อความแบบ String
void sendMQTTMessageInt(const char* topic, int message);         // ส่งข้อความแบบ int
extern PubSubClient client;
extern bool dropGrabage;

#endif
