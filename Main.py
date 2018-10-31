import threading
import pdb
from tkinter import *
from PIL import ImageTk, Image
# import pyttsx3

import datetime
import os
import cv2
import numpy as np
import tensorflow as tf
import sys

from utils import label_map_util as lmu
from utils import visualization_utils as vu
from picamera.array import PiRGBArray
from picamera import PiCamera

try:
    import queue as queue
except ImportError:
    import Queue as queue

import time


#--------------- Only change variables below this line! -----------------
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# The name of the folder the Frozen Inference Graph is in
FIG_MODEL_FOLDERNAME = 'inference_graph'
# The name of the Frozen Inference Graph file (with extention)
FIG_FILENAME = 'frozen_inference_graph.pb'
# The name of the folder the Labelmap is in
LABELMAP_FOLDERNAME = 'training'
# The name of the Labelmap file (with extention)
LABELMAP_FILENAME = 'labelmap.pbtxt'

# The number of classes the model can detect
NUMBER_OF_CLASSES = 14

# The certainty treshold for a classified object to show (0.0-1.0)
SCORE_TRESHOLD = 0.5

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#--------------- Only change variables above this line! -----------------


# <=~=> Class that implements the Graphical User Interface
class GUI():

    # -> formula which will be displayed
    formula = ''

    # --- Main constructor
    # -> threadID helps differentiate between threads
    # -> queue is the shared queue this thread will read from
    # -> exit is the flag which tells the thread to stop
    def __init__(self, queue):
        self.queue = queue
        self.exit = 0

        self.root = Tk()
        self.root.geometry("640x368")
        self.image = ImageTk.PhotoImage(Image.open('./image.jpg').resize((800, 600), Image.ANTIALIAS))
        self.panel = None
        self.panel = Label(self.root, image = self.image)
        self.panel.pack(side = "bottom", fill = X)
        self.root.update_idletasks()
        self.root.update()

    # --- Basic setter
    # Sets a new value of < formula >
    def setFormula(self, formula):
        self.formula = formula

    # --- Basic setter
    # Sets a new value of < exit >
    def setExit(self, exit):
        self.exit = exit

    # --- Override the Thread run() method
    # Thread will display frames which are read from the shared queue. Whenever the formula is changed, it will be displayed.
    def run(self):

        print("Starting GUI...")

        while self.exit == 0:

            s.acquire()
            if self.queue.empty():
                s.release()
            else:
                if self.panel is None:

                frame = self.queue.get()
                s.release()
                newImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                newImage = Image.fromarray(image)
                newImage = ImageTk.PhotoImage(image)

                if self.panel is None:
                    Label(self.root, image = newImage)
                    self.panel.pack(side = "bottom", fill = X)
                else:
                    self.panel.configure(image = newImage)
                    self.panel.image = newImage

                self.root.update_idletasks()
                self.root.update()

                if(self.formula != ''):
                    print("I got a formula: " + self.formula)
                    self.formula = ''

                #time.sleep(1)

                #s.release()

        print("GUI shutting down...")

        return

# <=~=> Class that implements the equation recognition and communication with the GPIO.
class backgroundApp(threading.Thread):

    # -> Random values for formulas.
    #formulas = ['x^2+y^2', '1/3', '3+2']

    #frames = ['./image.jpg', './dog.jpg', './Birds.jpg', './dude.jpg', './trump.jpg', './wow.jpg']

    # -> Formulas queue. Testing purposes.
    formulasQueue = queue.Queue(0)

    # -> Formula found by character recognition.
    formula = ''

    exit = 0

    # --- Main constructor
    # -> queue is the shared queue this thread will write to
    # -> threadID helps differentiate between threads
    def __init__(self, threadID, queue):
        threading.Thread.__init__(self)
        self.queue = queue

        # For testing purposes.
        # for i in range(0, 3):
        #     self.formulasQueue.put(self.formulas[i])
        self.camera = PiCamera()
        self.camera.resolution = (640, 368)
        self.camera.framerate = 24
        self.rawCapture = PiRGBArray(self.camera, size=(640, 368))
        time.sleep(0.1)

    # --- Override the Thread run() method
    # Thread will create frames and put them in the shared queue (where the GUI will read them from). For testing purposes, this thread will "find" a formula every 3 frames
    # and send it to the GUI thread.
    def run(self):
        print("Starting background app...")
        #i = 0
        # #while self.exit == 0:
        # for i in range(0, 6):
        #     s.acquire()
        #     self.queue.put(self.frames[i])
        #     if i % 2 == 0:
        #         while self.formula == '':
        #             self.formula = self.formulasQueue.get()
        #             threadGUI.setFormula(self.formula)
        #         self.formula = ''
        #     time.sleep(1)
        #     if(self.formulasQueue.empty()):
        #         threadGUI.setExit(1)
        #         self.exit = 1
        #     s.release()
        # print("App shutting down...")
        # return

        for frame in self.camera.capture_continuous(self.rawCapture, format = 'bgr', use_video_port = True):
            s.acquire()
            self.queue.put(frame)
            s.release()
            print('frame generated!')
            input_image = frame.formula_array
            expanded_input_image = np.expand_dims(input_image, axis = 0)
            self.rawCapture.truncate(0)
            print('starting model')

            (boxes, scores, classes, num) = sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections],
                feed_dict = {image_tensor: expanded_input_image)}

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

            sorted_list = sorted(temp_list, key = sortBy)
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

            threadGUI.setFormula(formula)

            vu.visualize_boxes_and_labels_on_image_array(
                input_image,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                cat_index,
                use_normalized_coordinates=True,
                line_thickness=8,
                min_score_thresh=SCORE_TRESHOLD)


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
		tf.import_graph_def(od_graph_def, name = '')

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
workQueue = queue.Queue(10)

# --- Semaphore for allowing certain threads to access shared memory at a time.
s = threading.Semaphore(3)

# --- Setup the GUI.
threadGUI = GUI(workQueue)

# --- Setup and start the BackgroundApp thread.
threadBackgroundApp = backgroundApp(2, workQueue)
threadBackgroundApp.start()

# -- Start the main Thread
threadGUI.run()

# --- Wait for both threads to finish and join them.
threadBackgroundApp.join()

print("DONE!")
