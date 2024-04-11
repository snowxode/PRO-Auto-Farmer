import pytesseract
import pyautogui
import cv2
import re
import time
import tkinter as tk
import random
from PIL import ImageGrab
import threading
import signal
import os

# === GLOBAL VARIABLES ===
flag = True  # Flag to indicate if in a pokemon fight to stop the screenshot thread
extracted_text = "" # Text extracted from the screenshot
stats = {} # Dictionary to store the stats of the session
prev_poke = '' # Initialise the last pokemon found
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pyautogui.FAILSAFE = False # Disable the fail safe to stop the script with the mouse

def screenshot():
    global flag, extracted_text, stats, prev_poke
    
    # Take a screenshot of the pokemon name every 0.5s
    while True:
        screenshot = ImageGrab.grab(bbox=(880, 260, 1200, 310))
        #screenshot.save("screenshot.png")
        extracted_text = pytesseract.image_to_string(screenshot).lower()
        time.sleep(0.5)
        
        # Check if the pokemon is found
        if "wild" in extracted_text:
            try:
                prev_poke = re.sub(r'[^a-zA-Z]', '', extracted_text.split("wild ")[1])
            except:
                prev_poke = ''
            break
        else:
            if prev_poke != '':
                if prev_poke in stats:
                    stats[prev_poke] += 1
                else:
                    stats[prev_poke] = 1
            prev_poke = ''
            
    
    #debug
    print(extracted_text)
    
    # Stop the movement loop
    flag = False

def overlay():
    x1, y1, x2, y2 = 880, 260, 1200, 310

    # Create a transparent window
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.3)  # Set transparency (0.0 to 1.0)

    # Set the size and position of the window
    window_width = x2 - x1
    window_height = y2 - y1
    window_position = f"{x1}+{y1}"
    root.geometry(f"{window_width}x{window_height}+{window_position}")

    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.create_rectangle(0, 0, window_width, window_height, outline="red", width=3)
    canvas.pack(fill="both", expand=True)

    # Start the window
    root.mainloop()
    
def countdown(x):
    print("Restarting in...")
    for i in range(x, 0, -1):
        print(i)
        time.sleep(1)

def signal_handler(sig, frame):
    global exit_flag
    print("Ctrl+C pressed. Stopping threads...")
    exit_flag = True
    while True:
        ans = str(input("Enter e to exit, c to continue or s to see stats:")).lower()
        print(ans)
        if ans != "e" and ans != "c" and ans != "s":
            print("Invalid input try again.")
        elif ans == "e":
            os.system('cls')
            print("=== STATS ===")
            for key, value in stats.items():
                print(f"{key}: {value}")
            os._exit(0)
        elif ans == "c":
            countdown(3)
            break
        elif ans == "s":
            print("=== STATS ===")
            for key, value in stats.items():
                print(f"{key}: {value}")

def main():
    global flag, extracted_text
    
    # Ctrl+C exit handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the overlay box
    overlay_thread = threading.Thread(target=overlay, daemon=True)
    overlay_thread.start()
    
    # Enter the pokemon to catch and tab into the game
    pokemon = str(input("Enter the pokemon you want to catch (in lowercase): ")).lower()
    input("Press enter and tab into the game")
    countdown(5)
    
    # Main loop
    while True:
        # Start capturing ss every 0.5s
        screenshot_thread = threading.Thread(target=screenshot, daemon=True)
        screenshot_thread.start()
        
        # Start moving left and right until the pokemon is found (flag = False)
        while flag:
            pyautogui.keyDown('d')
            x = random.uniform(0.01, 0.5)
            pyautogui.keyDown('a')
            time.sleep(x)
            pyautogui.keyUp('a')
        
        # Stop the screenshot thread
        screenshot_thread.join()

        # Check if the correct pokemon is found and stop execution until the pokemon is caught
        if pokemon in extracted_text:
            input("Press enter once the pokemon is caught")
            countdown(3)
        
        # Run away from the pokemon (not desired pokemon found)
        pyautogui.press('4')
        
        # Restart the movement loop
        flag = True

if __name__ == "__main__":
    main()
