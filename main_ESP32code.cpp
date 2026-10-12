#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// TODO(esp32-persistent-pc-connection): Remove hardcoded credentials and server URL.
//   Use ConnectionManager instead. It will read stored networks from Preferences
//   and resolve the server via mDNS (steckt-server.local) with a static-IP fallback.
//   Delete these three lines once ConnectionManager.begin() is called in setup().
const char* ssid = "TU_RED";
const char* pass = "TU_CLAVE";
const char* url  = "LA DIRECCION IP"; // IP del PC
#define BOTON 13

void setup() {
  pinMode(BOTON, INPUT_PULLUP);
  camera_config_t c = {};
  c.pin_pwdn=32; c.pin_reset=-1; c.pin_xclk=0;
  c.pin_sccb_sda=26; c.pin_sccb_scl=27;
  c.pin_d7=35; c.pin_d6=34; c.pin_d5=39; c.pin_d4=36;
  c.pin_d3=21; c.pin_d2=19; c.pin_d1=18; c.pin_d0=5;
  c.pin_vsync=25; c.pin_href=23; c.pin_pclk=22;
  c.xclk_freq_hz=20000000;
  c.ledc_timer=LEDC_TIMER_0; c.ledc_channel=LEDC_CHANNEL_0;
  c.pixel_format=PIXFORMAT_JPEG; c.frame_size=FRAMESIZE_UXGA;
  c.jpeg_quality=12; c.fb_count=2;
  c.fb_location=CAMERA_FB_IN_PSRAM; c.grab_mode=CAMERA_GRAB_LATEST;
  esp_camera_init(&c);
  // TODO(esp32-persistent-pc-connection): Replace with ConnectionManager.ensureConnected().
  //   ConnectionManager will iterate stored networks and handle reconnection automatically.
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(300);
}

void loop() {
  if (digitalRead(BOTON) == LOW) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (fb) {
      // TODO(esp32-persistent-pc-connection): Use ConnectionManager.getServerUrl()
      //   instead of the hardcoded `url`. It returns the resolved mDNS or fallback IP.
      HTTPClient http;
      http.begin(url);
      http.addHeader("Content-Type", "image/jpeg");
      http.addHeader("X-Api-Key", "cambia-esta-clave");   // debe coincidir con servidor.py
      http.POST(fb->buf, fb->len);
      http.end();
      esp_camera_fb_return(fb);
    }
    while (digitalRead(BOTON) == LOW) delay(10); // espera a que sueltes
    delay(200);
  }
}
