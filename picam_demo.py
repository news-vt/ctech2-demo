import cv2
import picamera
import picamera.array

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = picamera.array.PiRGBArray(camera, size=camera.resolution)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    # show the frame
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break