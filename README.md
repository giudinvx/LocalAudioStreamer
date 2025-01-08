**Local Audio Streamer**
___
This software let you share your pc audio through an RTSP stream.  
You can use it in case there is no Bluetooth device or just don't want use it.  
An RTSP program is needed, I advice VLC
___
**Prerequisites**

You need GStreamer lib on your pc, check with:
> $ gst-launch-1.0 --gst-version
___

**Install**

The *PyGObject* is needed:

> $ pip install -r requirements.txt
___
**Usage**

Just launch from terminal:
> $ python3 main.py -v

You should get something like this:

> $ python3 main.py -v  
[CURRENT DATE] - INFO - Available audio devices:  
[CURRENT DATE] - INFO -   1: Monitor of Built-in Audio Analog Stereo  
[CURRENT DATE] - INFO -   2: Built-in Audio Analog Stereo  
[CURRENT DATE] - INFO -   3: Built-in Audio Analog Stereo  
[CURRENT DATE] - INFO -   4: Unknown  
[CURRENT DATE] - INFO - Using default device: alsa_output.pci-0000_00_1b.0.analog-stereo  
[CURRENT DATE] - INFO - Local IP address: 192.168.1.56  
[CURRENT DATE] - INFO - Streaming at rtsp://192.168.1.56:8554/audio  

 Then just open the streaming link with vlc or something similar
