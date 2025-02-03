#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  Share your pc audio in form of RTSP
#  Copyright (C) 2025 <giudinvx[at]gmail[dot]com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
import socket
import gi
import argparse
import logging
import subprocess
import threading

try:
    gi.require_version('Gst', '1.0')
    gi.require_version('GstRtspServer', '1.0')
    from gi.repository import Gst, GLib, GObject, GstRtspServer
    
    GObject.threads_init() # for GStreamer threading
    Gst.init(None)
except ImportError or ValueError as exc:
    print('Error: Dependencies not met.', exc)
    exit()
     
class LocalAudioStreamer:
    """
    Shares the current audio playback on the PC as an RTSP stream.
    """
    def __init__(self, port=8554, mount_point="/audio", codec="vorbis",
				 bitrate=128, device=None, gui=None):
        """
        Initializes the AudioStreamer with default port, mount point, codec, bitrate and device.

        Args:
            port (int, optional): The port to listen on for RTSP connections.
                                  Defaults to 8554.
            mount_point (str, optional): The mount point for the RTSP stream.
                                         Defaults to "/audio".
            codec (str, optional): The codec for encoding the audio.
                                   Defults to vorbis.
            bitrate (int, optional): The bitrate for the audio.
                                     Defults to 128.
            device (str): The system's default audio input device.
                          Defults to None.
        """
        self.port = port
        self.mount_point = mount_point
        self.codec = codec
        self.bitrate = bitrate
        self.device_name = device
        self.gui = gui
        self.ip_address = None
        self.server = None
        self.logger = logging.getLogger(__name__)

    def _find_audio_device(self):
        """
        Find the system's default input device or choose one
        """
        if self.device_name:
            self.logger.info(f"Using specified device: {self.device_name}")
            return # Use specified device

        monitor = Gst.DeviceMonitor.new()
        monitor.start()
        devices = monitor.get_devices()

        if devices:
            self.logger.info("Available audio devices:")
            for i, device in enumerate(devices):
                props = device.get_properties()
                name = props.get_string("device.description") or props.get_string("device.nick") or "Unknown"
                self.logger.info(f"  {i+1}: {name}")

        for device in devices:
            if device.get_device_class() == "Audio/Sink" and device.get_properties().get_value("is-default"):
                element = device.create_element()
                self.device_name = element.get_properties("device")[0]
                self.logger.info(f"Using default device: {self.device_name}")
                break

        monitor.stop()

        if not self.device_name:
            raise RuntimeError("No audio sink device found. Please specify one using --device.")


    def _get_local_ip(self):
        """
        Find your device's IP address
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to a public DNS server
            self.ip_address = s.getsockname()[0]
        except OSError:
            try:
                # Fallback for systems without internet connectivity.
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.connect(('<broadcast>', 12345))
                self.ip_address = s.getsockname()[0]
            except OSError:
                self.ip_address = "127.0.0.1" # Default to loopback if all else fails
                print("Could not determine local IP. Using loopback address.")
        finally:
            s.close()
        self.logger.info(f"Local IP address: {self.ip_address}")

    def start_streaming(self):
        """
        Creates and configures the RTSP server.
        Starts the audio streaming.
        """
        try:
            self._find_audio_device()
            self._get_local_ip()

            self.server = GstRtspServer.RTSPServer.new()
            self.server.set_service(str(self.port))
            
            mounts = self.server.get_mount_points()
            
            factory = GstRtspServer.RTSPMediaFactory.new()

            codec_elements = {
              "vorbis": f"vorbisenc bitrate={self.bitrate*1000} ! rtpvorbispay name=pay0 pt=96",
              "opus": f"opusenc bitrate={self.bitrate*1000} ! rtpopuspay name=pay0 pt=97",
              "mp3": f"lamemp3enc target=bitrate bitrate={self.bitrate} ! rtpmpapay name=pay0 pt=98"
            }
            if self.codec not in codec_elements:
                raise ValueError(f"Invalid codec: {self.codec}. Supported codecs: {','.join(codec_elements.keys())}")

            launch_string = f"pulsesrc device={self.device_name}.monitor client-name=LocalAudioShare !\
                             audioconvert ! audioresample ! {codec_elements[self.codec]}"
            factory.set_launch(launch_string)
            mounts.add_factory(self.mount_point, factory)
            self.server.attach(None)
               
            self.logger.info(f"Streaming at rtsp://{self.ip_address}:{self.port}{self.mount_point}")
            
            # Start the GLib main loop in a separate thread
            self.loop = GLib.MainLoop()  # Store the loop as an instance variable
            self.loop_thread = threading.Thread(target=self.loop.run)  # Create a thread
            self.loop_thread.daemon = True # Allow application to exit even if thread is running
            self.loop_thread.start() #Start the thread

            if self.gui:
                from .window import window
                window_gui = window(self)  # Pass self
                window_gui.start_gui()  # GUI starts here
            else:  # Terminal-only mode
                # Keep the main thread alive until the stream finishes or an error occurs
                try:
                    self.loop_thread.join() # Wait for the thread to stop, this is important
                except KeyboardInterrupt:
                    pass # Allow Ctrl+C to exit
                finally: # Ensure proper cleanup
                    self.stop_streaming() # Stop streaming when finished
                    
        except Exception as e:
            self.logger.exception("Error in start_streaming:")
        finally:  # Ensure proper cleanup
            if self.server:
                self.stop_streaming()  # Call stop_streaming in finally
                
    def stop_streaming(self):
        if self.server:
            print("Stopping streaming...")
            GLib.idle_add(self._stop_streaming_internal)  # Use idle_add

    def _stop_streaming_internal(self):
        if self.server:
            self.server.close()
            self.server = None
            if self.loop and self.loop.is_running():
                self.loop.quit()
            if self.loop_thread and self.loop_thread.is_alive():
                self.loop_thread.join() # Wait for the thread to fully stop
