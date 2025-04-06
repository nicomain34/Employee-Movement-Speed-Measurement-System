import cv2
import time
import pygame
import numpy as np

# Initialize pygame for sound
pygame.mixer.init()
alert_sound = pygame.mixer.Sound("alert.wav")  # Load the sound file

# Specify the RTSP URL of your camera
rtsp_url = "rtsp://admin:password!@192.168.1.64/Stream1"  # Replace with your RTSP URL

# Open the camera via RTSP
cap = cv2.VideoCapture(rtsp_url)

# Check if the camera is accessible
if not cap.isOpened():
    print("Failed to open RTSP stream. Check the URL or connection.")
    exit()

# Time at the start of the recording
prev_time = time.time()

# Get the first frame
ret, prev_frame = cap.read()
if not ret:
    print("Failed to get the first frame")
    exit()

# Resize the frame to avoid size issues
height, width = prev_frame.shape[:2]
prev_frame_resized = cv2.resize(prev_frame, (width // 2, height // 2))
prev_gray = cv2.cvtColor(prev_frame_resized, cv2.COLOR_BGR2GRAY)

# Set up the control area (red rectangle)
zone_x, zone_y = 100, 100  # Top-left corner of the area
zone_width, zone_height = 420, 310  # Width and height of the area

# Speed threshold (pixels per second)
speed_threshold = 4300
change_threshold = 55
min_area = 2000  
max_area = 5000  

# Color range (for object tracking)
lower_hsv = np.array([102, 50, 50])        
upper_hsv = np.array([122, 131, 145])   

# Global variables for mouse event handling
drag = False  # For tracking mouse click
start_x, start_y = -1, -1  # Initial coordinates
end_x, end_y = -1, -1  # Final coordinates

# Mouse event handler function
def mouse_callback(event, x, y, flags, param):
    global drag, start_x, start_y, end_x, end_y, zone_x, zone_y, zone_width, zone_height
    if event == cv2.EVENT_LBUTTONDOWN:
        # If the left mouse button is pressed, start moving
        drag = True
        start_x, start_y = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        # If the mouse is moving, change the size of the rectangle
        if drag:
            end_x, end_y = x, y
            zone_x = min(start_x, end_x)
            zone_y = min(start_y, end_y)
            zone_width = abs(start_x - end_x)
            zone_height = abs(start_y - end_y)
    elif event == cv2.EVENT_LBUTTONUP:
        # End the rectangle movement
        drag = False
        end_x, end_y = x, y
        zone_x = min(start_x, end_x)
        zone_y = min(start_y, end_y)
        zone_width = abs(start_x - end_x)
        zone_height = abs(start_y - end_y)

# OpenCV window setup
cv2.namedWindow("Speed Detection")
cv2.setMouseCallback("Speed Detection", mouse_callback)

# Variables to track the plastic's static position
last_position = None
static_threshold = 300  # Threshold for detecting position change (in pixels)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize the frame to half the screen
    height, width = frame.shape[:2]
    frame_resized = cv2.resize(frame, (width // 2, height // 2))

    # Time of the current frame
    curr_time = time.time()
    elapsed_time = curr_time - prev_time  

    # Draw the red rectangle for the control area
    cv2.rectangle(frame_resized, (zone_x, zone_y), 
                  (zone_x + zone_width, zone_y + zone_height), 
                  (0, 0, 255), 2)

    # Convert the frame to HSV
    hsv = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    result = cv2.bitwise_and(frame_resized, frame_resized, mask=mask)
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    # Difference between the current and previous frames
    diff = cv2.absdiff(prev_gray, gray)
    _, thresh = cv2.threshold(diff, change_threshold, 255, cv2.THRESH_BINARY)

    # Find contours of moving objects
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Filter objects by size
        area = cv2.contourArea(contour)
        if area < min_area or area > max_area:
            continue

        # Get the object coordinates
        x, y, w, h = cv2.boundingRect(contour)

        # Check if the object is within the control area
        if not (zone_x <= x <= zone_x + zone_width and zone_y <= y <= zone_y + zone_height):
            continue  # Skip the object if it's outside the area

        # Calculate speed (in pixels per second)
        speed = w / elapsed_time  

        if speed < speed_threshold:
            continue  

        # If the plastic has not changed its position, no alert
        if last_position is not None:
            dx = abs(x - last_position[0])
            dy = abs(y - last_position[1])
            if dx < static_threshold and dy < static_threshold:
                continue  # Ignore the alert if the plastic is static

        # Update the last position of the plastic
        last_position = (x, y)

        # Draw a rectangle around the object
        cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)  
        cv2.putText(frame_resized, f"Speed: {speed:.2f} px/s", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Play sound if speed exceeds the threshold
        alert_sound.play()
        print("🚨 Cell damage Risk! 🚨")

    # Update the previous frame
    prev_gray = gray
    prev_time = curr_time

    # Display the resized video
    cv2.imshow("Speed Detection", frame_resized)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
