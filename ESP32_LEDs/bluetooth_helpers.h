#include <Arduino.h>
#include <FastLED.h>
#include <vector>

//  Mode 0 - Configure
//            0 - set NUM_LEDS
//            1 - set type of LEDs (future)
//            2 - set maxBrightness
//            3 - set default color correction
//            4 - set default color temperature correction
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

    // Reset colorIndex array for animatePalette_RandomBreathe()
    delete[] colorIndex;
    colorIndex = nullptr;
    colorIndex = new uint8_t[NUM_LEDS];
    for (int i = 0; i < NUM_LEDS; i++)
    {
        colorIndex[i] = random8();
    }

    FastLED.clear();
    FastLED.show();
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
    FastLED.show();
}

void setColorTemperatureCorrection(int message[])
{
    int key = message [2];
    FastLED.setTemperature(intColorTemperatureCorrectionMap[key]);
    preferences.putUInt("colorTemperatureCorrectionKey", key);
    Serial.print("Color Temperature corrected to ");
    Serial.println(intColorTemperatureCorrectionMap[key]);
    FastLED.show();
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



//  Mode 1 - Update Color
//             byte0       byte1        byte2       byte3       byet4      byte5
//  Message:     1          red         green       blue        junk        end
void updateColor(int message[])
{
    Serial.println("updateColor");
    animatePalette = false;
    masterRed = message[1];
    masterGreen = message[2];
    masterBlue = message[3];
    dimmedRed = int(masterRed * masterBrightness / 255);
    dimmedGreen = int(masterGreen * masterBrightness / 255);
    dimmedBlue = int(masterBlue * masterBrightness / 255);
    fill_solid(leds, NUM_LEDS, CRGB(dimmedRed, dimmedGreen, dimmedBlue));
    FastLED.show();
}


//  Mode 2 - Update Brightness
//             byte0       byte1        byte2       byte3       byet4      byte5
//  Message:     2      brightness      junk        junk        junk        end
void updateBrightness(int message[])
{
    Serial.println("updateBrightness");
    // animatePalette = false;
    masterBrightness = message[1];
    dimmedRed = int(masterRed * masterBrightness / 255);
    dimmedGreen = int(masterGreen * masterBrightness / 255);
    dimmedBlue = int(masterBlue * masterBrightness / 255);
    // Update animated palette brightness if running, otherwise update solid color brightness.
    if (!animatePalette)
    {
        fill_solid(leds, NUM_LEDS, CRGB(dimmedRed, dimmedGreen, dimmedBlue));
        FastLED.show();
    }
}



//  3 - Palettes
//  Need to send multiple messages in order to get all the data for colors
//                   byte0      byte1         byte2       byte3       byet4      byte5
//  First Message:     3      num_colors      junk        junk        junk        end
//  Color Messages:    3         red          green       blue        junk        end
void animatePalette_RandomBreathe()
{
    if (isPaletteNew)
    {
        for (int i = 0; i < NUM_LEDS; i++)
        {
            colorIndex[i] = random8();
        }
        isPaletteNew = false;
    }
    for (int i = 0; i < NUM_LEDS; i++)
    {
        CRGB thisColor = ColorFromPalette(curPalette, colorIndex[i]);
        for (int j = 0; j < 3; j++)
        {
            thisColor[j] = int(thisColor[j] * masterBrightness / 255);
        }
        leds[i] = thisColor;
        colorIndex[i]++;
    }
    FastLED.show();
}

void animatePalette_Breathe()
{
    static uint8_t palIndex = 0;
    CRGB fillColor = ColorFromPalette(curPalette, palIndex);
    for (int i = 0; i < 3; i++)
    {
        fillColor[i] = int(fillColor[i] * masterBrightness / 255);
    }
    fill_solid(leds, NUM_LEDS, fillColor);
    palIndex += 1;
    FastLED.show();
}

void animatePalette_Scroll()
{
    static uint8_t palStartIndex = 0;
    fill_palette(leds, NUM_LEDS, palStartIndex, max((uint)1, 255 / NUM_LEDS), curPalette, masterBrightness, LINEARBLEND);
    palStartIndex += 1;
    FastLED.show();
}

void animatePalette_Scroll2()
{
    FastLED.clear();
    static uint8_t palStartIndex = 0;
    static uint8_t palIndex = 0;
    palIndex = palStartIndex;
    for (int i = 0; i < NUM_LEDS; i+= 1)
    {
        CRGB pixelColor = ColorFromPalette(curPalette, palIndex);
        for (int j = 0; j < 3; j++)
        {
            pixelColor[j] = int(pixelColor[j] * masterBrightness / 255);
        }
        leds[i] = pixelColor;
        palIndex += 1;
    }
    palStartIndex += 1;
    FastLED.show();
}

void animatePalette_SmoothScroll()
{
    // DrawPixel is, and should be, additive for each color in leds.
    // Therefore need to clear it on each iteration or it will turn
    // fully white after a few iterations.
    FastLED.clear();
    // Draw a "pixel" of width 1 from a fractional starting point.
    // palStartIndex - keep track of what color to start first
    // pixel at.
    // palIndex - iterate through the palette and apply to next pixel.
    // scroll - how much each pixel moves per loop.
    static uint8_t palStartIndex = 0;
    static uint8_t palIndex = 0;
    static float scroll = 0.0f;
    scroll += 0.1f;
    if (scroll > 1.0)
    {
        scroll = 0.0;
        // palStartIndex += 1;
    }
    palIndex = palStartIndex;
    for (float i = scroll; i < NUM_LEDS; i+= 1)
    {
        CRGB pixelColor = ColorFromPalette(curPalette, palIndex);
        for (int j = 0; j < 3; j++)
        {
            pixelColor[j] = int(pixelColor[j] * masterBrightness / 255);
        }
        DrawPixels(i, 1, pixelColor);
        palIndex += 1;
    }
    palStartIndex += 1;
    FastLED.show();
}

// void doAnimatePalette()
// {
//   FastLED.clear();
//   static uint8_t palIndex = 0;
//   static float scroll = 0.0f;
//   scroll += 0.05f;
//   if (scroll > 1.0)
//     scroll = 0;

//   for (float i = scroll; i < NUM_LEDS; i+= 1)
//   {
//     DrawPixels(i, 1, ColorFromPalette(curPalette, palIndex));
//   }
//   palIndex += 1;
//   FastLED.show();
// }

void showPalette()
{
    Serial.println("showPalette");
    animatePalette = true;
    FastLED.show();
}

void buildPalette(int numColors)
{
    Serial.println("buildPalette");
    isPaletteNew = true;
    curPalette.loadDynamicGradientPalette(paletteColors);
}

void printPalette(int numColors)
{
    Serial.println("printPalette");
    Serial.println("  paletteColors:");
    for (int i = 0; i < numColors * 4; i+= 4)
    {
        for (int j = i; j < i + 4; j++)
        {
            Serial.print(paletteColors[j]);
            Serial.print(" | ");
        }
        Serial.println(" ");
    }
}

void paletteHelper(int message[])
{
    Serial.println("paletteHelper");
    static int msgNumber = -1;
    static uint numColors;
    static uint width;
    Serial.print("    msgNumber: ");
    Serial.println(msgNumber);

    if (msgNumber == -1)
    {
        // Out with the old..
        delete[] paletteColors;
        delete[] mirroredPaletteColors;

        paletteColors = nullptr;
        mirroredPaletteColors = nullptr;

        // In with the new..
        numColors = message[1];
        width = 255 / (numColors - 1);
        paletteColors = new byte[numColors * 4];
        mirroredPaletteColors = new byte[numColors * 4 * 2];
        Serial.print("  numColors: ");
        Serial.println(numColors);
        msgNumber += 1;
    }
    else
    {
        Serial.print("    ");
        byte red = static_cast<byte>(message[1]);
        byte green = static_cast<byte>(message[2]);
        byte blue = static_cast<byte>(message[3]);
        int index = msgNumber * 4;
        for (int i = 0; i < 4; i++)
        {
            if (i == 0)
            {
                if (msgNumber == numColors - 1)
                {
                    paletteColors[index + i] = 255;
                }
                else
                {
                    byte pos = width * msgNumber;
                    paletteColors[index + i] = pos;
                }
            }
            else
            {
                paletteColors[index + i] = message[i];
            }
        }
        msgNumber += 1;
    }
    if (msgNumber == numColors)
    {
        msgNumber = -1;
        printPalette(numColors);
        buildPalette(numColors);
        showPalette();
    }
}


void printMessage(int message[])
{
    for (int i = 0; i < MESSAGE_LENGTH; i++)
    {
        Serial.print(message[i]);
        Serial.print(" | ");
    }
    Serial.println(" ");
}


bool validateMessage(int message[])
{
    Serial.println("bluetooth_helpers.validate_message");
    Serial.println("  message: ");
    printMessage(message);
    for (int j = 0; j < MESSAGE_LENGTH; j++)
    {
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
    mode = message[0];
    if (mode == 0)
    {
        configure(message);
    }
    // "Color Mode" - change color, keep brightness
    if (mode == 1)
    {
        updateColor(message);
    }
    // "Dimmer Mode" - keep color, change brightness
    if (mode == 2)
    {
        updateBrightness(message);
    }
    // Send a palette?
    if (mode == 3)
    {
        paletteHelper(message);
    }
    return true;
}


void resetMessage(int message[])
{
    Serial.println("Resetting message...");
    for (int i = 0; i < MESSAGE_LENGTH; i++) {
        message[i] = -1;
    }
    printMessage(message);
}