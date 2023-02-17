import cv2
import pickle
import cvzone
import numpy as np


# Video feed

cap = cv2.VideoCapture('carPark.mp4')

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48


def checkParkingSpace(imgProcess):

    spaceCounter = 0

    for pos in posList:
        x, y = pos

        # We know each frame of parking space's height and width therefore we have to determine whether there's a car inside a parking space
        # so we're going to crop the images of the car parking spots posList gives us the values from the CarParkPos file and we're storing x and y
        # values of these positions into x and y for every frame within the loop, since for each frame we know these values now we can crop the image
        imgCrop = imgProcess[y:y+height, x:x+width]
        # just to show parking spots in different frames
        # cv2.imshow(str(x*y), imgCrop)
        # So now we have each frame of parking spots, and we're ready to determine whether there's a car in that parking space or not.
        # We'll count pixels, and check if there's lot's of edges, if yes then we can say there's a car inside that parking space but first we need
        # to convert these frames into binary images and check // after that part from our loop, we are sending our dilated image and now every
        # cropped image shows us a dilated image with white thick pixels now we have to count these pixels
        count = cv2.countNonZero(imgCrop)
        # now in order to determine whether there's a car by looking at these count numbers we need to check the numbers, we'll do that by putting
        # these numbers into the frames by cvzone.putTextRect() function -> (x, y+height-10) initial position of the count text
        cvzone.putTextRect(img, str(count), (x, y+height-10),
                           scale=1.5, thickness=2, offset=0)
        # param offset: Clearance around the text
        # it should be noted that we're doing the process with dilated image but, when we're showing whether it's empty or not, we'll show it on our original img
        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(
            img, pos, (pos[0]+width, pos[1]+height), color, thickness)
        # Drawing rectangle around marked cars from CarParkPos that is generated from ParkingSpacePicker.py

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50),
                       scale=3, thickness=5, offset=20, colorR=(0, 200, 0))
    # param offset: Clearance around the text


while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # right after reading the frame, we'll convert it into grayscale and after that we'll add some blur onto our imgGray
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    # now we're going to convert our image into a binary image
    imgThreshold = cv2.adaptiveThreshold(
        imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    # it can be clearly seen that if there's a car in that spot, then white pixels are visible.
    # However, there are also some white pixels, other than the park spaces, to prevent that, we'll generate the median version of the imgThreshold
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    # 5 is the kernel size / if size gets bigger, the accuracy of the white lines will be worse
    # Sometimes these pixels can be a little bit thin, so we can make it a little bit thicker. So we can easily differentiate between empty spaces
    # and car parked spaces. In order to achieve that goal, we'll need dilation and we'll store this image into imgDil
    # defining our kernel values by (3,3) and the size for unsigned integer 8 bits
    kernel = np.ones((3, 3), np.uint8)
    imgDil = cv2.dilate(imgMedian, kernel, iterations=1)
    # and now sending our imgDil into our checkParkingSpace() function to check whether there's a car in parking spaces, and this will be checked through dilated image
    checkParkingSpace(imgDil)

    cv2.imshow('Image', img)
    # cv2.imshow("Image Blur", imgBlur)
    # cv2.imshow("Image Threshold", imgThreshold)
    # cv2.imshow("Image Median", imgMedian)
    # cv2.imshow("Image Dilate", imgDil)
    # displaying binary converted threshold image.
    cv2.waitKey(10)
