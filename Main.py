import threading
import pdb
from tkinter import *
from PIL import ImageTk, Image

sys.path.append("..")
import datetime
import os
import cv2
import numpy as np
import tensorflow as tf
import sys

import new_calculator as Calc

from utils import label_map_util as lmu
from utils import visualization_utils as vu
from picamera.array import PiRGBArray
from picamera import PiCamera

try:
    import queue as queue
except ImportError:
    import Queue as queue

import time

# --------------- Only change variables below this line! -----------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# The name of the folder the Frozen Inference Graph is in
FIG_MODEL_FOLDERNAME = 'inference_graph'
# The name of the Frozen Inference Graph file (with extention)
FIG_FILENAME = 'frozen_inference_graph.pb'
# The name of the folder the Labelmap is in
LABELMAP_FOLDERNAME = 'training'
# The name of the Labelmap file (with extention)
LABELMAP_FILENAME = 'labelmap.pbtxt'

# The number of classes the model can detect
NUMBER_OF_CLASSES = 16

# The certainty treshold for a classified object to show (0.0-1.0)
SCORE_TRESHOLD = 0.75


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# --------------- Only change variables above this line! -----------------


# <=~=> Class that implements the Graphical User Interface
class GUI():
    # -> Formula which will be displayed
    formula = ''
    # -> Result which will be displayed
    result = ''

    # --- Main constructor
    # -> threadID helps differentiate between threads
    # -> queue is the shared queue this thread will read from
    # -> exit is the flag which tells the thread to stop
    def __init__(self, queue):
        self.queue = queue
        self.exit = 0

        # Define the Tk window of size 640x600
        self.root = Tk()
        self.root.geometry("640x600")
        self.root.resizable(width=False, height=False)

        # Configure the frame panel and the canvas containing text.
        self.panel = None
        self.canvas = Canvas(self.root, height=280)
        self.canvas.pack(side="bottom", fill="both", expand="yes")

        x1 = 120
        y1 = 50
        x2 = 520
        y2 = 140
        radius = 25
        self.points = [x1 + radius, y1,
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

        # Add the background image
        self.img = Image.open(os.path.abspath("./ProjectImages/image.jpg")).resize((640, 280), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, image=self.image, anchor="nw")

        # Configure the text position
        self.canvas.create_polygon(self.points, fill="#dddddd", smooth=True)
        self.formula_container = self.canvas.create_text(320, 30, fill="black", text="Waiting for formula...")
        self.result_container = self.canvas.create_text(320, 95, fill="black", text="This is the result", font=25)

        self.img2 = Image.open(os.path.abspath("./ProjectImages/image.jpg")).resize((300, 110), Image.ANTIALIAS)
        self.image2 = ImageTk.PhotoImage(self.img2)
        self.image_container = self.canvas.create_image(170, 140, image=self.image2, anchor="nw")
        self.image2_array = None

        # Update the GUI
        self.root.update_idletasks()
        self.root.update()

        print("GUI setup successfully!")

    # --- Basic setter
    # Sets a new value of < formula >
    def setFormula(self, formula):
        self.formula = formula

    # --- Basic setter
    # Sets a new value of < exit >
    def setExit(self, exit):
        self.exit = exit

    # --- Basic setter
    # Sets a new value of < result >
    def setResult(self, result):
        self.result = result

    def setImageWithBoxes(self, newImage):
        # self.canvas.itemconfigure(self.image_container, image = newImage)
        self.image2_array = newImage

    # --- Override the Thread run() method
    # Thread will display frames which are read from the shared queue. Whenever the formula is changed, it will be displayed.
    def run(self):

        print("Starting GUI...")

        while self.exit == 0:

            # Record each frame and process it
            for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):

                # Wait for lock in order to add this frame to the shared queue
                s.acquire()
                while not self.queue.empty():
                    self.queue.get()
                self.queue.put(frame)
                s.release()

                # Convert the frame into a GUI friendly image
                newImage = cv2.cvtColor(frame.array, cv2.COLOR_BGR2RGB)
                newImage = Image.fromarray(newImage)
                newImage = ImageTk.PhotoImage(newImage)

                # Reset the capture
                rawCapture.truncate(0)

                # If no frame was displayed before, add the panel and display the current frame
                if self.panel is None:
                    self.panel = Label(self.root, image=newImage)
                    self.panel.pack(side="bottom", fill=X)
                # Else just configure the panel to display the current frame
                else:
                    self.panel.configure(image=newImage)
                    self.panel.image = newImage

                # If the formula was updated, display it
                if (self.formula != ''):
                    print("I got a formula: " + self.formula)
                    self.canvas.itemconfigure(self.formula_container, text=self.formula)
                    self.formula = ''

                # If the result was updated, display it
                if (self.result != ''):
                    print("I got a result: " + self.result)
                    self.canvas.itemconfigure(self.result_container, text=self.result)
                    self.result = ''

                if self.image2_array is not None:
                    np_array = np.array(self.image2_array)
                    resized = cv2.resize(np_array, None, fx = 0.45, fy = 0.4, interpolation = cv2.INTER_CUBIC)
                    boxImage = Image.fromarray(resized)
                    boxImage = ImageTk.PhotoImage(boxImage)
                    self.canvas.itemconfigure(self.image_container, image=boxImage)
                    self.image2_array = None
                # Update the GUI
                self.root.update_idletasks()
                self.root.update()

        print("GUI shutting down...")

        return


# <=~=> Class that implements the equation recognition and communication with the GPIO.
class backgroundApp(threading.Thread):
    # -> Formula found by character recognition.
    formula = ''

    # -> Exit flag
    exit = 0

    # --- Main constructor
    # -> queue is the shared queue this thread will write to
    # -> threadID helps differentiate between threads
    def __init__(self, threadID, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    # --- Override the Thread run() method
    # Thread will create frames and put them in the shared queue (where the GUI will read them from). For testing purposes, this thread will "find" a formula every 3 frames
    # and send it to the GUI thread.
    def run(self):
        print("Starting background app...")
        while True:
            frame = None
            # Wait for lock in order to retrieve the current frame.
            while frame == None:
                s.acquire()
                frame = self.queue.get()
                s.release()
            print('frame generated!')
            # Convert the frame into a numpy array for further processing.
            input_image = frame.array
            expanded_input_image = np.expand_dims(input_image, axis=0)

            print('starting model')

            (boxes, scores, classes, num) = sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections],
                feed_dict={image_tensor: expanded_input_image})

            items_with_good_percentage = 0
            for item in scores[0]:
                if item >= SCORE_TRESHOLD:
                    items_with_good_percentage += 1
                else:
                    break

            temp_list = []
            for i in range(0, items_with_good_percentage):
                temp_list.append((boxes[0][i][1], classes[0][i]))

            def sortBy(item):
                return item[0]

            sorted_list = sorted(temp_list, key=sortBy)
            formula_array = []

            for item in sorted_list:
                formula_array.append(int(item[1]))

            formula = ""
            for item in formula_array:
                if item <= 9:
                    formula += str(item)
                elif item == 10:
                    formula += '0'
                elif item == 11:
                    formula += '+'
                elif item == 12:
                    formula += '-'
                elif item == 13:
                    formula += '*'
                elif item == 14:
                    formula += '/'
                elif item == 15:
                    formula += '('
                elif item == 16:
                    formula += ')'
            if formula is not "":
                if Calc.check_formula_correct(formula):
                    threadGUI.setFormula(formula)
                    result = Calc.formula_to_array(formula)
                    threadGUI.setResult(str(result))
                else:
                    threadGUI.setFormula("Incorrect Formula, waiting for new formula")
            else:
                threadGUI.setFormula("Waiting for formula")

            image_with_box = input_image
            image_with_box.setflags(write=1)

            #resized = cv2.resize(frame.array, None, fx = 0.125, fy = 0.125, interpolation = cv2.INTER_CUBIC)
            #image_with_box = resized.array

            vu.visualize_boxes_and_labels_on_image_array(
                image_with_box,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                cat_index,
                use_normalized_coordinates=True,
                line_thickness=8,
                min_score_thresh=SCORE_TRESHOLD)

            threadGUI.setImageWithBoxes(image_with_box)


# <== MAIN CODE HERE ==>

# The path to the current directory
CURRENT_DIR = os.getcwd()

# The path to the Frozen Inference Graph
FIG_DIR = os.path.join(CURRENT_DIR, FIG_MODEL_FOLDERNAME, FIG_FILENAME)

# The path to the Labelmap
LABELMAP_DIR = os.path.join(CURRENT_DIR, LABELMAP_FOLDERNAME, LABELMAP_FILENAME)

# Load the labelmap to convert ID numbers the model uses into usable category names
labelmap = lmu.load_labelmap(LABELMAP_DIR)
categories = lmu.convert_label_map_to_categories(labelmap, max_num_classes=NUMBER_OF_CLASSES, use_display_name=True)
cat_index = lmu.create_category_index(categories)

print("Loaded directories, starting to load Tensorflow Model")

# Load the Tensorflow model
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(FIG_DIR, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

print("Tensorflow model loaded, initializing model")

# Define that the input tensor is an image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Define that the wanted output tensors are
# Detection boxes: The parts of the image where an object was detected (and qualified)
# Scores: The percentage of confidence the model has in the correct classification of the detected objects
# Classes: The classification the model has given to the detected object (with the certainty of the score above)
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# The amount of objects detected in the image given as input
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# --- Frame queue that both threads work will access. The GUI thread will read from it while the BackgroundApp thread will write to it.
frameQueue = queue.Queue(0)

# --- Semaphore for allowing certain threads to access shared memory at a time.
s = threading.Semaphore(3)

# --- Setup the Pi Camera
camera = PiCamera()
camera.resolution = (640, 368)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=(640, 368))
time.sleep(0.1)
print("Camera started succesfully!")

# --- Setup the GUI.
threadGUI = GUI(frameQueue)

# --- Setup and start the BackgroundApp thread.
threadBackgroundApp = backgroundApp(2, frameQueue)
threadBackgroundApp.start()

# -- Start the main Thread
threadGUI.run()

# --- Wait for both threads to finish and join them.
threadBackgroundApp.join()

print("DONE!")
