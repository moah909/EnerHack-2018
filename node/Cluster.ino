/*
 *  Simple HTTP get webclient test
 */

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>

const char* ssid     = "enerhack";
const char* password = "internetaccess";

int photoPin = A0;
int roomPin  = 2;
int prevLight, prevTemp, prevInRoom = -1;

WiFiUDP Udp;

String messageBuilder(int temp, int light, int inRoom) {
  //I now know sprintf works with Arduino
  String tempStr = "temp:";
  tempStr = tempStr + temp;
  tempStr = tempStr + " light:";
  tempStr = tempStr + light;
  tempStr = tempStr + " inRoom:";
  tempStr = tempStr + inRoom;

  return tempStr;
}

void setup() {
  Serial.begin(115200);
  delay(100);

  // We start by connecting to a WiFi network

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  pinMode(roomPin, INPUT);
}

int value = 0;

void loop() {
  delay(500);

  prevLight = prevLight/2 + analogRead(photoPin)/2;
  prevInRoom = digitalRead(roomPin);
  
  Serial.println("Sending data...");
  Serial.println(messageBuilder(prevTemp,prevLight/4,prevInRoom));
  Udp.beginPacket("192.168.1.100", 5005);
  Udp.print(messageBuilder(prevTemp,prevLight/4,prevInRoom));
  Udp.endPacket();
}
