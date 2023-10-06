#include <Arduino.h>
#include <FastLED.h>
#include "BluetoothSerial.h"    // Needed for Bluetooth Serial - works ONLY on ESP32
#include <vector>



class BluetoothManager
{
private:
    BluetoothSerial ESP32_BT;
    int messageLength = 6;
    byte message[6] = {0, 0, 0, 0, 0, 0};
    byte curByte;
    int mi = 0;
    int bluetoothTimeout = 1000;
    LEDManager* ledManager;
    byte* paletteColors;
    byte mode;

public:
    BluetoothManager(LEDManager* ledMgr) : ledManager(ledMgr) {}
    void beginBluetooth()
    {
        ESP32_BT.begin("ESP32_Test"); //Name of your Bluetooth interface -> will show up on your phone
    }

    void readBluetooth()
    {
        if (ESP32_BT.available())
        {
            curByte = ESP32_BT.read();
            message[mi] = curByte;
            mi = mi + 1;
            if (mi == messageLength)
            {
                // End byte is -1 (actually 255 because idk)
                if (validateMessage(message))
                {
                    Serial.println("Valid message received");
                    bluetoothTimeout = 1000;
                }
                else
                {
                    // Erase all incoming Bluetooth data to start over.
                    Serial.println("Invalid message recieved, clearing Bluetooth buffer...");
                    while (ESP32_BT.available())
                    {
                        byte junkByte = ESP32_BT.read();
                    }
                }
                resetMessage(message);
                mi = 0;
            }
        }
    }

    bool validateMessage(byte message[])
    {
        Serial.println("bluetoothManager.validateMessage");
        Serial.println("  message: ");
        printMessage(message);
        for (int j = 0; j < messageLength; j++)
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
            this->ledManager->configure(message);
        }
        // "Color Mode" - change color, keep brightness
        if (mode == 1)
        {
            this->ledManager->updateColor(message);
        }
        // "Dimmer Mode" - keep color, change brightness
        if (mode == 2)
        {
            this->ledManager->updateBrightness(message);
        }
        // Palette
        if (mode == 3)
        {
            receivePaletteColors(message);
        }
        if (mode == 4)
        {
            this->ledManager->animationHelper(message);
        }
        return true;
    }

    void resetMessage(byte message[])
    {
        Serial.println("bluetoothManager.resetMessage");
        for (int i = 0; i < messageLength; i++)
        {
            message[i] = 0;
        }
    }

    void printMessage(byte message[])
    {
        for (int i = 0; i < messageLength; i++)
        {
            Serial.print(message[i]);
            Serial.print(" | ");
        }
        Serial.println(" ");
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

    void receivePaletteColors(byte message[])
    {
        Serial.println("bluetoothManager.receivePaletteColors");
        static int msgNumber = -1;
        static uint numColors;
        static uint width;
        Serial.print("    msgNumber: ");
        Serial.println(msgNumber);

        if (msgNumber == -1)
        {
            // Out with the old..
            delete[] paletteColors;
            paletteColors = nullptr;

            // In with the new..
            numColors = message[1];
            width = 255 / (numColors - 1);
            paletteColors = new byte[numColors * 4];
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
            this->ledManager->loadPalette(paletteColors);
        }
    }
};

