#include <Arduino.h>
#include <FastLED.h>




void animatePalette_Splatter()
{
    // Formerly 'RandomBreathe'
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
// From Dave's Garage.. this really isn't working and idk wtf is up with it
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


void (*animationFunction)() = animatePalette_Scroll;


void animationHelper(int message[])
{
    Serial.println("animationHelper");
    int animationID = message[1];
    if (animationID == 1)
    {
        Serial.println("    Changing to Breathe");
        animationFunction = animatePalette_Breathe;
    }
    if (animationID == 2)
    {
        Serial.println("    Changing to Scroll");
        animationFunction = animatePalette_Scroll;
    }
    if (animationID == 3)
    {
        Serial.println("    Changing to Splatter");
        animationFunction = animatePalette_Splatter;
    }
}


void doAnimation()
{
    EVERY_N_MILLISECONDS(animationSpeed)
    {
        if (animatePalette)
        {
            animationFunction();
        }
    }
}
