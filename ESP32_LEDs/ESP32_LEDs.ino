// TODAY
// Needed for Bluetooth Serial -> works ONLY on ESP32
#include "BluetoothSerial.h"
// Needed for WS2812B LEDs
#include <FastLED.h>
// Needed for abs() function
#include <cstdlib>
// Needed for keeping NUM_LEDS permanent
#include <Preferences.h>


// Preferences holds permanent data
Preferences preferences;


// Define Pins
const int DATA_PIN = 22;
const int POT_PIN = 15;
const int REF_PIN = 25;


// Initialize Bluetooth Class, BT Message Length
BluetoothSerial ESP_BT;
const unsigned int MESSAGE_LENGTH = 6; // in bytes (0-indexed)


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


// Initialize LED array - needed for LED functions
unsigned int NUM_LEDS;
CRGB *leds;

void turnStripOn() {
    for (int i = 0; i < NUM_LEDS; i++) {
        leds[i].setRGB(255, 255, 255);
    }
    FastLED.show();
}

void turnStripOff() {
    for (int i = 0; i < NUM_LEDS; i++) {
        leds[i].setRGB(0, 0, 0);
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

bool validate_message(int message[]) {
    Serial.println("validate_message, message:");
    for (int j = 0; j < MESSAGE_LENGTH; j++) {
        Serial.print(message[j]);
        Serial.print(" | ");
        if (j == 0) {
            if (!(0 < message[j]) || !(message[j] < 10)) {
                return false;
            }
        }
        else {
            if (!((0 <= message[j]) && (message[j] <= 255))) {
                return false;
            }
        }
    }
    Serial.println(" ");
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
    // Input number of LEDs
    if (mode == 3) {
        FastLED.clear();
        FastLED.show();
        delete[] leds;
        leds = nullptr;

        // To allow NUM_LEDS to be over 255, need to combine 2 bytes.
        int leftBits = message[1];
        int rightBits = message[2];
        leftBits = leftBits << 8;
        NUM_LEDS = leftBits + rightBits;

        leds = new CRGB[NUM_LEDS];
        FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
        preferences.putUInt("NUM_LEDS", NUM_LEDS);
        Serial.print("NUM_LEDS now ");
        Serial.println(NUM_LEDS);
    }
    return true;
}

void reset_message(int message[]) {
    for (int j = 0; j < MESSAGE_LENGTH; j++) {
        message[j] = -1;
        Serial.println(message[j]);
    }
}


void setup() {
    Serial.begin(115200);
    ESP_BT.begin("ESP32_Control"); //Name of your Bluetooth interface -> will show up on your phone
    preferences.begin("myApp", false);  // Open preferences namespace
    NUM_LEDS = preferences.getUInt("NUM_LEDS", 0);  // Load with default value
    if (NUM_LEDS == 0) {
        Serial.println("NUM_LEDS read as 0, resetting to 100 ");
        NUM_LEDS = 100;
    }
    else {
        Serial.print("NUM_LEDS read as: ");
        Serial.println(NUM_LEDS);
    }
    leds = new CRGB[NUM_LEDS];
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);  // GRB ordering typ for WS2812B
    pinMode(POT_PIN, INPUT);
    analogSetVRefPin(REF_PIN);
}

void loop() {
    // -------------------- Receive Bluetooth signal ----------------------
    // This loop seems to run faster than message is being sent, therefore
    // need to keep track of what byte we are on in the message.
    // `static` variables keep state after function is called (necessary).

    // Incoming data is in form:
    // mode red green blue alpha -1
    // NOTE: BluetoothSerial.read() seemingly incapable of reading -1,
    //       so its 255... ?  Was supposed to be an end of message flag,
    //       but code runs without errors not using it...
    static int message[] = {-1, -1, -1, -1, -1, -1};
    static unsigned int i = 0;
    int cur_byte;
    static int bluetooth_timeout = 1000;

    if (ESP_BT.available()) {
        cur_byte = static_cast<int>(ESP_BT.read());
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

            // End byte is -1 (actually 255 because idk)
        else {
            Serial.println("Validating message of size:");
            Serial.println(sizeof(message));
            Serial.println(sizeof(message[0]));
            if (validate_message(message)) {
                Serial.println("Valid message received");
                turnStripRGB(dimmedRed, dimmedGreen, dimmedBlue);
                bluetooth_timeout = 1000;
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
    // Using this number to read when the potentiometer is actually being spun.
    static int pot_reading;
    const int num_pot_readings = 5;
    static int pot_readings[num_pot_readings];
    static int pot_reading_sum = 0;
    static int pot_reading_avg = 0;
    static int p = 0;

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
    float pot_brightness;

    pot_reading = analogRead(POT_PIN);
    pot_reading_sum = pot_reading_sum - pot_readings[p] + pot_reading;
    pot_readings[p] = pot_reading;
    pot_reading_avg = pot_reading_sum / num_pot_readings;
    p = (p + 1) % num_pot_readings;

    pot_sum1 = pot_sum1 - pot_vals1[p1] + pot_reading;
    pot_vals1[p1] = pot_reading;
    pot_avg1 = pot_sum1 / num_readings1;
    p1 = (p1 + 1) % num_readings1;

    pot_sum2 = pot_sum2 - pot_vals2[p2] + pot_reading;
    pot_vals2[p2] = pot_reading;
    pot_avg2 = pot_sum2 / num_readings2;
    p2 = (p2 + 1) % num_readings2;

    difference = pot_avg1 - pot_avg2;
    diff_sum = diff_sum - diffs[d] + difference;
    diffs[d] = difference;
    diff_avg = diff_sum / num_diffs;
    d = (d + 1) % num_diffs;

    // Initialize - make sure the num_readings lists are full before
    // doing anything.
    if (num_loops < num_readings2) {
        num_loops += 1;
    }
        // Receiving a Bluetooth command makes the pot_reading bounce up.
        // Give it a second so this doesn't randomly read the potentiometer.
    else if (bluetooth_timeout > 0) {
        bluetooth_timeout -= 1;
    }
        // Even after doing running averages, potentiometer values still
        // fluctuate a LOT randomly.. num_on_readings helps limit false
        // positives but also makes it less responsive.
    else if (abs(diff_avg) > 20 && num_on_readings < 10) {
        num_on_readings += 1;
    }
    else if (abs(diff_avg) > 20) {
        Serial.print(abs(difference));
        Serial.print("   |   ");
        Serial.print(abs(diff_avg));
        Serial.print("   |   ");
        Serial.print(pot_reading_avg);
        Serial.print("   ON");
        masterBrightness = int(float(pot_reading_avg) / 2600.0 * 100.0);
        dimmedRed = min(int(255 * masterBrightness / 100), 255);
        dimmedGreen = min(int(255 * masterBrightness / 100), 255);
        dimmedBlue = min(int(255 * masterBrightness / 100), 255);
        Serial.print("   |   ");
        Serial.println(masterBrightness);
        turnStripGRB(dimmedGreen, dimmedRed, dimmedBlue);
    }
    else {
        num_on_readings = 0;
        // Serial.print(abs(difference));
        // Serial.print("   -   ");
        // Serial.print(abs(diff_avg));
        // Serial.print("   -   ");
        // Serial.println(pot_reading_avg);
    }
}

