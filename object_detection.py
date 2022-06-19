# How to install RPi camera:
# https://thepihut.com/blogs/raspberry-pi-tutorials/16021420-how-to-install-use-the-raspberry-pi-camera

# TensorFlow Lite object detection guide.
# https://www.digikey.com/en/maker/projects/how-to-perform-object-detection-with-tensorflow-lite-on-raspberry-pi/b929e1519c7c43d5b2c6f89984883588

import argparse
import urllib.request
import cv2
import threading
import time
from pathlib import Path
import importlib.util

# Import for IoT platform.
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    import tflite_runtime.interpreter as tflite
# Default to full TensorFlow package.
else:
    import tensorflow.lite as tflite



class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(640,480),framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

	# Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
	# Start the thread that reads frames from the video stream
        threading.Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
	# Return the most recent frame
        return self.frame

    def stop(self):
	# Indicate that the camera and thread should be stopped
        self.stopped = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m',
        '--model-file',
        default='/tmp/ssd_mobilenet_v1_1_metadata_1.tflite',
        help='.tflite model to use',
        )
    return parser.parse_args()


if __name__ == '__main__':

    # Get CLI arguments.
    args = parse_args()

    # Create tflite model.
    model_path = Path(args.model_path).expanduser()
    model = tflite.Interpreter(model_path=model_path)

    # Get model details.
    input_details = model.get_input_details()
    output_details = model.get_output_details()

    print(model)

    # # Get input image dimensions.
    # height = input_details[0]['shape'][1]
    # width = input_details[0]['shape'][2]

    # # Setup framerate.
    # freq = cv2.getTickFrequency()

    # # Setup video stream.
    # resolution = (1280, 720) # width x height
    # video_stream = VideoStream(resolution=resolution, framerate=30).start()

    # # Create stream window.
    # cv2.namedWindow('Object Detector', cv2.WINDOW_NORMAL)