# LED-remote-control



Problem: https://github.com/kivymd/KivyMD/blob/master/README.md#how-to-fix-a-shader-bug-on-an-android-device

Seems the latest versions of kivy and kivymd have a bug on Android (?) that can be solved by using the latest development versions of kivy and kivymd.

So with your virtual environment activated, do:

pip3 uninstall kivy
pip3 uninstall kivymd

then:

pip3 install https://github.com/kivy/kivy/archive/master.zip
    > Failed building wheel for Kivy? 
        - Due to missing <GL/gl.h>
            - Solution: `sudo apt install libgl-dev`
pip3 install https://github.com/kivymd/KivyMD/archive/master.zip

and replace your kivy and kivymd requirements in buildozer.spec with:

requirements = kivy==master, https://github.com/kivymd/KivyMD/archive/master.zip

To add to the fun, I can't get the latest development versions of kivy and kivymd to run on Ubuntu. But they compiled to an APK successfully and on my phone the app doesn't crash.

To go back to developing on your computer, you'll have to uninstall kivy and kivymd (as above) and reinstall:

pip3 install kivy
pip3 install kivymd

