#include <Arduino.h>
#include <FastLED.h>


void loadSavedData()
{
    // Number of LEDs
    NUM_LEDS = preferences.getUInt("NUM_LEDS", 0);  // Load with default value
    if (NUM_LEDS == 0)
    {
        Serial.println("NUM_LEDS read as 0, resetting to default value");
        NUM_LEDS = 144;
    }
    else
    {
        Serial.print("NUM_LEDS read as: ");
        Serial.println(NUM_LEDS);
    }

    // Max Brightness
    maxBrightness = preferences.getUInt("maxBrightness", 256);
    if (maxBrightness == 256)
    {
        Serial.println("maxBrightness not set, setting to 100");
        maxBrightness = 100;
    }
    else
    {
        Serial.print("maxBrightness read as: ");
        Serial.println(maxBrightness);
    }

    // Color Correction
    colorCorrectionKey = preferences.getUInt("colorCorrectionKey", 5);
    if (colorCorrectionKey == 5)
    {
        Serial.println("colorCorrectionKey not set, setting to Uncorrected Color");
        colorCorrectionKey = 4;
    }
    else
    {
        Serial.print("colorCorrectionKey read as: ");
        Serial.println(colorCorrectionKey);
    }

    // Color Temperature Correction
    colorTemperatureCorrectionKey = preferences.getUInt("colorTemperatureCorrectionKey", 19);
    if (colorTemperatureCorrectionKey == 19)
    {
        Serial.println("colorTemperatureCorrectionKey not set, setting to Uncorrected Temperature");
        colorTemperatureCorrectionKey = 18;
    }
    else
    {
        Serial.print("colorTemperatureCorrectionKey read as: ");
        Serial.println(colorTemperatureCorrectionKey);
    }
}
