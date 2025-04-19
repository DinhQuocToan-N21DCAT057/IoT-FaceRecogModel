/*************************************************************
  Blynk is a platform with iOS and Android apps to control
  ESP32, Arduino, Raspberry Pi and the likes over the Internet.
  You can easily build mobile and web interfaces for any
  projects by simply dragging and dropping widgets.

    Downloads, docs, tutorials: https://www.blynk.io
    Sketch generator:           https://examples.blynk.cc
    Blynk community:            https://community.blynk.cc
    Follow us:                  https://www.fb.com/blynkapp
                                https://twitter.com/blynk_app

  Blynk library is licensed under MIT license
 *************************************************************
  Blynk.Edgent implements:
  - Blynk.Inject - Dynamic WiFi credentials provisioning
  - Blynk.Air    - Over The Air firmware updates
  - Device state indication using a physical LED
  - Credentials reset using a physical Button
 *************************************************************/

/* Fill in information from your Blynk Template here */
/* Read more: https://bit.ly/BlynkInject */
#define BLYNK_TEMPLATE_ID "TMPL6rPYtpGOy"
#define BLYNK_TEMPLATE_NAME "4LED"
//#define Auth "cGxwzESkTcImx2FoPB_j29NGW-TW9PtT"
#define BLYNK_FIRMWARE_VERSION        "0.1.0"

#define BLYNK_PRINT Serial
//#define BLYNK_DEBUG

#define APP_DEBUG

// Uncomment your board, or configure a custom board in Settings.h
//#define USE_SPARKFUN_BLYNK_BOARD
#define USE_NODE_MCU_BOARD
//#define USE_WITTY_CLOUD_BOARD
//#define USE_WEMOS_D1_MINI

//#include "BlynkEdgent.h"
#include <ESP8266WiFi.h>
#include "BlynkSimpleEsp8266.h"
BlynkTimer timer;

WidgetLED LED_KET_NOI(V0);
int LED1 = D1;
int LED2 = D2;
unsigned long timeT = millis();
const char* ssid = "Quoc Toan";
const char* pass = "12345678";
const char* auth = "cGxwzESkTcImx2FoPB_j29NGW-TW9PtT";

void setup()
{
  Serial.begin(115200);
  delay(100);
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);

  WiFi.begin(ssid, pass);

  // Chờ kết nối Wi-Fi
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    //Serial.print(".");
  }

  // Kiểm tra kết nối và in địa chỉ IP
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("Địa chỉ IP của ESP8266 là: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("Không thể kết nối tới Wi-Fi");
  }

  //BlynkEdgent.begin();

  Blynk.begin(auth, ssid, pass);
  Blynk.connect(3333);  // timeout set to 10 seconds and then continue without Blynk
  while (Blynk.connect() == false) {
    Serial.print("Chk");
  }
  Serial.println("Kết nối tới Blynk server");

}

void loop() {
  //BlynkEdgent.run();
  if(connected2Blynk){
    Blynk.run();
    //Chương trình điều khiển led chớp tắt mỗi giây
    if(millis() - timeT > 1000){
    if(LED_KET_NOI.getValue()) LED_KET_NOI.off();
    else LED_KET_NOI.on();
    timeT = millis();
    }
  }
  timer.run();
}

BLYNK_CONNECTED(){
  Blynk.syncAll(); //Đồng bộ data từ server xuống ESP khi kết nối
}
BLYNK_WRITE(V1){
  int p = param.asInt();
  digitalWrite(D1, p);
}
BLYNK_WRITE(V2){ 
  int p = param.asInt();
  digitalWrite(D2,p);
}
BLYNK_WRITE(V3){ 
  int p = param.asInt();
  digitalWrite(D5,p);
}
BLYNK_WRITE(V4){ 
  int p = param.asInt();
  digitalWrite(D6,p);
}
