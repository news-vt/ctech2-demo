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
import numpy as np

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
        '--model-path',
        default='/tmp/ssd_mobilenet_v1_1_metadata_1.tflite',
        help='.tflite model to use',
        )
    parser.add_argument(
        '-l',
        '--labels-path',
        default='/tmp/labelmap.txt',
        help='.txt labels file to use',
        )
    parser.add_argument(
        '-r',
        '--rotate',
        choices=['0', '90', '180', '270'],
        default='0',
        help='image rotation',
        )
    return parser.parse_args()




import picamera
import picamera.array

# camera = picamera.PiCamera()
# camera.resolution = (640, 480)
# camera.framerate = 32
# rawCapture = picamera.array.PiRGBArray(camera, size=(640, 480))

# # capture frames from the camera
# for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
#     # grab the raw NumPy array representing the image, then initialize the timestamp
#     # and occupied/unoccupied text
#     image = frame.array
#     # show the frame
#     cv2.imshow("Frame", image)
#     key = cv2.waitKey(1) & 0xFF
#     # clear the stream in preparation for the next frame
#     rawCapture.truncate(0)
#     # if the `q` key was pressed, break from the loop
#     if key == ord("q"):
#         break


if __name__ == '__main__':

    # Get CLI arguments.
    args = parse_args()

    rotate = args.rotate
    min_conf_threshold = 0.5

    # Get labels.
    labels_path = str(Path(args.labels_path).expanduser())
    with open(labels_path, 'r') as f:
        labels = [line.strip() for line in f]
    print(labels)

    # Create tflite model.
    model_path = str(Path(args.model_path).expanduser())
    model = tflite.Interpreter(model_path=model_path)
    model.allocate_tensors()

    # Get model details.
    input_details = model.get_input_details()
    output_details = model.get_output_details()

    # Get input image dimensions.
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    floating_model = (input_details[0]['dtype'] == np.float32)
    input_mean = 127.5
    input_std = 127.5

    # Setup framerate.
    frame_rate_calc = 1
    freq = cv2.getTickFrequency()

    # Setup video stream.
    resolution = (1280, 720) # width x height
    # resolution = (640, 480) # width x height
    imW, imH = resolution # Unpack resolution parameters.
    # videostream = VideoStream(resolution=resolution, framerate=30).start()

    # Create stream window.
    cv2.namedWindow('Object Detector', cv2.WINDOW_NORMAL)

    camera = picamera.PiCamera()
    camera.resolution = resolution
    camera.framerate = 32
    rawCapture = picamera.array.PiRGBArray(camera, size=resolution)
    for frame1 in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    #
    #
    # while True:
        frame1 = frame1.array
        rawCapture.truncate(0)

        # Start timer (for calculating frame rate)
        t1 = cv2.getTickCount()

        # # Grab frame from video stream
        # frame1 = videostream.read()

        # Rotate frame if necessary.
        if rotate != '0':
            frame1 = cv2.rotate(frame1, getattr(cv2, f'ROTATE_{rotate}'))

        # Acquire frame and resize to expected shape [1xHxWx3]
        frame = frame1.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        model.set_tensor(input_details[0]['index'],input_data)
        model.invoke()

        # Retrieve detection results
        boxes = model.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = model.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
        scores = model.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
        #num = model.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))
                
                cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
                
                # Draw label
                object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

                # Draw circle in center
                xcenter = xmin + (int(round((xmax - xmin) / 2)))
                ycenter = ymin + (int(round((ymax - ymin) / 2)))
                cv2.circle(frame, (xcenter, ycenter), 5, (0,0,255), thickness=-1)

                # Print info
                print('Object ' + str(i) + ': ' + object_name + ' at (' + str(xcenter) + ', ' + str(ycenter) + ')')

        # Draw framerate in corner of frame
        cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)

        # All the results have been drawn on the frame, so it's time to display it.
        cv2.imshow('Object detector', frame)

        # Calculate framerate
        t2 = cv2.getTickCount()
        time1 = (t2-t1)/freq
        frame_rate_calc= 1/time1

        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break

    # Clean up
    cv2.destroyAllWindows()
    # videostream.stop()