#include <ESP8266WiFi.h>
#include <PubSubClient.h>
   
// GPIO 5 D1
#define LED 14
#define detectorPin 16

// WiFi
const char *ssid = "WSKGOOD"; // Enter your WiFi name
const char *password = "7064070640";  // Enter WiFi password
   
// MQTT Broker
const char *mqtt_broker = "13.213.7.109";
const char *topic = "iottalk/Dummy_Device/Button_1/Dummy_Sensor";
const char *topic_sub = "iottalk/Dummy_Device/Output_1/Dummy_Control";
const char *mqtt_username = "";
const char *mqtt_password = "";
const int mqtt_port = 1883;

String msgStr = "";
char json[25];
int val;  

WiFiClient espClient;
PubSubClient client(espClient);
   
void setup() {
    pinMode(LED, OUTPUT);
    //pinMode(buzzer,OUTPUT);
    // Set software serial baud to 115200;
    Serial.begin(115200);
    // connecting to a WiFi network
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.println("Connecting to WiFi..");
    }
    Serial.println("Connected to the WiFi network");
    //connecting to a mqtt broker
    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(callback);
    while (!client.connected()) {
        char* client_id = "esp8266-client-";
        //client_id += char(WiFi.macAddress());
        Serial.println("Connecting to public emqx mqtt broker.....");
        if (client.connect(client_id, mqtt_username, mqtt_password)) {
            Serial.println("Public emqx mqtt broker connected");
        } else {
            Serial.print("failed with state ");
            Serial.print(client.state());
            delay(2000);
        }
    }
    // publish and subscribe
    client.subscribe(topic_sub);
}
   
void callback(char *topic, byte *payload, unsigned int length) {
    Serial.print("Message arrived in topic: ");
    Serial.println(topic);
    Serial.print("Message:");
    String message;
    for (int i = 0; i < length; i++) {
        message = message + (char) payload[i];  // convert *byte to string
    }
    Serial.print(message);
    if (message == "1.0") { 
      digitalWrite(LED, HIGH);  
    }   // LED on
    if (message == "0.0") { 
      digitalWrite(LED, LOW);
    } // LED off
    Serial.println();
    Serial.println("-----------------------");
}
   
void loop() {
    val = digitalRead(detectorPin); // Read value from sensor
    if(val == LOW) // When the sensor detects an obstacle, the LED on the Arduino lights up
    {
      msgStr = "1";
      msgStr.toCharArray(json, 25);
      client.publish(topic, json);
    }
    else if (val == HIGH)
    {
      msgStr = "0";
      msgStr.toCharArray(json, 25);
      client.publish(topic, json);
    }
    else
    {
      }
    
    client.loop();
}
