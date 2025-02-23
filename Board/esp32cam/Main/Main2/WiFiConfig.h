#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#include <WiFi.h>
#include <esp_now.h>
#include <Preferences.h>
#include <esp_wifi.h>

void setup_wifi();
void resetESPNow();

#endif
