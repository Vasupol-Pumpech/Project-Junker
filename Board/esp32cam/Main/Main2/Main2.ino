#include "esp_camera.h"
#include "Arduino.h"
#include "WiFiConfig.h"
#include "MQTTConfig.h"
#include "CameraConfig.h"
#include "esp_http_server.h"
#include "Controlls.h"

#define SENSOR_PIN  15
#define LED_FLASH 4  

const int pingPin = 2;    // ขา Trigger (Ultrasonic)
const int inPin = 3;    // ขา Echo

int stuck_count = 0;   // ตัวนับจำนวนครั้งที่พบของติด
bool stuck_state = false; // สถานะ stuck หรือ unstuck

httpd_handle_t camera_httpd = NULL;

void startCameraServer() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();

    httpd_uri_t capture_uri = {
        .uri       = "/capture",
        .method    = HTTP_GET,
        .handler   = capture_handler,
        .user_ctx  = NULL
    };

    if (httpd_start(&camera_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(camera_httpd, &capture_uri);
        Serial.println("Camera server started");
    } else {
        Serial.println("Failed to start camera server");
    }
}

static esp_err_t capture_handler(httpd_req_t *req) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (fb) {
        esp_camera_fb_return(fb);
    }
    delay(1000);  

    fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Camera capture failed");
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
    esp_err_t res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
    esp_camera_fb_return(fb);
    return res;
}

void setup() {
  
    Serial.begin(115200);

    pinMode(pingPin, OUTPUT);
    pinMode(inPin, INPUT);
    pinMode(SENSOR_PIN, INPUT);

    setup_Controlls();
    WiFi.mode(WIFI_STA);
    pinMode(LED_FLASH, OUTPUT);
    digitalWrite(LED_FLASH, LOW);

    setup_wifi();

    while (WiFi.status() != WL_CONNECTED) {
        Serial.println("Waiting for WiFi connection...");
        delay(1000);
    }
    Serial.println("WiFi Connected!");

    setup_mqtt();
    setup_camera();
    startCameraServer();
    reconnectMQTT();
    sendMQTTMessageStr(mqtt_SendReady, "Ready");
    doorStart();

}

void loop() {

    if (!client.connected()) {
        reconnectMQTT();
    }
    client.loop();
    int sensorState = digitalRead(SENSOR_PIN);

    if (sensorState == LOW) {
        stuck_count++;
        digitalWrite(LED_FLASH, HIGH);
        doorOpen();

        if (stuck_count >= 10 && !stuck_state) {
            sendMQTTMessageStr(mqtt_Stuck, "stuck");
            Serial.print("stuck count : ");
            Serial.println(stuck_count);
            stuck_state = true;
        }
        delay(1000);
        return; 
    }

    if (stuck_state) {
        sendMQTTMessageStr(mqtt_Stuck, "unstuck");
        digitalWrite(LED_FLASH, LOW);
        delay(5000);
        doorClose();
        stuck_state = false;
    }

    if (stuck_count >= 1){
        stuck_count = 0;
        delay(5000);
        digitalWrite(LED_FLASH, LOW);
        doorClose();
    }

    static unsigned long ReadySendTime = 0;
    unsigned long currentMillis = millis();

    if (currentMillis - ReadySendTime >= 10000) {
        sendMQTTMessageStr(mqtt_SendReady, "Ready");
        Serial.println("📡 Sent Ready");
        ReadySendTime = currentMillis;
    }

    if (start == true){
      }else{
        return;
      }
    

    long duration, cm;
    digitalWrite(pingPin, LOW);
    delayMicroseconds(2);
    digitalWrite(pingPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(pingPin, LOW);

    duration = pulseIn(inPin, HIGH, 30000);

    if (duration == 0) {
        Serial.println("Warning: No Echo detected! Skipping...");
        digitalWrite(LED_FLASH, LOW);
        doorClose();
        return;
    }

    cm = microsecondsToCentimeters(duration);

    if (cm <= 0 || cm > 500) {
        Serial.println("Invalid distance detected! Skipping...");
        digitalWrite(LED_FLASH, LOW);
        doorClose();
        return;
    }

    Serial.print("Distance: ");
    Serial.print(cm);
    Serial.println(" cm");

    delay(100);

    if (backdoor) {
        Serial.println("Backdoor Open...");
        doorClose();
        delay(10000);
        return;
    }

    if (cm <= 50) {
        Serial.println("Person detected");
        digitalWrite(LED_FLASH, HIGH);
        doorOpen();
    } else {
        digitalWrite(LED_FLASH, LOW);
        doorClose();
        return;
    }

    delay(500);  
    sensorState = digitalRead(SENSOR_PIN);  
    if (sensorState == LOW) {
        Serial.println("Object Detected!");
        // delay(2000);
        doorClose();
        delay(1000);
    } else {
        Serial.println("No Object.");
        return;
    }

    // ✅ ส่งภาพไป MQTT
    String cameraUrl = "http://" + WiFi.localIP().toString() + "/capture";
    String message = "send_img " + cameraUrl;
    sendMQTTMessageStr(mqtt_camera, message.c_str());
    Serial.println("Sent image link: " + message);

    unsigned long startTime = millis();
    unsigned long lastReadySent = millis();

    dropGrabage = false;

    while (dropGrabage == false) {
        client.loop();
        if (millis() - lastReadySent >= 10000) {
            sendMQTTMessageStr(mqtt_SendReady, "Ready");
            Serial.println("Sent Ready (inside while)");
            lastReadySent = millis();
        }

        if (millis() - startTime >= 60000) {
            Serial.println("Timeout!");
            break;
        }
        
        delay(500);
    }

    // startTime = millis();
    dropGrabage = false;
    Serial.println("Reset dropGrabage.");
    digitalWrite(LED_FLASH, LOW);

}
