from __future__ import print_function
from PIL import Image, ImageDraw
from PIL import ImageTk
import tkinter as tki
import threading
import datetime
import imutils
import cv2
import os


class Live:
    def __init__(self, vs, outputPath):


        self.vs = vs
        self.outputPath = outputPath
        self.frame = None
        self.thread = None
        self.stopEvent = None

        self.root = tki.Tk()
        self.root.resizable(width = False, height = False)

        self.panel = None

        # btn = tki.Button(self.root, text = "Capture operation", command = self.captureImage)
        # btn.pack(side="bottom", fill="both", expand="yes", padx=10, pady=5)
        canvas = tki.Canvas(self.root, height = 80)
        canvas.pack(side = "bottom", fill = "both", expand = "yes", padx = 10)
        x1 = 2
        y1 = 2
        x2 = 800
        y2 = 80
        radius = 25
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]

        canvas.create_polygon(points, fill = "#cd00cd", smooth=True)
        canvas.create_text(100, 20, fill = "black", text = "Hello world")


        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

        self.root.wm_title("BARBIE")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)



    def videoLoop(self):

        try:
            while not self.stopEvent.is_set():
                self.frame = self.vs.read()
                self.frame = imutils.resize(self.frame, width=800)

                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                if self.panel is None:
                    self.panel = tki.Label(image = image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx = 10, pady = 5)

                else:
                    self.panel.configure(image = image)
                    self.panel.image = image

        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")

    def onClose(self):
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()
