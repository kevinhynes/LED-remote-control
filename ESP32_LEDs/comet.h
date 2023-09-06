#include <Arduino.h>
#include <FastLED.h>

// extern CRGB leds[];

void DrawComet()
{
    const byte fadeAmt = 64;
    const int cometSize = 15;
    const int deltaHue  = 4;
    const double cometSpeed = 1.5;

    static byte hue = HUE_RED;
    static int direction = 1;
    static int index = 0;
    static double pos = 1.0;

    hue += deltaHue;
    pos += direction * cometSpeed;
    index = constrain((int)pos, 0, NUM_LEDS - cometSize - 1);

    if (index == (NUM_LEDS - cometSize - 1) || index == 0)
        direction *= -1;

    for (int i = 0; i < cometSize; i++)
        leds[index + i].setHue(hue);

    // Randomly fade the LEDs
    for (int j = 0; j < NUM_LEDS; j++) {
        if (random(2) == 1)
            leds[j] = leds[j].fadeToBlackBy(fadeAmt);
    }

    FastLED.show();
}