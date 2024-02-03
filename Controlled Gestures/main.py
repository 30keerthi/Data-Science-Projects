""" IMPORTING REQUIRED LIBRARIES """
import os
import numpy as np
import cv2
from cvzone.HandTrackingModule import HandDetector

# Setting the dimension of the camera
width, height = 1280, 720
folderPath = "Presentation"

# Setting up the camera
capture = cv2.VideoCapture(0)
capture.set(3, width)    # Setting the width
capture.set(4, height)   # Setting the height

# Creating a list for the presentation images
pathImages = os.listdir(folderPath)
pathImages = [filename for filename in pathImages if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'))]
pathImages.sort(key=lambda x: int(os.path.splitext(x)[0]))
print(pathImages)

# Setting dimension for smaller window
sw_height, sw_width = int(120*1), int(213*1)

# Setting the base slide
imgNumber = 0

""" HAND DETECTOR """

# Variable Declarations
detector = HandDetector(detectionCon= 0.8, maxHands=1)
gesturethreshold = 250
buttonpressed = False
counter = 0
delay = 25

# For drawing
annotation = [[]]
annotationNo = 0
annotationStart = False

while True:
    # Importing images
    success, img = capture.read()
    img = cv2.flip(img, 1)
    # To open another window for slides
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    # Detection of hands
    hands, img = detector.findHands(img)
    cv2.line(img,(0, gesturethreshold), (width, gesturethreshold), (0,255,255),10)

    if hands and buttonpressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        center_x, center_y = hand['center']
        lmList = hand['lmList']

        # Converting the range of the landmarks
        xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
        indexFinger = xVal, yVal

        """ DEFINING THE CONSTRAINTS FOR THE GESTURES """
        # only if the hand is above the threshold line
        if center_y <= gesturethreshold:
            annotationStart = False

            # Left Gesture - 1
            if fingers == [1, 0, 0, 0, 0]:
                print('Left')
                if imgNumber > 0:
                    buttonpressed = True
                    # For drawing
                    annotation = [[]]
                    annotationNo = 0
                    annotationStart = False
                    imgNumber -= 1

            # Right Gesture - 2
            if fingers == [0, 0, 0, 0, 1]:
                print('Right')
                if imgNumber < len(pathImages)-1:
                    buttonpressed = True
                    # For drawing
                    annotation = [[]]
                    annotationNo = 0
                    annotationStart = False
                    imgNumber += 1

        # Showing pointer Gesture - 3
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12,(0,0,255),cv2.FILLED)
            annotationStart = False

        # Drawing pointer Gesture - 4
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNo += 1
                annotation.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotation[annotationNo].append(indexFinger)
        else:
            annotationStart = False

        # Eraser gesture - 5
        if fingers ==[1, 1, 1, 1, 1]:
            if annotation:
                if annotationNo >=0:
                    annotation.pop(-1)
                    annotationNo -= 1
                    buttonpressed = True
    else:
        annotationStart = False

    # Slowing the gesture action
    if buttonpressed:
        counter += 1
        if counter > delay:
            counter = 0
            buttonpressed = False

    # For drawing gesture
    for i in range(len(annotation)):
        for j in range(len(annotation[i])):
            if j != 0:
                cv2.line(imgCurrent, annotation[i][j - 1], annotation[i][j], (0, 0, 200),12)

    # Placing the webcam on slide
    imgSmall = cv2.resize(img, (sw_width, sw_height))
    # Getting dimension of the current slide
    h, w, _ = imgCurrent.shape
    imgCurrent[h - sw_height:, 0:sw_width] = imgSmall

    # Display the image
    cv2.imshow("Image", img)
    cv2.imshow("Slides", imgCurrent)

    # To exit press the 'q' key
    key = cv2.waitKey(1)
    if key == ord('x' or 'X'):
        break

capture.release()
cv2.destroyAllWindows()