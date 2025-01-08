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

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GObject, GstRtspServer

Gst.init(None)

class LocalAudioStreamer:
    def __init__(self, port=8554, mount_point="/audio", codec="vorbis", bitrate=128, device=None):
        self.port = port
        self.mount_point = mount_point
        self.codec = codec
        self.bitrate = bitrate
        self.device_name = device
        self.ip_address = None
        self.server = None
        self.logger = logging.getLogger(__name__)

    def _find_audio_device(self):
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
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.ip_address = s.getsockname()[0]
        except OSError:
            self.ip_address = "127.0.0.1"
            self.logger.warning("Could not determine local IP. Using loopback address.")
        finally:
            s.close()
        self.logger.info(f"Local IP address: {self.ip_address}")

    def start_streaming(self):
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
                raise ValueError(f"Invalid codec: {self.codec}. Supported codecs: {', '.join(codec_elements.keys())}")
            
            launch_string = f"pulsesrc device={self.device_name}.monitor client-name=LocalAudioShare ! audioconvert ! audioresample ! {codec_elements[self.codec]}"
            factory.set_launch(launch_string)
            mounts.add_factory(self.mount_point, factory)
            self.server.attach(None)
            self.logger.info(f"Streaming at rtsp://{self.ip_address}:{self.port}{self.mount_point}")

            loop = GLib.MainLoop()
            loop.run()

        except RuntimeError as e:
            self.logger.error(f"Error: {e}")
        except ValueError as e:
            self.logger.error(f"Configuration Error: {e}")
        except Exception as e:
            self.logger.exception("An unexpected error occurred:")
        finally:
            if self.server:
                self.server = None

    def stop_streaming(self):
        if self.server:
            self.server.close()
            self.server = None
            self.logger.info("Streaming stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream audio over RTSP.")
    parser.add_argument("-p", "--port", type=int, default=8554, help="RTSP port")
    parser.add_argument("-m", "--mount-point", type=str, default="/audio", help="Mount point")
    parser.add_argument("-c", "--codec", type=str, default="vorbis", choices=["vorbis", "opus", "mp3"], help="Audio codec (vorbis, opus, mp3)")
    parser.add_argument("-b", "--bitrate", type=int, default=128, help="Bitrate in kbps")
    parser.add_argument("-d", "--device", type=str, help="Specify audio device name directly")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    streamer = LocalAudioStreamer(port=args.port, mount_point=args.mount_point, codec=args.codec, bitrate=args.bitrate, device=args.device)

    try:
        streamer.start_streaming()
    except KeyboardInterrupt:
        logger.info("Stopping streaming...")
        streamer.stop_streaming()
        logger.info("Exiting.")
