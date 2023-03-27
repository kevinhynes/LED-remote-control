// --------------------------------------------------
//
// Code for control of ESP32 through MIT inventor app (Bluetooth).
// device used for tests: ESP32-WROOM-32D
//
// App on phone has three buttons:
// Button 1: 11 for ON and 10 for OFF
// Button 2: 21 for ON and 20 for OFF
// Button 3: 31 for ON and 30 for OFF
//
// Written by mo thunderz (last update: 20.4.2021)
//
// --------------------------------------------------

// This header is needed for Bluetooth Serial -> works ONLY on ESP32
#include "BluetoothSerial.h"
#include <stdlib.h>     /* atoi */

// Initialize Class:
BluetoothSerial ESP_BT;

// init PINs: assign any pin on ESP32
int led_pin_1 = 5;
int led_pin_2 = 2;

// Parameters for Bluetooth interface
int incoming;

void setup() {
  Serial.begin(19200);
  ESP_BT.begin("ESP32_Control"); //Name of your Bluetooth interface -> will show up on your phone

  pinMode (led_pin_1, OUTPUT);
  pinMode (led_pin_2, OUTPUT);
}

void loop() {

  // -------------------- Receive Bluetooth signal ----------------------
  if (ESP_BT.available())
  {
    incoming = ESP_BT.read(); //Read what we receive

    int value = incoming;
    Serial.println("###############################\n");
    Serial.println("Incoming Value:");
    Serial.println(value);
    Serial.println("Incoming Value:");
    Serial.write(value);
    Serial.println();

    if (value == 1) {
      Serial.println("Turning On");
      Serial.println();
      digitalWrite(led_pin_1, value);
      digitalWrite(led_pin_2, value);
    }
    if (value == 0) {
      Serial.print("Turning Off");
      Serial.println();
      digitalWrite(led_pin_1, value);
      digitalWrite(led_pin_2, value);
    }
    Serial.println("###############################\n");
    delay(50);
  }
}
