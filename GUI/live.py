from __future__ import print_function
from tkinter import *
from PIL import ImageTk, Image

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

        self.root = Tk()
        self.root.geometry("820x800")
        self.root.resizable(width = False, height = False)

        self.panel = None

        # btn = tki.Button(self.root, text = "Capture operation", command = self.captureImage)
        # btn.pack(side="bottom", fill="both", expand="yes", padx=10, pady=5)

        self.canvas = Canvas(self.root, height = 90)
        self.canvas.pack(side = "bottom", fill = "both", expand = "yes", padx = 5, pady = 5)
        x1 = 5
        y1 = 5
        x2 = 805
        y2 = 85
        radius = 360
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
        self.img = Image.open(os.path.abspath("ProjectImages\image.jpg")).resize((800, 600), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, image = self.image)
        self.canvas.create_polygon(points, fill = "#c7261a", smooth=True, outline = "black", width = 1)
        self.canvas.create_text(405, 30, fill = "black", text = "This is the result:", font = ("Engravers MT", 10))

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

        self.root.wm_title("BARBIE")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.update_idletasks()
        self.root.update()



    def videoLoop(self):

        try:
            while not self.stopEvent.is_set():
                self.frame = self.vs.read()
                self.frame = imutils.resize(self.frame, width=820)

                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                if self.panel is None:
                    self.panel = Label(image = image)
                    self.panel.image = image
                    self.panel.pack()

                else:
                    self.panel.configure(image = image)
                    self.panel.image = image

        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")

    def onClose(self):
        print("[INFO] closing...")
        self.thread.join()
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()
