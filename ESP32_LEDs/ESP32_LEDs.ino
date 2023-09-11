#include <Arduino.h>
#include <FastLED.h>
#define FASTLED_INTERNAL
#include "BluetoothSerial.h"    // Needed for Bluetooth Serial - works ONLY on ESP32
#include <Preferences.h>        // Needed for keeping NUM_LEDS permanent
#define DATA_PIN 2


Preferences preferences;
BluetoothSerial ESP_BT;
const unsigned int MESSAGE_LENGTH = 6; // in bytes (0-indexed)
unsigned int NUM_LEDS;
CRGB *leds;
unsigned int colorCorrectionKey;
unsigned int colorTemperatureCorrectionKey;
unsigned int maxBrightness;


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


#include "twinkle.h"
#include "comet.h"
#include "bounce.h"
#include "beat.h"
#include "color_correction.h"
#include "color_temperature.h"
#include "bluetooth_helpers.h"
#include "saved_data.h"
#include "palettes.h"

CRGBPalette16 fire = heatmapPalette;

void setup() {

    Serial.begin(115200);
    while (!Serial) { }
    Serial.println("ESP32 Startup");

    ESP_BT.begin("ESP32_Test"); //Name of your Bluetooth interface -> will show up on your phone

    preferences.begin("myApp", false);              // Open preferences namespace
    loadSavedData();

    leds = new CRGB[NUM_LEDS];
    pinMode(DATA_PIN, OUTPUT);
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
    FastLED.clear();
    FastLED.show();
    FastLED.setBrightness(maxBrightness);
    FastLED.setTemperature(intColorTemperatureCorrectionMap[colorTemperatureCorrectionKey]);
    // FastLED.setCorrection(intColorCorrectionMap[colorCorrectionKey]);
    FastLED.setCorrection(TypicalLEDStrip);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, 30000);
}



void loop()
{
    static int message[] = {-1, -1, -1, -1, -1, -1};
    static unsigned int i = 0;
    int cur_byte;
    static int bluetooth_timeout = 1000;
    static uint8_t palStartIndex = 0;

    if (ESP_BT.available())
    {
        cur_byte = static_cast<int>(ESP_BT.read());
        message[i] = cur_byte;

        // Mode
        if (i == 0)
        {
            Serial.println("###############################");
            Serial.println(cur_byte);
            i = i + 1;
        }

            // RGB
        else if ((1 <= i) && (i < MESSAGE_LENGTH - 2))
        {
            Serial.println(cur_byte);
            i = i + 1;
        }

            // Alpha
        else if (i == MESSAGE_LENGTH - 2)
        {
            Serial.println(cur_byte);
            Serial.println("###############################");
            i = i + 1;
        }

            // End byte is -1 (actually 255 because idk)
        else
        {
            if (validate_message(message))
            {
                Serial.println("Valid message received");
                // turnStripRGB(dimmedRed, dimmedGreen, dimmedBlue);
                fill_solid(leds, NUM_LEDS, CRGB(dimmedRed, dimmedGreen, dimmedBlue));
                bluetooth_timeout = 1000;
            }
            else
            {
                Serial.println("Invalid message recieved");
            }
            // // Reset variables
            Serial.println("Resetting message...");
            i = 0;
            reset_message(message);
            while (ESP_BT.available())
            {
                int junk_byte = static_cast<int>(ESP_BT.read());
            }
        }
    }

    // EVERY_N_MILLISECONDS(50)
    // {
    //   palStartIndex += 1;
    //   fill_palette(leds, NUM_LEDS, palStartIndex, max((uint)1, 255 / NUM_LEDS), purplePalette, 200, LINEARBLEND);
    //   FastLED.show();
    // }

}
