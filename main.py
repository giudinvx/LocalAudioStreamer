#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging

from src.app import LocalAudioStreamer
from src.window import window

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream audio over RTSP.")
    
    parser.add_argument("-p", "--port", type=int, default=8554, help="RTSP port")
    parser.add_argument("-m", "--mount-point", type=str, default="/audio", help="Mount point")
    parser.add_argument("-c", "--codec", type=str, default="vorbis",
                        choices=["vorbis", "opus", "mp3"], help="Audio codec (vorbis, opus, mp3)")
    parser.add_argument("-b", "--bitrate", type=int, default=128, help="Bitrate in kbps")
    parser.add_argument("-d", "--device", type=str, help="Specify audio device name directly")
    parser.add_argument("-g", "--gui", action="store_true", help="Increase verbosity")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity")
    
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    streamer = LocalAudioStreamer(port=args.port, mount_point=args.mount_point,
                                  codec=args.codec, bitrate=args.bitrate,
                                   device=args.device, gui=args.gui)

    try:
        streamer.start_streaming()
    except KeyboardInterrupt:
        logger.info("Stopping streaming...77")
        streamer.stop_streaming()
        logger.info("Exiting.")
