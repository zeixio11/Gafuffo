// TODO(esp32-persistent-pc-connection): Uncomment this file to enable the
//   ConnectionManager module. It must be used together with ConnectionManager.cpp.
//
// #ifndef CONNECTION_MANAGER_H
// #define CONNECTION_MANAGER_H
//
// #include <WiFi.h>
// #include <Preferences.h>
// #include <ESPmDNS.h>
// #include <HTTPClient.h>
//
// class ConnectionManager {
// public:
//     ConnectionManager();
//     void begin();
//     bool ensureConnected();
//     bool isConnected();
//     String getServerUrl();
//
// private:
//     Preferences prefs;
//     String serverUrl;
//     unsigned long lastHealthCheck;
//     int currentNetworkIndex;
//     static const int MAX_NETWORKS = 5;
//     static const unsigned long HEALTH_CHECK_INTERVAL_MS = 10000;
//     static const unsigned long HEALTH_CHECK_FAIL_TIMEOUT_MS = 30000;
//     static const unsigned long WIFI_CONNECT_TIMEOUT_MS = 10000;
//
//     bool reconnect();
//     bool tryConnectNetwork(int index);
//     bool resolveServer();
//     bool performHealthCheck();
//     void loadCredentials(int index, String& ssid, String& password);
//     int getStoredNetworkCount();
//     String getFallbackIp();
// };
//
// #endif
