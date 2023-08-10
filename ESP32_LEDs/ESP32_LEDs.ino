// For Bluetooth Serial -> works ONLY on ESP32
#include "BluetoothSerial.h"
// For WS2812B LEDs
#include <FastLED.h>
// For abs()
#include <cstdlib>

// LED SECTION
const int DATA_PIN = 22;
const int POT_PIN = 15;
const int REF_PIN = 25;
const int NUM_LEDS = 60;
const unsigned int MESSAGE_LENGTH = 6; // in bytes (0-indexed)
CRGB leds[NUM_LEDS];

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

void turnStripRGB(int r, int g, int b) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i].setRGB(r, g, b);
    }
  FastLED.show();
}

void turnStripGRB(int g, int r, int b) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i].setRGB(g, r, b);
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


void setup() {
  FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  Serial.begin(115200);
  ESP_BT.begin("ESP32_Control"); //Name of your Bluetooth interface -> will show up on your phone
  pinMode(POT_PIN, INPUT);
  analogSetVRefPin(REF_PIN);
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


void reset_message(int message[]) {
  for (int j = 0; j < (sizeof(message) / sizeof(message[0])); j++) {
    message[j] = -1;
    Serial.println(message[j]);
  }
}


void loop() {
  static int message[] = {-1, -1, -1, -1, -1, -1};
  static unsigned int i = 0;
  int cur_byte;
  static int raw_reading;

  const int num_readings1 = 75;
  static int pot_vals1[num_readings1];
  static int pot_sum1 = 0;
  static int pot_avg1 = 0;
  static int p1 = 0;

  const int num_readings2 = 150;
  static int pot_vals2[num_readings2];
  static int pot_sum2 = 0;
  static int pot_avg2 = 0;
  static int p2 = 0;

  const int num_diffs = 25;
  static int diffs[num_diffs];
  static int diff_sum = 0;
  static int diff_avg = 0;
  static int d = 0;
  int difference;

  static int num_loops = 0;
  static int num_on_readings = 0;
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
          // GRB ordering for WS2812B
          turnStripGRB(dimmedGreen, dimmedRed, dimmedBlue);
      }
      else {
        Serial.println("Invalid message recieved");
      }
      // // Reset variables
      Serial.println("Resetting message...");
      i = 0;
      reset_message(message);
      }
    }

  // -------------------- Receive potentiometer value ----------------------
  // ESP32 analogRead() values fluctuate WILDLY (+/- 300).  Need to keep
  // running sum averages to compare to one another.
  // Then keep running sum average of the difference b/w these averages.
  // Using this number to read when the potentiometer is actually being spin.
  raw_reading = analogRead(POT_PIN);

  pot_sum1 = pot_sum1 - pot_vals1[p1] + raw_reading;
  pot_vals1[p1] = raw_reading;
  pot_avg1 = pot_sum1 / num_readings1;
  p1 = (p1 + 1) % num_readings1;

  pot_sum2 = pot_sum2 - pot_vals2[p2] + raw_reading;
  pot_vals2[p2] = raw_reading;
  pot_avg2 = pot_sum2 / num_readings2;
  p2 = (p2 + 1) % num_readings2;

  difference = pot_avg1 - pot_avg2;
  diff_sum = diff_sum - diffs[d] + difference;
  diffs[d] = difference;
  diff_avg = diff_sum / num_diffs;
  d = (d + 1) % num_diffs;

  if (num_loops < num_readings2) {
    num_loops += 1;
  } else {
    if (abs(diff_avg) > 20 && num_on_readings < 10) {
      num_on_readings += 1;
    } else if (abs(diff_avg) > 20) {
      Serial.print("Difference: ");
      Serial.print(difference);
      Serial.print("  Average Difference: ");
      Serial.print(diff_avg);
      Serial.println("   ON");
    } else {
      num_on_readings = 0;
      Serial.print(abs(difference));
      Serial.print("   -   ");
      Serial.println(abs(diff_avg));
    }
  }
}
