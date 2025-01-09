**Local Audio Streamer**
___
This software allows you to share the audio from your computer with other devices on your network using an RTSP stream. This can be useful in situations where Bluetooth is unavailable or undesirable.  
___
**Requirements:**  

* **GStreamer:** This multimedia framework is required for streaming audio. You can check if it's installed by running the following command in your terminal:

> $ gst-launch-1.0 --gst-version

If GStreamer is not installed, you can find installation instructions online for your specific operating system.  

* **Python 3:** This script requires Python 3 to run. You can check if you have it by running python3 --version in your terminal. If not installed, download it from https://www.python.org/downloads/.  
 
* **PyGObject:** This library allows Python to interact with GStreamer. You can install it using the following command in your terminal:
Bash

> $ pip install PyGObject
___
**Usage:**  

1. **Download the script:** Save the Python script provided earlier as main.py.  

2. **Run the script:** Open your terminal, navigate to the directory where you saved the script, and run the following command:  

> $ python3 main.py -v

The *-v* flag enables verbose output, which will show you information like the available audio devices and the streaming address.  
___
**Expected Output:**

You should see output similar to this in your terminal:  

> [CURRENT DATE] - INFO - Available audio devices:  
> [CURRENT DATE] - INFO -   1: Monitor of Built-in Audio Analog Stereo  
> [CURRENT DATE] - INFO -   2: Built-in Audio Analog Stereo  
> [CURRENT DATE] - INFO -   3: Built-in Audio Analog Stereo  
> [CURRENT DATE] - INFO -   4: Unknown  
> [CURRENT DATE] - INFO - Using default device: alsa_output.pci-0000_00_1b.0.analog-stereo  
> [CURRENT DATE] - INFO - Local IP address: 192.168.1.56  
> [CURRENT DATE] - INFO - Streaming at rtsp://192.168.1.56:8554/audio  
___
**Connecting to the Stream:**  

The script will print the streaming address in the format *rtsp://<your_local_IP_address>:8554/audio*. Open this address in a media player that supports RTSP streams, such as VLC.  You should then be able to hear the audio from your computer playing on the other device.
___
**Additional Notes:**

+ This script streams the audio from your default audio output device. If you have multiple audio devices, you can use the script's command-line arguments to specify a different device.  
+ You may need to adjust firewall settings on your computer and network to allow incoming RTSP connections if you plan to stream from behind a firewall.  




