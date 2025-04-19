#include <ESP8266WiFi.h> 
#include "ThingSpeak.h"
#define BLYNK_TEMPLATE_ID "TMPL6rPYtpGOy"
#define BLYNK_TEMPLATE_NAME "4LED"
//#define Auth "cGxwzESkTcImx2FoPB_j29NGW-TW9PtT"
#define BLYNK_FIRMWARE_VERSION   
#define BLYNK_PRINT Serial
#include <BlynkSimpleEsp8266.h>


char ssid[] = "Quoc Toan";
char pass[] = "12345678";
char auth[] = "cGxwzESkTcImx2FoPB_j29NGW-TW9PtT";

//Wifi Nha
// #define WIFI_SSID "Quoc Toan" 
// #define WIFI_PASSWORD "123456789"

//Wifi Truong
#define WIFI_SSID "PTIT.HCM_SV" 
#define WIFI_PASSWORD ""

WiFiClient  client;
unsigned long myChannelNumber = 2657868;
const char * myWriteAPIKey = "EPE2RTNPWXG3DAZ7";

int LED1 = D1;
int LED2 = D2;
int LED3 = D5;
int LED4 = D6;

WidgetLED LED_KET_NOI(V0);
BlynkTimer timer;
boolean bt1_state=HIGH;
unsigned long timeT = millis();

void setup()
{
  Serial.begin(115200);
  delay(100);
  pinMode(LED1,OUTPUT);
  pinMode(LED2,OUTPUT);
  pinMode(LED3,OUTPUT);
  pinMode(LED4,OUTPUT);
  //pinMode(button1,INPUT_PULLUP);
  digitalWrite(LED1,LOW);
  digitalWrite(LED2,LOW);
  digitalWrite(LED3,LOW);
  digitalWrite(LED4,LOW);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD); 
  while (WiFi.status() != WL_CONNECTED) 
  { 
    delay(500); 
    Serial.print("."); 
  }
  ThingSpeak.begin(client);
  Blynk.begin(auth, ssid, pass);
}
void loop() 
{
  Blynk.run();
  timer.run();
  Serial.println(WiFi.localIP());
  Serial.println("\nĐã kết nối với mạng Wi-Fi");

  if(millis() - timeT > 1000){
    if(LED_KET_NOI.getValue()) LED_KET_NOI.off();
    else LED_KET_NOI.on();
    timeT = millis();
  }

  int led1_state = digitalRead(LED1);
  int led2_state = digitalRead(LED2);
  int led3_state = digitalRead(LED3);
  int led4_state = digitalRead(LED4);

  ThingSpeak.writeField(myChannelNumber, 1, led1_state, myWriteAPIKey);
  ThingSpeak.writeField(myChannelNumber, 2, led2_state, myWriteAPIKey);
  ThingSpeak.writeField(myChannelNumber, 3, led3_state, myWriteAPIKey);
  ThingSpeak.writeField(myChannelNumber, 4, led4_state, myWriteAPIKey);

  delay(1000);
}

BLYNK_CONNECTED() {
  // Request the latest state from the server
  Blynk.syncAll();
}
BLYNK_WRITE(V1){
  int p = param.asInt();
  digitalWrite(D1, p);
}
BLYNK_WRITE(V2){ 
  int p = param.asInt();
  digitalWrite(D2, p);
}
BLYNK_WRITE(V3){ 
  int p = param.asInt();
  digitalWrite(D5, p);
}
BLYNK_WRITE(V4){ 
  int p = param.asInt();
  digitalWrite(D6, p);
}


