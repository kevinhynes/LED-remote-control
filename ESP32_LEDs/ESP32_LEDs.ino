#include <Arduino.h>
#include <FastLED.h>
#include "BluetoothSerial.h"    // Needed for Bluetooth Serial - works ONLY on ESP32
#include <Preferences.h>        // Needed for keeping NUM_LEDS permanent
#include <TaskScheduler.h>      // Keep animations in separate threads?
#define DATA_PIN 2




Preferences preferences;
BluetoothSerial ESP_BT;
const unsigned int MESSAGE_LENGTH = 6; // in bytes (0-indexed)
uint NUM_LEDS;
CRGB *leds;
uint colorCorrectionKey;
uint colorTemperatureCorrectionKey;
uint maxBrightness;


// Global master values
int mode;
int masterRed = 255;
int masterGreen = 255;
int masterBlue = 255;
int masterBrightness = 255;


// Dimmer / processed values
int dimmedRed = 255;
int dimmedGreen = 255;
int dimmedBlue = 255;


// Global Current Palette... testing
CRGBPalette256 curPalette;
bool animatePalette = false;
uint8_t palStartIndex = 0;  // type keeps values between [0 - 255]
byte *paletteColors;
byte *mirroredPaletteColors;
int animationSpeed = 5;
uint8_t *colorIndex;  // for animatePalette_RandomBreathe()
bool isPaletteNew = true;  // to randomize animatePalette_RandomBreathe()

#include "twinkle.h"
#include "comet.h"
#include "bounce.h"
#include "beat.h"
#include "smooth_draw.h"
#include "color_correction.h"
#include "color_temperature.h"
#include "bluetooth_helpers.h"
#include "saved_data.h"
#include "palettes.h"


CRGBPalette16 fire = heatmapPalette;

void doAnimation()
{
    EVERY_N_MILLISECONDS(animationSpeed)
    {
        if (animatePalette)
        {
            animatePalette_RandomBreathe();
        }
    }
}
Scheduler runner;
Task animationTask(0, TASK_FOREVER, &doAnimation);


void setup() {

    Serial.begin(115200);
    while (!Serial) { }
    Serial.println("ESP32 Startup");

    ESP_BT.begin("ESP32_Test"); //Name of your Bluetooth interface -> will show up on your phone

    preferences.begin("myApp", false);              // Open preferences namespace
    // int clearMessage[6] = {0, 0, 255, 255, 0, 0};
    // setNumLEDs(clearMessage);
    loadSavedData();

    leds = new CRGB[NUM_LEDS];
    pinMode(DATA_PIN, OUTPUT);
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
    colorIndex = new uint8_t[NUM_LEDS];
    FastLED.clear();
    FastLED.show();
    // FastLED.setBrightness(maxBrightness);
    // FastLED.setTemperature(intColorTemperatureCorrectionMap[colorTemperatureCorrectionKey]);
    // FastLED.setCorrection(intColorCorrectionMap[colorCorrectionKey]);
    // FastLED.setCorrection(TypicalLEDStrip);
    // FastLED.setMaxPowerInVoltsAndMilliamps(5, 30000);

    runner.addTask(animationTask);
    animationTask.enable();
}



void loop()
{
    static int message[] = {-1, -1, -1, -1, -1, -1};
    static uint i = 0;
    int cur_byte;
    static int bluetooth_timeout = 1000;
    // static uint8_t palStartIndex = 0;

    if (ESP_BT.available())
    {
        cur_byte = static_cast<int>(ESP_BT.read());
        message[i] = cur_byte;

        // Mode
        if (i == 0)
        {
            Serial.println("##### BEGIN MESSAGE #####");
            Serial.println(cur_byte);
            i = i + 1;
        }

        else if ((1 <= i) && (i < MESSAGE_LENGTH - 2))
        {
            Serial.println(cur_byte);
            i = i + 1;
        }

        else if (i == MESSAGE_LENGTH - 2)
        {
            Serial.println(cur_byte);
            Serial.println("##### END MESSAGE #####");
            i = i + 1;
        }

            // End byte is -1 (actually 255 because idk)
        else
        {
            if (validateMessage(message))
            {
                Serial.println("Valid message received");
                bluetooth_timeout = 1000;
            }
            else
            {
                Serial.println("Invalid message recieved");
            }
            // Reset variables
            resetMessage(message);
            i = 0;
            // while (ESP_BT.available())
            // {
            //   int junk_byte = static_cast<int>(ESP_BT.read());
            // }
        }
    }

    // EVERY_N_MILLISECONDS(50)
    // {
    //   fill_palette(leds, NUM_LEDS, palStartIndex, 1, purplePalette, 200, LINEARBLEND);
    //   palStartIndex += 1;
    //   palStartIndex %= 256;
    //   FastLED.show();
    // }

    // EVERY_N_MILLISECONDS(50)
    // {
    //   if (animatePalette)
    //   {
    //     // doAnimatePalette();
    //     // animatePalette_Breathe();
    //     // animatePalette_Scroll();
    //     animatePalette_RandomBreathe();
    //   }
    // }
    runner.execute();
}
