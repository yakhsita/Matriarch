import cv2
import subprocess
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import datetime, os, threading, time

# Ensure Pictures folder exists
os.makedirs("/home/pi/Pictures", exist_ok=True)

# --- CAMERA SETTINGS ---
WIDTH = 600
HEIGHT = 400
FPS = 60  # Increase FPS target here (keep resolution same)
QUALITY = 85  # Slightly higher quality helps reduce artifacts

# --- RPi Camera command ---
command = [
    "rpicam-vid",
    "-t", "0",                   # run forever
    "--inline",                  # MJPEG inline stream
    "--codec", "mjpeg",          # MJPEG codec
    "-n",                        # no preview
    "-o", "-",                   # output to stdout
    "--width", str(WIDTH),
    "--height", str(HEIGHT),
    "--framerate", str(FPS),
    "--quality", str(QUALITY)
]

# Start process with big buffer (helps at 60 FPS)
proc = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=2**22)

# Tkinter setup
window = tk.Tk()
window.title(f"Raspberry Pi Camera GUI ({WIDTH}x{HEIGHT}@{FPS}fps)")
label = tk.Label(window)
label.pack()

last_frame = None
frame_lock = threading.Lock()

def capture_thread():
    """Continuously read frames in background thread"""
    global last_frame
    data = b""
    while True:
        chunk = proc.stdout.read(4096)
        if not chunk:
            break
        data += chunk
        while b'\xff\xd9' in data:  # handle multiple frames quickly
            jpeg_end = data.index(b'\xff\xd9') + 2
            jpeg = data[:jpeg_end]
            data = data[jpeg_end:]
            arr = np.frombuffer(jpeg, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is not None:
                with frame_lock:
                    last_frame = frame

def update_gui():
    """Show frame on GUI (non-blocking)"""
    start = time.time()
    with frame_lock:
        frame = last_frame.copy() if last_frame is not None else None
    if frame is not None:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
        label.config(image=img)
        label.image = img

    # Dynamically adjust refresh rate for smoothness
    elapsed = time.time() - start
    delay = max(1, int((1000/FPS) - (elapsed * 1000)))
    label.after(delay, update_gui)

def capture_photo():
    """Save latest frame"""
    with frame_lock:
        frame = last_frame.copy() if last_frame is not None else None
    if frame is not None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/home/pi/Pictures/photo_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"?? Saved: {filename}")

def on_close():
    """Close safely"""
    proc.terminate()
    window.destroy()

# Button
btn = tk.Button(window, text="Capture Photo", command=capture_photo)
btn.pack(pady=10)

# Start background thread for reading frames
thread = threading.Thread(target=capture_thread, daemon=True)
thread.start()

# Run GUI
window.protocol("WM_DELETE_WINDOW", on_close)
update_gui()
window.mainloop()
