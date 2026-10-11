// TODO(esp32-persistent-pc-connection): Uncomment this entire sketch to flash
//   WiFi credentials and fallback IP into ESP32 Preferences (NVS).
//   Run this once, then flash the main sketch.
//
// /*
//   setup_credentials.ino
//
//   One-time setup sketch for the ESP32.
//   Writes WiFi credentials and fallback server IP into Preferences (NVS)
//   so the main firmware (stckt-claude.cpp) can read them at runtime.
//
//   Edit the NETWORKS array below with your WiFi credentials, then flash once.
//   After flashing, upload the main sketch normally.
// */
//
// #include <Preferences.h>
//
// Preferences prefs;
//
// struct Network {
//   const char* ssid;
//   const char* password;
// };
//
// // ============================================
// // EDIT THESE VALUES BEFORE FLASHING
// // ============================================
// Network NETWORKS[] = {
//   {"ACTURUS_EXT", "Erizo690#qts"},
//   {"TU_OTRA_RED", "TU_OTRA_CLAVE"},
//   // Add up to 5 networks total
// };
//
// const char* FALLBACK_IP = "192.168.1.50";
// // ============================================
//
// void setup() {
//   Serial.begin(115200);
//   delay(1000);
//
//   prefs.begin("connmgr", false);
//
//   int count = sizeof(NETWORKS) / sizeof(Network);
//   if (count > 5) count = 5;
//
//   prefs.putInt("netcount", count);
//
//   for (int i = 0; i < count; i++) {
//     String ssidKey = "ssid" + String(i);
//     String passKey = "pass" + String(i);
//     prefs.putString(ssidKey.c_str(), NETWORKS[i].ssid);
//     prefs.putString(passKey.c_str(), NETWORKS[i].password);
//     Serial.printf("Stored network %d: %s\n", i, NETWORKS[i].ssid);
//   }
//
//   prefs.putString("fallback_ip", FALLBACK_IP);
//   Serial.printf("Stored fallback IP: %s\n", FALLBACK_IP);
//
//   prefs.end();
//
//   Serial.println("\nCredentials saved. You can now flash the main sketch.");
// }
//
// void loop() {
//   // Nothing to do
// }
