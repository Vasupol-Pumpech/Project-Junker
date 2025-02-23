#ifndef MQTT_CONFIG_H
#define MQTT_CONFIG_H

#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <Preferences.h>
#include <ArduinoJson.h>
#include "Monitor.h"

extern Preferences preferences; 

extern const char* mqtt_server;
extern const int mqtt_port;
extern const char* mqtt_username;
extern const char* mqtt_password;
extern const char* mqtt_topic;
extern const char* mqtt_status;
extern const char* mqtt_binLevel;
extern const char* mqtt_run;
extern const char* mqtt_backdoor;
extern const char* mqtt_start;

void setup_mqtt();
void reconnectMQTT();
void checkReadyTimeout();
void sendMQTTMessageStr(const char* topic, const char* message);
void sendMQTTMessageInt(const char* topic, int message);
void sendBinLevelData(int bin_level_bottle, int bin_level_can, int bin_level_papercup, int bin_level_others);
extern PubSubClient client;
extern String detected;
extern int min_level;
extern int max_level;
extern bool stuck;

#endif
