import cv2
import numpy as np
import time
import picar
from picar import front_wheels
from picar import back_wheels

# Set up the PiCar
picar.setup()
fw = picar.front_wheels.Front_Wheels(db='config')
bw = picar.back_wheels.Back_Wheels(db='config')
speed = 30

# Öfne Kamera
camera = cv2.VideoCapture(0)

# Kamera Einstellungen
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


while True:
    # Fahre
    bw.backward()
    bw.speed = speed
    print("Start")

    # Bild von der Kamera nehmen
    ret, frame = camera.read()

    # Frame Check
    if not ret:
        print("Error: Failed to capture frame from camera")
        continue

    # grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Linien Finden
    edges = cv2.Canny(gray, 50, 150, apertureSize = 3)

    # Hough transform
    lines = cv2.HoughLines(edges, 1, np.pi/180, 200)

    # Line Check
    if lines is None:
        print("Warning: No lines detected")
        continue

    # Zentrum
    image_center = frame.shape[1] // 2

    # Linienpositionen bestimmen
    line_positions = []
    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        line_positions.append((x1 + x2) // 2)

    # Zwischen Linien
    center_pos = (line_positions[0] + line_positions[1]) // 2
    # Calculate the angle between the center position and the center of the frame
    angle = np.arctan2(frame.shape[0], center_pos - image_center)

    # Winkel in Grad umrechnen
    angle = angle * 180 / np.pi

    # Servo entsprechend einstellen
    set_angle(angle)
    print(angle)

    angle = max(-45, min(45, angle))
    fw.turn(90 + angle)

    # Check if the 'q' key was pressed
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

# Clean up resources
camera.release()
bw.stop()
