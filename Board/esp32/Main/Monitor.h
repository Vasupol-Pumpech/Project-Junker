#ifndef MONITOR_H
#define MONITOR_H

#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>
#include <FS.h>
#include <SPIFFS.h>

void setup_monitor();
void displayBMP(const char *filename, int x, int y, int iconNumber);
void displayFound(const char *filename, int x, int y, const char *labelText);
void displayText(const char *textdisplay);
void displayLongInt(long int value);
void displayClear();


#endif
