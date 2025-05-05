# Virtual Painter

'''
------------------------------------------------
1) Import Image from folder and display it on the screen
2) Find the hand landmarks
3) Check wiv finger are vUP
4) If 2 fingers are up, then Selection mode
5) If 1 finger is up, then Paint mode
------------------------------------------------
'''
# Virtual Painter

import handTrackingModule as htm
import mediapipe as mp
import numpy as np
import time
import cv2
import os

folderPath = os.path.dirname(os.path.abspath(__file__)) + "/Image"
myList = os.listdir(folderPath)
overlayList = []

drawColor = (255, 0, 255)  # Default color
brushThickness = 15
eraserThickness = 100
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)
useAddWeighted = True



# Load all header images
for imgPath in myList:
    image = cv2.imread(f'{folderPath}/{imgPath}')
    overlayList.append(image)

header = overlayList[0]

cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

detector = htm.handDetector(detectionCon=0.85, maxHands=1)

while True:
    success, image = cap.read()
    if not success:
        print("Camera not accessible.")
        break

    image = cv2.flip(image, 1)
    image = detector.findHands(image)
    lmList = detector.findPosition(image, draw=False)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1], lmList[8][2]  # Index
        x2, y2 = lmList[12][1], lmList[12][2]  # Middle

        fingers = detector.fingersUp()

        # Selection Mode: Both fingers up
        if fingers[1] and fingers[2]:
            
            xp, yp = 0, 0  # Reset previous position
            if y1 < 185:
                if 200 <= x1 < 450:
                    header = overlayList[1]
                    drawColor = (255, 0, 0)
                elif 450 <= x1 < 715:
                    header = overlayList[2]
                    drawColor = (0, 255, 0)
                elif 715 <= x1 < 1000:
                    header = overlayList[3]
                    drawColor = (0, 0, 255)
                elif 1000 <= x1 < 1280:
                    header = overlayList[4]
                    drawColor = (0, 0, 0)

            cv2.rectangle(image, (x1, y1 - 35), (x2, y2 + 35), drawColor, cv2.FILLED)

        # Drawing Mode: Only index finger up
        elif fingers[1] and not fingers[2]:
            cv2.circle(image, (x1, y1), 15, (0, 255, 0), cv2.FILLED)

            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            thickness = eraserThickness if drawColor == (0, 0, 0) else brushThickness

            cv2.line(image, (xp, yp), (x1, y1), drawColor, thickness)
            cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, thickness)
            xp, yp = x1, y1


    if useAddWeighted:
        image = cv2.addWeighted(image, 0.75, imgCanvas, 0.95, 0)
    else:
        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        image = cv2.bitwise_and(image, imgInv)
        image = cv2.bitwise_or(image, imgCanvas)



    # Add header
    image[0:header.shape[0], 0:header.shape[1]] = header

    # Show final output
    cv2.imshow("Virtual Painter", image)

    # Stop if 'q' is pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        cv2.imwrite(os.path.dirname(os.path.abspath(__file__)) + f"/Saved Canvas/Painting_{timestamp}.png", imgCanvas)
        print(f"Canvas saved as {os.path.dirname(os.path.abspath(__file__)) }+ /Saved Canvas/Painting_{timestamp}.png")


    elif key == ord('m'):
        useAddWeighted = not useAddWeighted
        print(f"Blending mode changed: {'addWeighted' if useAddWeighted else 'bitwise'}")

    # Release resources
cap.release()
cv2.destroyAllWindows()
