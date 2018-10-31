from __future__ import print_function

from threading import Thread

import live
# from picamera.array import PiRGBArray
# from picamera import PiCamera
from imutils.video import VideoStream
import argparse
import time

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True, help="path to output directory")
ap.add_argument("-p", "--picamera", type=int, default=0, help="use/don't use PI camera")
args = vars(ap.parse_args())

print("[INFO] warming up camera...")
vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
time.sleep(2.0)

# class VideoStreamPi:
#         def __init__(self, resolution = (320, 240), framerate = 32):
#             self.camera = PiCamera()
#             self.camera.resolution = resolution
#             self.camera.framerate = framerate
#             self.rawCapture = PiRGBArray(self.camera, size=resolution)
#             self.stream = self.camera.capture_continuous(self.rawCapture,
#                                                          format = "bgr", use_video_port=True)
#             self.frame = None
#             self.stopped = False
#         def start(self):
#             t = Thread(target=self.update, args=())
#             t.daemon = True
#             t.start()
#             return self
#         def update(self):
#             for f in self.stream:
#                 self.frame = f.array
#                 self.rawCapture.truncate(0)
#                 if self.stopped:
#                     self.stream.close()
#                     self.rawCapture.close()
#                     self.camera.close()
#                     return
#         def read(self):
#             return self.frame
#         def stop(self):
#             self.stopped = True
# vs = VideoStreamPi()
pba = live.Live(vs, args["output"])
pba.root.mainloop()
