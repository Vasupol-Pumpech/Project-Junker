#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#include <WiFi.h>
#include <WiFiManager.h>


void setup_wifi();
void check_wifi();
void sendWiFiCredentials();
void setup_espnow();
#endif
