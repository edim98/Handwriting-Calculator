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
        self.root.geometry("640x600")
        self.root.resizable(width = False, height = False)

        self.panel = None

        # btn = tki.Button(self.root, text = "Capture operation", command = self.captureImage)
        # btn.pack(side="bottom", fill="both", expand="yes", padx=10, pady=5)

        self.canvas = Canvas(self.root, height = 250)
        self.canvas.pack(side = "bottom", fill = "both", expand = "yes")
        x1 = 120
        y1 = 50
        x2 = 520
        y2 = 140
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
        self.img = Image.open(os.path.abspath("ProjectImages\image.jpg")).resize((640, 250), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, image = self.image, anchor = "nw")
        self.canvas.create_polygon(points, fill = "#dddddd", smooth=True)
        self.canvas.create_text(325, 30, fill = "black", text = "This is the result:", font = ("Engravers MT", 10))
        self.img2 = Image.open(os.path.abspath("ProjectImages\image.jpg")).resize((300, 110), Image.ANTIALIAS)
        self.image2 = ImageTk.PhotoImage(self.img2)
        self.canvas.create_image(170, 140, image = self.image2, anchor = "nw")

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
                self.frame = imutils.resize(self.frame, width=640, height = 480)

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
