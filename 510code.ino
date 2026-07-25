#include <WiFiClientSecure.h>
#include <Wire.h>
const int SDA_PIN = 21;
const int SCL_PIN = 18;
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <WiFi.h>
#include <HTTPClient.h>

// --- WI-FI NETWORK CREDENTIALS ---
const char* WIFI_SSID = "Sans's Galaxy A33 5G";          // Replace with your Wi-Fi name
const char* WIFI_PASSWORD = "smallstepsmatter";  // Replace with your Wi-Fi password

// --- FIREBASE DATABASE URL ---
const char* firebaseURL = "https://ai-powered-workshop-assistant-default-rtdb.asia-southeast1.firebasedatabase.app/sensor_data.json"; // Replace with your Firebase URL

// --- PIN DEFINITIONS ---
#define ONE_WIRE_BUS 33          

// --- SAFETY UPPER LIMITS ---
const float MAX_SAFE_TEMP = 45.0;     // Max safe temp in °C
const float MAX_SAFE_ACCEL = 15.0;    // Max safe vibration magnitude in m/s²

// --- OBJECT INITIALIZATION ---
Adafruit_MPU6050 mpu;           
OneWire oneWire(ONE_WIRE_BUS);  
DallasTemperature tempSensor(&oneWire); 

void connectToWiFi() {
  Serial.print("Connecting to Wi-Fi...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ Wi-Fi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Device Wi-Fi ID (MAC): ");
  Serial.println(WiFi.macAddress());
}

void setup() {
  Serial.begin(115200);
  connectToWiFi();
  while (!Serial) delay(10); 
  Wire.begin(SDA_PIN, SCL_PIN);

  Serial.println("\n--- Industrial Monitoring System Initialization ---");

  // Initialize MPU6050 Gyroscope
  if (!mpu.begin()) {
    Serial.println("❌ Failed to find MPU6050 chip!");
  } else {
    Serial.println("✅ MPU6050 Gyroscope successfully connected!");
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  }

  // Initialize DS18B20 Temperature Sensor
  tempSensor.begin();
  Serial.println("✅ Dallas Temperature Sensor Ready!");
  Serial.println("---------------------------------------------------\n");
}

void loop() {
  // 1. Read MPU6050 Acceleration & Calculate Combined Vibration Magnitude
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  // Calculate total acceleration magnitude: magnitude = sqrt(x² + y² + z²)
  float accelMagnitude = sqrt(pow(a.acceleration.x, 2) + pow(a.acceleration.y, 2) + pow(a.acceleration.z, 2));

  // 2. Read DS18B20 Temperature
  tempSensor.requestTemperatures(); 
  float temperatureC = tempSensor.getTempCByIndex(0);


  // --- PRINT SENSOR READINGS TO SERIAL MONITOR ---
  Serial.print(" 🌡️ Temp: "); Serial.print(temperatureC); Serial.print(" °C | ");
  Serial.print(" 📳 Vib: "); Serial.print(accelMagnitude); Serial.print(" m/s² | ");
  // 4. Evaluate Threshold Limits and Flags
  bool systemWarning = false;
  String warningMessage = "System Safe";

  if (temperatureC != -127.00 && temperatureC > MAX_SAFE_TEMP) {
    systemWarning = true;
    warningMessage = "CRITICAL: Temperature Limit Exceeded!";
  } else if (accelMagnitude > MAX_SAFE_ACCEL) {
    systemWarning = true;
    warningMessage = "CRITICAL: High Vibration Detected!";
  }

  // 5. Construct JSON Payload string
  String jsonPayload = "{";
  jsonPayload += "\"device_id\":\"" + WiFi.macAddress() + "\","; 
  jsonPayload += "\"temperature\":" + String(temperatureC) + ",";
  jsonPayload += "\"vibration\":" + String(accelMagnitude) + ",";
  jsonPayload += "\"warning\":" + String(systemWarning ? "true" : "false") + ",";
  jsonPayload += "\"message\":\"" + warningMessage + "\"";
  jsonPayload += "}";

  // 6. Push JSON Payload to Cloud Database via HTTP PUT
  // 6. Push JSON Payload to Cloud Database via HTTP PUT
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure(); // Skip SSL certificate verification for Firebase

    HTTPClient http;
    http.begin(client, firebaseURL); // Pass the secure client here
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.PUT(jsonPayload);
    
    if (httpResponseCode > 0) {
      Serial.print("Data Stream Sync Success. Response code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Data Sync Error: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("Wi-Fi Connection Dropped! Unable to sync data.");
  }
  delay(1000); // Send data packet every 1 second
}