// TODO(esp32-persistent-pc-connection): Uncomment this file to enable the
//   ConnectionManager module. It handles multi-network WiFi, mDNS server
//   discovery, and automatic reconnection.
//
// #include "ConnectionManager.h"
//
// ConnectionManager::ConnectionManager()
//     : lastHealthCheck(0), currentNetworkIndex(0) {}
//
// void ConnectionManager::begin() {
//     prefs.begin("connmgr", false);
//     ensureConnected();
// }
//
// bool ConnectionManager::ensureConnected() {
//     if (isConnected() && !serverUrl.isEmpty()) {
//         unsigned long now = millis();
//         if (now - lastHealthCheck >= HEALTH_CHECK_INTERVAL_MS) {
//             lastHealthCheck = now;
//             if (!performHealthCheck()) {
//                 Serial.println("[ConnectionManager] Health check failed, reconnecting...");
//                 return reconnect();
//             }
//         }
//         return true;
//     }
//     return reconnect();
// }
//
// bool ConnectionManager::isConnected() {
//     return WiFi.status() == WL_CONNECTED;
// }
//
// String ConnectionManager::getServerUrl() {
//     if (serverUrl.isEmpty()) {
//         resolveServer();
//     }
//     return serverUrl;
// }
//
// bool ConnectionManager::reconnect() {
//     WiFi.disconnect();
//     delay(100);
//
//     int count = getStoredNetworkCount();
//     if (count == 0) {
//         Serial.println("[ConnectionManager] No stored networks");
//         return false;
//     }
//
//     for (int i = 0; i < count; i++) {
//         int idx = (currentNetworkIndex + i) % count;
//         if (tryConnectNetwork(idx)) {
//             currentNetworkIndex = idx;
//             if (resolveServer()) {
//                 lastHealthCheck = millis();
//                 return true;
//             }
//             WiFi.disconnect();
//         }
//     }
//     return false;
// }
//
// bool ConnectionManager::tryConnectNetwork(int index) {
//     String ssid, password;
//     loadCredentials(index, ssid, password);
//     if (ssid.isEmpty()) return false;
//
//     Serial.printf("[ConnectionManager] Trying WiFi: %s\n", ssid.c_str());
//     WiFi.begin(ssid.c_str(), password.c_str());
//
//     unsigned long start = millis();
//     while (WiFi.status() != WL_CONNECTED && millis() - start < WIFI_CONNECT_TIMEOUT_MS) {
//         delay(500);
//         Serial.print(".");
//     }
//     Serial.println();
//
//     if (WiFi.status() == WL_CONNECTED) {
//         Serial.printf("[ConnectionManager] WiFi connected, IP: %s\n", WiFi.localIP().toString().c_str());
//         return true;
//     }
//     Serial.println("[ConnectionManager] WiFi connection failed");
//     return false;
// }
//
// bool ConnectionManager::resolveServer() {
//     String fallback = getFallbackIp();
//
//     for (int attempt = 0; attempt < 3; attempt++) {
//         Serial.printf("[ConnectionManager] mDNS resolving steckt-server.local (attempt %d/3)...\n", attempt + 1);
//         IPAddress serverIP;
//         if (WiFi.hostByName("steckt-server.local", serverIP)) {
//             serverUrl = "http://" + serverIP.toString() + ":5000/upload";
//             Serial.printf("[ConnectionManager] Server resolved via mDNS: %s\n", serverUrl.c_str());
//             return true;
//         }
//         delay(500);
//     }
//
//     if (!fallback.isEmpty()) {
//         serverUrl = "http://" + fallback + ":5000/upload";
//         Serial.printf("[ConnectionManager] Using fallback IP: %s\n", serverUrl.c_str());
//         return true;
//     }
//
//     Serial.println("[ConnectionManager] Could not resolve server");
//     serverUrl = "";
//     return false;
// }
//
// bool ConnectionManager::performHealthCheck() {
//     if (serverUrl.isEmpty()) return false;
//
//     HTTPClient http;
//     String healthUrl = serverUrl;
//     healthUrl.replace("/upload", "/api/ultima");
//     http.begin(healthUrl);
//     int code = http.sendRequest("HEAD");
//     http.end();
//
//     return (code >= 200 && code < 400);
// }
//
// void ConnectionManager::loadCredentials(int index, String& ssid, String& password) {
//     String ssidKey = "ssid" + String(index);
//     String passKey = "pass" + String(index);
//     ssid = prefs.getString(ssidKey.c_str(), "");
//     password = prefs.getString(passKey.c_str(), "");
// }
//
// int ConnectionManager::getStoredNetworkCount() {
//     return prefs.getInt("netcount", 0);
// }
//
// String ConnectionManager::getFallbackIp() {
//     return prefs.getString("fallback_ip", "");
// }
