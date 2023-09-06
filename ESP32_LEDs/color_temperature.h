#include <Arduino.h>
#include <FastLED.h>


std::map<int, ColorTemperature> intColorTemperatureCorrectionMap =
        {
                {0, Candle},
                {1, Tungsten40W},
                {2, Tungsten100W},
                {3, Halogen},
                {4, CarbonArc},
                {5, HighNoonSun},
                {6, DirectSunlight},
                {7, OvercastSky},
                {8, ClearBlueSky},
                {9, WarmFluorescent},
                {10, StandardFluorescent},
                {11, CoolWhiteFluorescent},
                {12, FullSpectrumFluorescent},
                {13, GrowLightFluorescent},
                {14, BlackLightFluorescent},
                {15, MercuryVapor},
                {16, SodiumVapor},
                {17, MetalHalide},
                {18, UncorrectedTemperature}
        };

std::map<ColorTemperature, String> colorTemperatureCorrectionMap =
        {
                {Candle, "Candle"},
                {Tungsten40W, "Tungsten40W"},
                {Tungsten100W, "Tungsten100W"},
                {Halogen, "Halogen"},
                {CarbonArc, "CarbonArc"},
                {HighNoonSun, "HighNoonSun"},
                {DirectSunlight, "DirectSunlight"},
                {OvercastSky, "OvercastSky"},
                {ClearBlueSky, "ClearBlueSky"},
                {WarmFluorescent, "WarmFluorescent"},
                {StandardFluorescent, "StandardFluorescent"},
                {CoolWhiteFluorescent, "CoolWhiteFluorescent"},
                {FullSpectrumFluorescent, "FullSpectrumFluorescent"},
                {GrowLightFluorescent, "GrowLightFluorescent"},
                {BlackLightFluorescent, "BlackLightFluorescent"},
                {MercuryVapor, "MercuryVapor"},
                {SodiumVapor, "SodiumVapor"},
                {MetalHalide, "MetalHalide"},
                {UncorrectedTemperature, "UncorrectedTemperature"}
        };

int delayTimeCT = 3000;

void DrawTemperatures()
{
    for (const auto& pair : colorTemperatureCorrectionMap) {
        Serial.print(pair.first);
        Serial.print("  -  ");
        Serial.println(pair.second);
        FastLED.clear();
        fill_solid(leds, NUM_LEDS, CRGB::White);
        FastLED.setCorrection(pair.first);
        FastLED.delay(3000);
    }
}

