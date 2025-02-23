#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>
#include <FS.h>
#include <SPIFFS.h>

// Define TFT pins
#define TFT_CS    15
#define TFT_RST   4
#define TFT_DC    2

// Create an object for the ST7789 display
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

// Icon dimensions for scaling
#define ICON_WIDTH_ORIGINAL  40
#define ICON_HEIGHT_ORIGINAL 40
#define ICON_WIDTH_SCALED    70
#define ICON_HEIGHT_SCALED   70
static int TextLayer = 0; 

void setup_monitor() {

  if (!SPIFFS.begin(true)) {
    Serial.println("Failed to initialize SPIFFS");
    return;
  }

  tft.init(240, 320); 
  tft.fillScreen(ST77XX_WHITE);
  tft.setTextColor(ST77XX_BLACK);
  //tft.setTextSize(3);
  tft.setRotation(1);

  Serial.println("Monitor started");
}

void displayClear(){
  tft.fillScreen(ST77XX_WHITE);
  TextLayer = 0;
}

void displayLongInt(long int value) {
    tft.setTextSize(2);  // ปรับขนาดตัวอักษร
    tft.setTextColor(ST77XX_BLACK);  // ตั้งค่าสีของข้อความ
    tft.setCursor(10, 30);  // กำหนดตำแหน่งแสดงผล
    tft.print(value);  // แสดงค่า long int บนจอ
}


void displayText(const char *textdisplay) {

    tft.setTextSize(2);
    if (TextLayer == 0) {
        tft.setCursor(10, 30); 
        tft.print(textdisplay); 
        TextLayer += 1;
        delay(100);
    } else if (TextLayer == 1) {
        tft.setCursor(10, 70); 
        tft.print(textdisplay); 
        TextLayer += 1;
        delay(100);
    } else if (TextLayer == 2) {
        tft.setCursor(10, 110);
        tft.print(textdisplay); 
        TextLayer += 1;
        delay(100);
    } else if (TextLayer == 3) {
        tft.setCursor(10, 150);
        tft.print(textdisplay); 
        TextLayer += 1;
        delay(100);
    } else {
        tft.fillScreen(ST77XX_WHITE); 
        TextLayer = 0; 
        tft.setCursor(10, 30); 
        tft.print(textdisplay); 
        TextLayer += 1;
        delay(100);
    }
}



void displayBMP(const char *filename, int x, int y, int iconNumber) {
  tft.setTextSize(3);
  File file = SPIFFS.open(filename, "r");
  if (!file) {
    Serial.println("Failed to open BMP file");
    return;
  }

  uint8_t header[54];
  file.read(header, 54); // Read BMP header

  // Check BMP signature
  if (header[0] != 'B' || header[1] != 'M') {
    Serial.println("Not a valid BMP file");
    file.close();
    return;
  }

  // Extract width and height from BMP header
  int32_t width = *(int32_t *)&header[18];
  int32_t height = *(int32_t *)&header[22];

  // Ensure BMP dimensions match expected size
  if (width != ICON_WIDTH_ORIGINAL || height != ICON_HEIGHT_ORIGINAL) {
    Serial.println("BMP dimensions do not match expected size");
    file.close();
    return;
  }

  // Skip to pixel data
  uint32_t pixelDataOffset = *(uint32_t *)&header[10];
  file.seek(pixelDataOffset);

  uint16_t color;
  float scaleX = (float)ICON_WIDTH_SCALED / ICON_WIDTH_ORIGINAL;
  float scaleY = (float)ICON_HEIGHT_SCALED / ICON_HEIGHT_ORIGINAL;

  for (int16_t row = 0; row < ICON_HEIGHT_ORIGINAL; row++) {
    for (int16_t col = 0; col < ICON_WIDTH_ORIGINAL; col++) {
      uint8_t b = file.read();
      uint8_t g = file.read();
      uint8_t r = file.read();

      // Convert RGB to 16-bit color
      color = tft.color565(r, g, b);

      // Adjust row for flipped display
      int adjustedRow = ICON_HEIGHT_ORIGINAL - 1 - row;

      // Scale pixels to new dimensions
      int scaledXStart = x + (int)(col * scaleX);
      int scaledXEnd = x + (int)((col + 1) * scaleX);
      int scaledYStart = y + (int)(adjustedRow * scaleY);
      int scaledYEnd = y + (int)((adjustedRow + 1) * scaleY);

      // Fill scaled area with the color
      for (int sx = scaledXStart; sx < scaledXEnd; sx++) {
        for (int sy = scaledYStart; sy < scaledYEnd; sy++) {
          tft.drawPixel(sx, sy, color);
        }
      }
    }
  }

  file.close();

  // Display percentage text next to the icon
  tft.setCursor(x + ICON_WIDTH_SCALED + 5, y + ICON_HEIGHT_SCALED / 2 - 8);
  tft.print(String(iconNumber) + "%");
}

void displayFound(const char *filename, int x, int y, const char *labelText) {
  tft.setTextSize(3);
  File file = SPIFFS.open(filename, "r");
  if (!file) {
    Serial.println("Failed to open BMP file");
    return;
  }

  uint8_t header[54];
  file.read(header, 54); // Read BMP header

  // Check BMP signature
  if (header[0] != 'B' || header[1] != 'M') {
    Serial.println("Not a valid BMP file");
    file.close();
    return;
  }

  // Extract width and height from BMP header
  int32_t width = *(int32_t *)&header[18];
  int32_t height = *(int32_t *)&header[22];

  // Ensure BMP dimensions match expected size
  if (width != ICON_WIDTH_ORIGINAL || height != ICON_HEIGHT_ORIGINAL) {
    Serial.println("BMP dimensions do not match expected size");
    file.close();
    return;
  }

  // Skip to pixel data
  uint32_t pixelDataOffset = *(uint32_t *)&header[10];
  file.seek(pixelDataOffset);

  uint16_t color;
  float scaleX = (float)ICON_WIDTH_SCALED / ICON_WIDTH_ORIGINAL;
  float scaleY = (float)ICON_HEIGHT_SCALED / ICON_HEIGHT_ORIGINAL;

  for (int16_t row = 0; row < ICON_HEIGHT_ORIGINAL; row++) {
    for (int16_t col = 0; col < ICON_WIDTH_ORIGINAL; col++) {
      uint8_t b = file.read();
      uint8_t g = file.read();
      uint8_t r = file.read();

      // Convert RGB to 16-bit color
      color = tft.color565(r, g, b);

      // Adjust row for flipped display
      int adjustedRow = ICON_HEIGHT_ORIGINAL - 1 - row;

      // Scale pixels to new dimensions
      int scaledXStart = x + (int)(col * scaleX);
      int scaledXEnd = x + (int)((col + 1) * scaleX);
      int scaledYStart = y + (int)(adjustedRow * scaleY);
      int scaledYEnd = y + (int)((adjustedRow + 1) * scaleY);

      // Fill scaled area with the color
      for (int sx = scaledXStart; sx < scaledXEnd; sx++) {
        for (int sy = scaledYStart; sy < scaledYEnd; sy++) {
          tft.drawPixel(sx, sy, color);
        }
      }
    }
  }

  file.close();

  // Display percentage text next to the icon
  tft.setCursor(x + ICON_WIDTH_SCALED + 5, y + ICON_HEIGHT_SCALED / 2 - 8);
  tft.print(String(labelText));
}



