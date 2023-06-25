// Needed for Bluetooth Serial -> works ONLY on ESP32
#include "BluetoothSerial.h"
// Needed for WS2812B LEDs
#include <FastLED.h>

// LED SECTION
#define NUM_LEDS 58
#define LED_PIN1 2
#define LED_PIN2 5
#define DATA_PIN 26
CRGB leds[NUM_LEDS];

void turnStripOn() {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i].setRGB(255, 255, 255);
  }
  FastLED.show();
}

void turnStripOff() {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB::Black;
  }
  FastLED.show();
}

void dimStrip(int level) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i].setRGB(level, level, level);
  }
  FastLED.show();
}

void turnStripRGB(int r, int g, int b) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i].setRGB(r, g, b);
    }
  FastLED.show();
}

void turnStripHSV(int h, int s, int v) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i].setHSV(h, s, v);
  }
  FastLED.show();
}

void moveLEDRGB(int r, int g, int b) {
  turnStripOff();
  int prev = -1;
  for (int cur = 0; cur < NUM_LEDS; cur++) {
    leds[cur].setRGB(r, g, b);
    leds[prev].setRGB(0, 0, 0);
    FastLED.show();
    prev += 1;
    delay(25);
  }
  leds[prev].setRGB(0, 0, 0);
  FastLED.show();
}

void blink() {
  turnStripOn();
  delay(500);
  turnStripOff();
  delay(500);
}


// Initialize Class:
BluetoothSerial ESP_BT;

// Global master values
int mode = 1;
int masterRed = 255;
int masterGreen = 255;
int masterBlue = 255;
int masterBrightness = 100;

// Dimmer / processed values
int dimmedRed = 255;
int dimmedGreen = 255;
int dimmedBlue = 255;


const unsigned int MESSAGE_LENGTH = 6; // in bytes (0-indexed)

void setup() {
  FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  Serial.begin(115200);
  ESP_BT.begin("ESP32_Control"); //Name of your Bluetooth interface -> will show up on your phone
  pinMode (LED_PIN1, OUTPUT);
  pinMode (LED_PIN2, OUTPUT);
}


bool validate_message(int message[]) {
  Serial.println("validate_message, message:");
  for (int i = 0; i < (sizeof(message) / sizeof(message[0])); i++) {
    Serial.println(message[i]);
    if (i == 0) {
      if (!(message[i] < 10)) {
        return false;
      }
    }
    else {
      if (!((0 <= message[i]) && (message[i] <= 255))) {
        return false;
      }
    }
    mode = message[0];
    // "Color Mode" - change color, keep brightness
    if (mode == 1) {
      masterRed = message[1];
      masterGreen = message[2];
      masterBlue = message[3];
      dimmedRed = int(masterRed * masterBrightness / 100);
      dimmedGreen = int(masterGreen * masterBrightness / 100);
      dimmedBlue = int(masterBlue * masterBrightness / 100);
    }
    // "Dimmer Mode" - keep color, change brightness
    if (mode == 2) {
      masterBrightness = message[4];
      dimmedRed = int(masterRed * masterBrightness / 100);
      dimmedGreen = int(masterGreen * masterBrightness / 100);
      dimmedBlue = int(masterBlue * masterBrightness / 100);
    }
  }
  return true;
}


void loop() {
  static int message[] = {-1, -1, -1, -1, -1, -1};
  static unsigned int i = 0;
  int cur_byte;

  // -------------------- Receive Bluetooth signal ----------------------
  // This loop seems to run faster than message is being sent, therefore
  // need to keep track of what byte we are on in the message
  // static variables keep state after function is called

  // Incoming data is in form:
    // mode red green blue alpha -1
  if (ESP_BT.available()) {
    cur_byte = ESP_BT.read();
    message[i] = cur_byte;

    // Mode
    if (i == 0) {
      Serial.println("###############################");
      Serial.println(cur_byte);
      i = i + 1;
    }

    // RGB
    else if ((1 <= i) && (i < MESSAGE_LENGTH - 2)) {
      Serial.println(cur_byte);
      i = i + 1;
    }

    // Alpha
    else if (i == MESSAGE_LENGTH - 2) {
      Serial.println(cur_byte);
      Serial.println("###############################");
      i = i + 1;
    }

    // End byte is -1
    else {
      Serial.println("Validating message of size:");
      Serial.println(sizeof(message));
      Serial.println(sizeof(message[0]));
      if (validate_message(message)) {
        Serial.println("Valid message received");
          turnStripRGB(dimmedRed, dimmedGreen, dimmedBlue);
      }
      else {
        Serial.println("Invalid message recieved");
      }
      // Reset variables
      Serial.println("Resetting message...");
      i = 0;
      for (int i = 0; i < (sizeof(message) / sizeof(message[0])); i++) {
        message[i] = -1;
        Serial.println(message[i]);
      }
    }
    // delay(50);

  }
