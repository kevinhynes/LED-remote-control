### Developer notes (for future me):
To build the APK file, need to use `buildozer` which only works on Linux.  Use a virtual machine,
then set it up for the project...
___
#### Update Linux, install Git and clone the project
###### In Home (~) directory:

    sudo apt update
    sudo apt install git
    sudo apt install python3-virtualenv
    git clone https://github.com/kevinhynes/LED-remote-control
___
#### Permissions issue: add username to sudoers file
###### In Home (~) directory:

    $ su
    > Enter password...
    $ visudo -f /etc/sudoers
Then edit the sudoers file:

    # User privilege specification
    root     ALL=(ALL:ALL) ALL
    username ALL=(ALL:ALL) ALL
Save and exit:

    ctrl+o
    enter
    ctrl+x
    exit
___
#### Create and activate virtual environment
###### In LED-remote-control directory (separate terminal):

    virtualenv -p python3 venv
    . venv/bin/activate
___
#### Install buildozer dependencies
###### In Home (~) directory:

    sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
    git clone https://github.com/kivy/buildozer
___
#### Install buildozer
###### In buildozer directory:

    sudo python3 setup.py install
___
#### Install Cython (version may need to be updated)
###### In Home (~) directory:

    pip3 install --user --upgrade Cython==0.29.19 virtualenv
(the --user should be removed if you do this in a venv)
___
#### Add PATH locations
###### In Home (~) directory:

    gedit .bashrc
Add buildozer path to PATH by adding this line to the bottom of `.bashrc`:

    export PATH="$PATH:$HOME/.local/bin"
Add Java compiler path to JAVA_HOME by adding this line to the bottom of `.bashrc`:

    export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
___
#### Install project dependencies
###### In LED-remote-control directory:

    pip3 install kivy==2.2.0
    pip3 install kivymd
    pip3 install pyjnius
    ...
___
#### Initialize buildozer
###### In LED-remote-control directory:

    buildozer init
Then, open and modify buildozer.spec:
title, package.name, package.domain, requirements, android.logcat filters, android.permissions,
___
#### Add syntax highlighting for .kv files

Follow instructions here: 
    https://github.com/noembryo/KV4Jetbrains
___
#### Build APK
###### In LED-remote-control directory:

    buildozer android debug
___
#### Upload APK to phone
###### **Android**:

Put Android device in developer mode, turn on USB debugging.
Go to Settings > About Device > Status and find YOUR_IP.

###### **Windows**:

Download adb for Windows.
From command prompt where adb.exe is located:

    adb devices
    adb tcpip 5555

###### **Linux**:

Install adb.

    adb connect YOUR_IP:5555
    adb devices -l
--> find TRANSPORT_ID

    adb -t TRANSPORT_ID install FILENAME.apk
Before opening app, run logcat:

    adb -t TRANSPORT_ID logcat *:S python:D

###### **Note**:

Android device and computer need to be on the same network for adb to work.

___
### A fly in the ointment...
Problem: https://github.com/kivymd/KivyMD/blob/master/README.md#how-to-fix-a-shader-bug-on-an-android-device

The latest versions of `kivy` and `kivymd` have a bug on Android (?) that can be solved by using
the latest development versions of `kivy` and `kivymd`.

So with your virtual environment activated, do:

    pip3 uninstall kivy
    pip3 uninstall kivymd

then install `kivy` development version:

    pip3 install https://github.com/kivy/kivy/archive/master.zip

Failed building wheel for `kivy`? Could be due to missing `<GL/gl.h>`. Solution:

    sudo apt install libgl-dev

then install `kivymd` development version:

    pip3 install https://github.com/kivymd/KivyMD/archive/master.zip

and replace your `kivy` and `kivymd` requirements in `buildozer.spec` with:

    requirements = kivy==master, https://github.com/kivymd/KivyMD/archive/master.zip

To add to the fun, I can't get the latest development versions of `kivy` and `kivymd` to run on
Ubuntu. But they compiled to an APK successfully and on my phone the app doesn't crash.

To go back to developing on your computer, you'll have to uninstall `kivy` and `kivymd` (as above)
and reinstall:

    pip3 install kivy
    pip3 install kivymd

- 6/17/23 - must use `kivy==2.2.0` for linux
- 6/18/23 - actually `kivymd` master branch does work on linux, only `kivy` is the problem.
- 6/25/23 - **UPDATE** - `buildozer` will download and use whichever packages are listed in the
requirements section of `buildozer.spec` when building the APK, so uninstalling / reinstalling
`kivy` and `kivymd` is not necessary.
- 7/10/23 - must use kivymd=1.1.1 for MDColorPicker to work. Issues with MDDropDownMenu b/w 1.1.1
1.2.0.
- 7/11/23 - UGH MDColorPicker doesn't work on Android with kivymd==1.1.1 or dev branch, even after 
adding olefile to buildozer.spec.  Known bug.  Other  stuff:
  - Create 'rooms' feature to control multiple lights at once?
  - https://github.com/kivy/python-for-android/blob/master/pythonforandroid/recipes/android/src/android/permissions.py