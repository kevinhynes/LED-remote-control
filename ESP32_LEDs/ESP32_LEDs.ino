#include <Arduino.h>
#include <FastLED.h>
#include "BluetoothSerial.h"    // Needed for Bluetooth Serial - works ONLY on ESP32
#include <Preferences.h>        // Needed for keeping NUM_LEDS permanent
#include <TaskScheduler.h>      // Keep animations in separate threads?
#define DATA_PIN 2



Preferences preferences;
uint NUM_LEDS;
// CRGB *leds;
uint colorCorrectionKey;
uint colorTemperatureCorrectionKey;
uint maxBrightness;


// // Global master values
// int mode;
// int masterRed = 255;
// int masterGreen = 255;
// int masterBlue = 255;
// int masterBrightness = 255;


// // Dimmer / processed values
// int dimmedRed = 255;
// int dimmedGreen = 255;
// int dimmedBlue = 255;


// // Global Current Palette... testing
// CRGBPalette256 curPalette;
// bool animatePalette = false;
// uint8_t palStartIndex = 0;  // type keeps values between [0 - 255]
// byte *paletteColors;
// // int animationSpeed = 5;
// uint8_t *colorIndex;  // for animatePalette_RandomBreathe()
// bool isPaletteNew = true;  // to randomize animatePalette_RandomBreathe()


// #include "twinkle.h"
// #include "comet.h"
// #include "bounce.h"
// #include "beat.h"
// #include "smooth_draw.h"
#include "color_correction.h"
#include "color_temperature.h"
// #include "animations.h"
#include "led_manager.h"
#include "bluetooth_manager.h"
#include "saved_data.h"
#include "palettes.h"

Scheduler runner;
LEDManager ledManager = LEDManager();
BluetoothManager bluetoothManager = BluetoothManager(&ledManager);
// TODO: wrapper is hacky/slow?
static void doAnimationWrapper()
{
    ledManager.doAnimation();
}
static void readBluetoothWrapper()
{
    bluetoothManager.readBluetooth();
}
Task animationTask(0, TASK_FOREVER, doAnimationWrapper);
Task bluetoothTask(0, TASK_FOREVER, readBluetoothWrapper);


void setup() {

    Serial.begin(115200);
    while (!Serial) { }
    Serial.println("ESP32 Startup");
    loadSavedData();
    ledManager.initializeLEDs(NUM_LEDS);
    bluetoothManager.beginBluetooth();

    preferences.begin("myApp", false);              // Open preferences namespace
    // int clearMessage[6] = {0, 0, 255, 255, 0, 0};
    // setNumLEDs(clearMessage);

    // leds = new CRGB[NUM_LEDS];
    pinMode(DATA_PIN, OUTPUT);
    // FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
    // colorIndex = new uint8_t[NUM_LEDS];
    FastLED.clear();
    FastLED.show();
    // FastLED.setBrightness(maxBrightness);
    // FastLED.setTemperature(intColorTemperatureCorrectionMap[colorTemperatureCorrectionKey]);
    // FastLED.setCorrection(intColorCorrectionMap[colorCorrectionKey]);
    // FastLED.setCorrection(TypicalLEDStrip);
    // FastLED.setMaxPowerInVoltsAndMilliamps(5, 30000);

    runner.addTask(animationTask);
    animationTask.enable();
    runner.addTask(bluetoothTask);
    bluetoothTask.enable();
}

void loop()
{
    runner.execute();
}
