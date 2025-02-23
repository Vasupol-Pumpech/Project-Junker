#include "WiFiConfig.h"

Preferences preferences;

typedef struct {
    char ssid[32];
    char password[32];
} WiFiCredentials;

WiFiCredentials receivedWiFiData;

// ✅ ฟังก์ชัน callback เมื่อได้รับข้อมูลจาก ESP-NOW
void OnDataRecv(const esp_now_recv_info_t *info, const uint8_t *incomingData, int len) {
    memcpy(&receivedWiFiData, incomingData, sizeof(receivedWiFiData));

    Serial.println("\n===== WiFi Credentials Received =====");
    Serial.print("Received SSID: ");
    Serial.println(receivedWiFiData.ssid);
    Serial.print("Received PASS: ");
    Serial.println(receivedWiFiData.password);
    Serial.println("======================================");

    preferences.begin("wifi-data", true);
    String savedSSID = preferences.getString("ssid", "");
    String savedPASS = preferences.getString("password", "");
    preferences.end();

    if (savedSSID != String(receivedWiFiData.ssid) || savedPASS != String(receivedWiFiData.password)) {
        Serial.println("🔄 WiFi Credentials Changed! Updating and Restarting...");
        
        preferences.begin("wifi-data", false);
        preferences.putString("ssid", receivedWiFiData.ssid);
        preferences.putString("password", receivedWiFiData.password);
        preferences.end();
        
        delay(2000);
        Serial.println("🔄 Restarting ESP32...");
        ESP.restart();
    } else {
        Serial.println("✅ WiFi Credentials Are The Same. No Restart Needed.");
    }
}

// ✅ ฟังก์ชันสำหรับล็อก ESP-NOW ให้อยู่ที่ Channel 6
void lockESPNowChannel() {
    WiFi.mode(WIFI_STA);
    delay(500);
    WiFi.setChannel(6);
    Serial.print("✅ ESP-NOW Locked to Channel: ");
    Serial.println(WiFi.channel());
}

// ✅ ฟังก์ชันเริ่มต้น ESP-NOW
void setupESPNow() {
    if (esp_now_init() != ESP_OK) {
        Serial.println("❌ ESP-NOW Initialization Failed! Restarting...");
        delay(3000);
        ESP.restart();
    }

    esp_now_register_recv_cb(OnDataRecv);
    Serial.println("✅ ESP-NOW Receiver Initialized. Waiting for data...");
}

// ✅ ฟังก์ชัน Task สำหรับ ESP-NOW บน Core 0 (รอรับค่าตลอด)
void espNowTask(void *parameter) {
    setupESPNow();
    while (true) {
        delay(10);  // ✅ ลดการใช้ CPU โดยให้ Task หน่วงเวลาเล็กน้อย
    }
}

// ✅ ฟังก์ชันรีเซ็ต ESP-NOW และเพิ่ม Peer ใหม่
void resetESPNow() {
    Serial.println("\n⚠️ WiFi Disconnected! Resetting ESP-NOW...");

    esp_now_deinit();
    delay(500);

    if (esp_now_init() != ESP_OK) {
        Serial.println("❌ ESP-NOW Re-initialization Failed! Restarting...");
        delay(3000);
        ESP.restart();
    }

    // ✅ เพิ่มตัวส่ง (Peer) กลับไปใหม่
    esp_now_peer_info_t peerInfo;
    memset(&peerInfo, 0, sizeof(peerInfo));
    uint8_t senderMacAddress[] = {0x7C, 0x87, 0xCE, 0x31, 0xC0, 0x3C};  // ใส่ MAC Address ของตัวส่ง
    memcpy(peerInfo.peer_addr, senderMacAddress, 6);
    peerInfo.channel = 6;
    peerInfo.encrypt = false;

    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("❌ Failed to add sender as Peer!");
    } else {
        Serial.println("✅ Sender added as Peer Successfully!");
    }

    esp_now_register_recv_cb(OnDataRecv);
    Serial.println("✅ ESP-NOW Restarted Successfully!");
}

void setup_wifi() {
    // ✅ ล็อก Channel ของ ESP-NOW ให้อยู่ที่ 6
    lockESPNowChannel();

    Serial.print("Receiver WiFi Channel: ");
    Serial.println(WiFi.channel());

    Serial.print("Connecting to WiFi: ");
    preferences.begin("wifi-data", true);
    String ssid = preferences.getString("ssid", "");
    String pass = preferences.getString("password", "");
    preferences.end();

    if (ssid != "") {
        Serial.print(ssid);
        WiFi.begin(ssid.c_str(), pass.c_str());
    }

    int wifiTimeout = 20;
    while (WiFi.status() != WL_CONNECTED && wifiTimeout > 0) {
        Serial.print(".");
        delay(1000);
        wifiTimeout--;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi Connected Successfully!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\n❌ WiFi Connection Failed!");
    }

    Serial.print("ESP32 Receiver MAC Address: ");
    Serial.println(WiFi.macAddress());

    // ✅ เริ่ม Task ESP-NOW บน Core 0
    xTaskCreatePinnedToCore(
        espNowTask, "ESP-NOW Task", 2048, NULL, 1, NULL, 0);
}