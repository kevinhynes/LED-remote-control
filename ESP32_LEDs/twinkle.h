#include <Arduino.h>
#include <FastLED.h>
#define NUM_COLORS 5

// extern CRGB leds[];

static const CRGB TwinkleColors[NUM_COLORS] =
        {
                CRGB::Red,
                CRGB::Blue,
                CRGB::Purple,
                CRGB::Green,
                CRGB::Yellow
        };

void DrawTwinkle() {
    FastLED.clear(false);
    for (int i=0; i < NUM_LEDS / 4; i++) {
        int index = random(NUM_LEDS);
        int colorIndex = random(NUM_COLORS);
        leds[index] = TwinkleColors[colorIndex];

        Serial.print("Index: ");
        Serial.print(index);
        Serial.print("   Color Index: ");
        Serial.println(colorIndex);

        FastLED.show();
    }
}