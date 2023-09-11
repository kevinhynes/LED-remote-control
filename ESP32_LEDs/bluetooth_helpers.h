#include <Arduino.h>
#include <FastLED.h>


//  0 - Configure
//      0 - set NUM_LEDS
//      1 - set type of LEDs (future)
//      2 - set maxBrightness
//      3 - set default color correction
//      4 - set default color temperature correction


void setNumLEDs(int message[])
{
    // To allow NUM_LEDS to be over 255, need to combine 2 bytes.
    int leftBits = message[2];
    int rightBits = message[3];
    leftBits = leftBits << 8;
    int NEW_NUM_LEDS = leftBits + rightBits;

    // Out with the old..
    FastLED.clear();
    FastLED.show();
    delete[] leds;
    leds = nullptr;

    // In with the new
    Serial.print("Updating number of LEDs from ");
    Serial.print(NUM_LEDS);
    Serial.print(" to ");
    NUM_LEDS = NEW_NUM_LEDS;
    Serial.println(NUM_LEDS);

    leds = new CRGB[NUM_LEDS];
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
    preferences.putUInt("NUM_LEDS", NUM_LEDS);
}


void setMaxBrightness(int message[])
{
    int brightness = message[2];
    int curBrightness = preferences.getUInt("maxBrightness", 256);
    Serial.print("Updating maximum brightness from ");
    Serial.print(curBrightness);
    Serial.print(" to ");
    Serial.println(brightness);
    preferences.putUInt("maxBrightness", brightness);
    // I think this should update the LEDs to the new brightness...?
    FastLED.show();
}


void setColorCorrection(int message[])
{
    int key = message[2];
    FastLED.setCorrection(intColorCorrectionMap[key]);
    preferences.putUInt("colorCorrectionKey", key);
    Serial.print("Color corrected to ");
    Serial.println(intColorCorrectionMap[key]);
}


void setColorTemperatureCorrection(int message[])
{
    int key = message [2];
    FastLED.setTemperature(intColorTemperatureCorrectionMap[key]);
    preferences.putUInt("colorTemperatureCorrectionKey", key);
    Serial.print("Color Temperature corrected to ");
    Serial.println(intColorTemperatureCorrectionMap[key]);
}


void configure(int message[])
{
    Serial.println("bluetooth_helpers.configure");
    int option = message[1];
    switch (option)
    {

        // Update & save number of LEDs
        case 0:
            setNumLEDs(message);
            break;
            // Update & save type of LEDs (future)
        case 1:
            Serial.println("Changing LED type not yet implemented");
            break;
            // Update & save max brightness
        case 2:
            setMaxBrightness(message);
            break;
            // Update & save color correction
        case 3:
            setColorCorrection(message);
            break;
            // Update & save color temperature correction
        case 4:
            setColorTemperatureCorrection(message);
            break;
            // Somehow received a value other than [0-4]
            // This is validated on Python / Android side..
        default:
            Serial.println("ERROR: No configuration option matching given integer.");
            break;
    }
}


void palette_helper(int message[])
{
    Serial.println("palette_helper");
};


bool validate_message(int message[])
{
    Serial.println("bluetooth_helpers.validate_message");
    Serial.println("  message: ");
    Serial.print("    ");
    for (int j = 0; j < MESSAGE_LENGTH; j++)
    {
        Serial.print(message[j]);
        Serial.print(" | ");
        if (j == 0)
        {
            if (!(0 <= message[j]) || !(message[j] < 10))
            {
                return false;
            }
        }
        else
        {
            if (!((0 <= message[j]) && (message[j] <= 255)))
            {
                return false;
            }
        }
    }
    Serial.println(" ");
    mode = message[0];
    if (mode == 0)
    {
        configure(message);
    }
    // "Color Mode" - change color, keep brightness
    if (mode == 1)
    {
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
    // Send a palette?
    if (mode == 3)
    {
        palette_helper(message);
    }

    return true;
}

void reset_message(int message[]) {
    for (int j = 0; j < MESSAGE_LENGTH; j++) {
        message[j] = -1;
        Serial.println(message[j]);
    }
}