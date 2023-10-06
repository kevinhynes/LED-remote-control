#include <Arduino.h>
#include <FastLED.h>


// Using map for visual indication.  Integers will be
// sent from Android app to get color correction value.
std::map<int, LEDColorCorrection> intColorCorrectionMap =
        {
                {0, TypicalSMD5050},
                {1, TypicalLEDStrip},
                {2, Typical8mmPixel},
                {3, TypicalPixelString},
                {4, UncorrectedColor},
        };

std::map<LEDColorCorrection, String> colorCorrectionMap =
        {
                {TypicalSMD5050, "TypicalSMD5050"},
                {TypicalLEDStrip, "TypicalLEDStrip"},
                {Typical8mmPixel, "Typical8mmPixel"},
                {TypicalPixelString, "TypicalPixelString"},
                {UncorrectedColor, "UncorrectedColor"},
        };


// int delayTimeCC = 3000;

// void DrawCorrections()
// {
//   for (const auto& pair : colorCorrectionMap) {
//     Serial.print(pair.first);
//     Serial.print("  -  ");
//     Serial.println(pair.second);
//     FastLED.clear();
//     fill_solid(leds, NUM_LEDS, CRGB::White);
//     FastLED.setCorrection(pair.first);
//     FastLED.delay(3000);
//   }
// }




