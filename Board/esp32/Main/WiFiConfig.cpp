#include "WiFiConfig.h"
#include <WiFiManager.h>
#include "Monitor.h"
#include <esp_now.h>
#include <string.h>

WiFiManager wm;
uint8_t receiverMacAddress[] = {0x7C, 0x87, 0xCE, 0x31, 0xC0, 0x3C};
volatile bool sendWiFiSuccess = false;

typedef struct {
    char ssid[32];
    char password[32];
} WiFiCredentials;

WiFiCredentials wifiData;

// ฟังก์ชัน callback เมื่อส่งข้อมูล ESP-NOW
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print("Send Status: ");
    if (status == ESP_NOW_SEND_SUCCESS) {
        Serial.println("Success");
        sendWiFiSuccess = true;  // อัปเดตให้รู้ว่าส่งสำเร็จ
    } else {
        Serial.println("Fail");
        sendWiFiSuccess = false; // อัปเดตให้รู้ว่าส่งล้มเหลว
    }
}

void sendWiFiCredentials() {
    strcpy(wifiData.ssid, WiFi.SSID().c_str());
    strcpy(wifiData.password, WiFi.psk().c_str());

    Serial.print("Sending SSID: ");
    Serial.println(wifiData.ssid);
    Serial.print("Sending PASS: ");
    Serial.println(wifiData.password);

    displayText("Camera WiFi connect...");
    // while (!sendWiFiSuccess) {  //ส่งซ้ำจนกว่า Send Status จะเป็น Success
    //     esp_err_t result = esp_now_send(receiverMacAddress, (uint8_t *)&wifiData, sizeof(wifiData));

    //     if (result == ESP_OK) {
    //         Serial.println("ESP-NOW Data Sent (Waiting for Success Status)...");
    //     } else {
    //         Serial.println("ESP-NOW Send Failed, Retrying...");
    //     }

    //     delay(2000);  // หน่วงเวลา 2 วินาทีก่อนลองใหม่
    // }

    Serial.println("WiFi Credentials Sent Successfully with ESP-NOW!");
}

// ฟังก์ชันแสดงข้อมูล WiFi ที่เชื่อมต่ออยู่
void printWiFiInfo() {
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n==== WiFi Information ====");
        Serial.print("SSID: ");
        Serial.println(WiFi.SSID());
        
        String SSID = "Wifi Connected: " + WiFi.SSID();

        Serial.print("Password: ");
        Serial.println(WiFi.psk());

        Serial.print("Local IP: ");
        Serial.println(WiFi.localIP());

        Serial.println("==========================");
    } else {
        Serial.println("WiFi ยังไม่เชื่อมต่อ!");
    }
}

// ตั้งค่า ESP-NOW และเพิ่ม Peer
void setup_espnow() {

  // กำหนดให้ ESP-NOW ใช้ Channel 6 ตลอดเวลา
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_channel(6, WIFI_SECOND_CHAN_NONE);
    esp_wifi_set_promiscuous(false);

    Serial.print("ESP-NOW Locked to WiFi Channel: ");
    Serial.println(WiFi.channel());

    if (esp_now_init() != ESP_OK) {
        Serial.println("ESP-NOW Initialization Failed! Restarting...");
        displayText("Connect Camera fail");
        displayText("Restarting...");
        delay(5000);
        ESP.restart();
    }

    esp_now_register_send_cb(OnDataSent);

    // เพิ่ม Peer ให้แน่ใจว่า ESP-NOW พร้อมส่งข้อมูล
    esp_now_peer_info_t peerInfo;
    memset(&peerInfo, 0, sizeof(peerInfo));
    memcpy(peerInfo.peer_addr, receiverMacAddress, 6);
    peerInfo.channel = 0;  // ใช้ช่อง 0
    peerInfo.encrypt = false; 

    Serial.print("Adding Peer: ");
    for (int i = 0; i < 6; i++) {
        Serial.printf("%02X", receiverMacAddress[i]);
        if (i < 5) Serial.print(":");
    }
    Serial.println();

    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("Failed to add peer! Restarting...");
        delay(3000);
        ESP.restart();
    }

    Serial.println("ESP-NOW Initialized and Peer Added Successfully!");
}



void setup_wifi() {
    WiFi.mode(WIFI_AP_STA);

    // ตั้งค่าให้รอเชื่อมต่อ WiFi ไม่เกิน 15 วินาที
    wm.setConnectTimeout(15);  
    wm.setConfigPortalTimeout(120);  
    wm.setBreakAfterConfig(true); // ออกจากโหมด Config ถ้าเชื่อมต่อไม่ได้

    // กำหนด Custom HTML/CSS + JavaScript
    wm.setCustomHeadElement(R"rawliteral(
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background-color: #f5f5f5; }
            h3 { color: #319708; text-align: center; }
            input, button { font-size: 16px; padding: 10px; margin: 5px; }
            .msg { display: none; }
            h1 { text-align: center; }
        </style>
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                if (window.location.pathname.includes("wifisave")) {
                    setTimeout(function() {
                        alert("WiFi บันทึกสำเร็จ! กรุณาตรวจสอบผลลัพธ์บนจอแสดงผล");
                    }, 500); // เพิ่ม delay สักนิดเพื่อให้โหลดเสร็จก่อน
                }
            });
        </script>
    )rawliteral");

    // ตั้งค่าเมนู
    std::vector<const char*> menuItems = {"wifi"};  
    wm.setMenu(menuItems);

    wm.setAPCallback([](WiFiManager* myWiFiManager) {
        Serial.println("WiFiManager เข้า AP Mode: Junker-Camera");
        Serial.print("กรุณาเข้าไปที่: http://");
        Serial.println(WiFi.softAPIP().toString() + "/wifi"); 
    });

    Serial.println("กำลังเปิด AP Mode...");
    displayText("WiFi Name : Junker");
    delay(1000);
    displayText("Wait config WiFi");
    

    bool wifiConnected = wm.autoConnect("Junker", "12345678");

    if (!wifiConnected || WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi เชื่อมต่อไม่สำเร็จ! กรุณากรอกรหัสใหม่...");
        displayClear();
        displayText("WiFi Connect Failed!");
        displayText("Check & Retry");

        wm.resetSettings();
        delay(3000);
        
        Serial.println("Restarting ESP...");
        ESP.restart();
    }

    Serial.println("WiFi เชื่อมต่อสำเร็จ!");
    displayText("WiFi Connected");
    delay(5000);
    setup_espnow();
    sendWiFiCredentials();
}

void check_wifi() {
    int count_try = 0;
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi หลุด! พยายามเชื่อมต่อใหม่...");
        
        while (WiFi.status() != WL_CONNECTED) {
            Serial.print(".");
            WiFi.reconnect();
            delay(5000);
            displayClear();
            displayText("Connecting to WiFi...");
            count_try ++;

            if(count_try >=12){
              Serial.println("WiFi ไม่สามารถเชื่อมต่อได้");
              displayClear();
              displayText("Wifi Can't Connect");
              delay(1000);
              displayText("Restarting...");
              delay(5000);
              count_try = 0;
              wm.resetSettings();
              ESP.restart();
            }
        }
        Serial.println("\nWiFi เชื่อมต่อสำเร็จ!");
        displayClear();
        displayText("WiFi Connected");
    }
}
