import datetime
import time
import os
import cv2
import numpy as np
import tensorflow as tf
import sys

from utils import label_map_util as lmu
from utils import visualization_utils as vu
from picamera.array import PiRGBArray
from picamera import PiCamera

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

print("Formula_detection.py started")

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

# Initialise PiCamera
camera = PiCamera()
camera.resolution = (640, 368)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size = (640, 368))

time.sleep(0.1)

# Get the camera input and start the model on it
for frame in camera.capture_continuous(rawCapture, format = 'bgr', use_video_port = True):
	print("frame")

	# Get the input image for the model
	input_image = frame.array
	expanded_input_image = np.expand_dims(input_image, axis = 0)

	# cv2.imshow("Frame", input_image)

	rawCapture.truncate(0)


	print("Starting model")

	# Let the model actually run on the input image, and gain the output values
	(boxes, scores, classes, num) = sess.run(
		[detection_boxes, detection_scores, detection_classes, num_detections],
		feed_dict = {image_tensor: expanded_input_image})

	# Get the formula recognised on the input image and make it a string
	# Check for scores higher than the treshold and count it
	items_with_good_percentage = 0
	for item in scores[0]:
		if item >= SCORE_TRESHOLD:
			items_with_good_percentage+=1
		else:
			break

	# Put the left x location of the box and the detected class as tuples in the temp_list
	temp_list = []
	for i in range(0, items_with_good_percentage):
		temp_list.append((boxes[0][i][1], classes[0][i]))

	# print(temp_list)

	def sortBy(item):
		return item[0]

	# Sort the temporary list
	sorted_list = sorted(temp_list, key=sortBy)
	formula_array = []

	# Put all IDs in the formula_array
	for item in sorted_list:
		formula_array.append(int(item[1]))

	# Check the IDs in the formula array and add the corresponding int/character to the formula string
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

	# To be replaced and calculated by FPGA
	# answer = int(eval(formula))

	# print("The formula in the image is: %s" % (formula))
	# print("The answer to that formula is: %d" % (answer))
	# print("%s = %d" % (formula, answer))

	# Make the labels on the image
	vu.visualize_boxes_and_labels_on_image_array(
		input_image,
		np.squeeze(boxes),
		np.squeeze(classes).astype(np.int32),
		np.squeeze(scores),
		cat_index,
		use_normalized_coordinates=True,
		line_thickness=8,
		min_score_thresh=SCORE_TRESHOLD)

	# cv2.imshow('Object detector', input_image)