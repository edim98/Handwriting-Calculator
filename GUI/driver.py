from __future__ import print_function
import live
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

pba = live.Live(vs, args["output"])
pba.root.mainloop()
