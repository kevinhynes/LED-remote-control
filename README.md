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

6/17/23 - must use kivy==2.2.0 for linux
6/18/23 - actually kivymd master branch does work on linux, only kivy is the problem.

#### Developer notes (for future me):
To build the APK file, need to use `buildozer` which only works on Linux.  Use a virtual machine,
then get it set up for the project:

##### Update Linux and clone the repo:
In Home (~) directory:  

`sudo apt update`
`sudo apt install git`
`sudo apt install python3-virtualenv`
`git clone https://github.com/kevinhynes/LED-remote-control`

##### Create and activate virtual environment:
In LED-remote-control directory (separate terminal):  

`virtualenv -p python3 venv`
`. venv/bin/activate`

##### Install buildozer dependencies:
In Home (~) directory:  

`sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev`
`git clone https://github.com/kivy/buildozer`

##### Install buildozer:
In buildozer directory:  

`sudo python3 setup.py install`

##### Install Cython (version may need to be updated):
In Home (~) directory:  

`pip3 install --user --upgrade Cython==0.29.19 virtualenv`  (the --user should be removed if you do this in a venv)

##### Add PATH locations:
In Home (~) directory:  

`gedit .bashrc`
    Add buildozer path to PATH by adding this line to the bottom of .bashrc:
    `export PATH="$PATH:$HOME/.local/bin"`
    Add Java compiler path to JAVA_HOME by adding this line to the bottom of .bashrc:
    `export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"`

##### Install project dependencies:
In LED-remote-control directory:  

`pip3 install kivy==2.2.0`
`pip3 install kivymd`
`pip3 install pyjnius`
...

##### Initialize buildozer:
In LED-remote-control directory:  

`buildozer init`
Then, open and modify buildozer.spec:
    title, package.name, package.domain, requirements, android.logcat filters, android.permissions,

##### Build APK:
In LED-remote-control directory:  

`buildozer android debug`

##### Upload APK to phone:
**Android**:

Put Android device in developer mode, turn on USB debugging.
Go to Settings > About Device > Status and find YOUR_IP.

**Windows**:

Download adb for Windows.
From command prompt where adb.exe is located:
`adb devices`
`adb tcpip 5555`

**Linux**:  

Install adb.  

`adb connect YOUR_IP:5555`
`adb devices -l`
    --> find TRANSPORT_ID
`adb -t TRANSPORT_ID install FILENAME.apk`
Before opening app, run logcat:
`adb -t TRANSPORT_ID logcat *:S python:D`

**NOTE**:  

Android device and computer need to be on the same network for adb to work.