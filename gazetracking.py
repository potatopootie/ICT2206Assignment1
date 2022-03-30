import numpy as np
import os
import cv2
import pyautogui
from tensorflow.python.keras.models import *
from tensorflow.python.keras.layers import *
from tensorflow.python.keras.optimizers import *

# directory of the images used to train the model
image_path = 'C:/Users/maris/OneDrive/Desktop/UNIVERSITY/2206/2206_Assignment1/test/'
# Load cascade classifier detection object
cascade = cv2.CascadeClassifier("haarcascade_eye.xml")
# On the web camera
webCam = cv2.VideoCapture(0)

# to scale the data so that all the numeric values are roughly the same range
# feature scaling to make training process less sensitive to the scale 
def normalization(x):
  minimum = x.min()
  maximum = x.max()
  return (x - minimum) / (maximum - minimum)
  
# scale input image to 32 by 32  
def detect_eye(image_size=(32, 32)):
  _, frame = webCam.read()
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  # to find eyes
  # 1.3 = scale factor (increases chance of a matching size with the model for detection) 
  # 10 = minNeighbors, a parameter specifying how many neighbors each candidate rectangle should have to retain 
  # Parameter affects the quality of the detected faces (higher value = less detections but with higher quality)
  cropped_eye = cascade.detectMultiScale(gray, 1.3, 10) 
  if len(cropped_eye) == 2:
    eye_list = []
    # get the rectangle parameters for the detected eye
    for (x, y, w, h) in cropped_eye:
      # crop bounding box from the frame
      eye_box = frame[y:y + h, x:x + w]
      # resize the cropped box to the size of the image
      eye_box = cv2.resize(eye_box, image_size)
      eye_box = normalization(eye_box)
      # crop till you only have the eyeball
      eye_box = eye_box[10:-10, 5:-5]
      # add current eye to the list of 2 eyes
      eye_list.append(eye_box) # coordinates of eye movement 
      #print("before")
      #print(eye_list)
      #print("after")
      # stacks arrays in sequence horizontally
    return (np.hstack(eye_list) * 255).astype(np.uint8)
  else:
    return None

# mouse coordinates are reported starting at (0, 0), not (1, 1)
# screen resolution
width, height = 1919, 1079

path = os.listdir(image_path)
x_coords_list = []
y_coords_list = []
for i in path:
  x, y, _ = i.split(' ')
  x = float(x) / width
  y = float(y) / height

  x_coords_list.append(cv2.imread(image_path + i))
  y_coords_list.append([x, y])
x_coords_list = np.array(x_coords_list) / 255.0  #???
y_coords_list = np.array(y_coords_list)
#print (x_coords_list.shape, y_coords_list.shape)


# creating a Convolution Neural Network 
model = Sequential()
# 32: number of filters that convolutional layers will learn from
# 3,2 is the size of the convolutional filter in pixels

# activation function is responsible for transforming the summed weighted input
# from the node into the activation of the node or output for that input

# ReLU is a linear function that will output the input directly if it is positive, otherwise, output 0

#input shape is 
model.add(Conv2D(32, 3, 2, activation = 'relu', input_shape = (12, 44, 3)))
model.add(Conv2D(64, 2, 2, activation = 'relu'))
model.add(Flatten())
model.add(Dense(32, activation = 'relu'))
model.add(Dense(2, activation = 'sigmoid'))
model.compile(optimizer = "adam", loss = "mean_squared_error")
# display contents
model.summary()
print(model.summary)

# training the model, need to add "noise" to the image
epochs = 200
for epoch in range(epochs):
  model.fit(x_coords_list, y_coords_list, batch_size = 32)
  
while True:
  eye_list = detect_eye()
  if not eye_list is None:
    eye_list = np.expand_dims(eye_list / 255.0, axis = 0)
    x, y = model.predict(eye_list)[0]
    # move mouse according to coordinates from the images
    pyautogui.moveTo(x * width, y * height, 0.5)
    # mouse click
    pyautogui.click(button='left')