# camera_gui.py
# GUI for capturing photos/videos from Raspberry Pi camera
# Works perfectly inside VNC desktop environment

import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import time
import threading

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height
cap.set(5, 60)    # FPS

# GUI setup
window = tk.Tk()
window.title("📸 Raspberry Pi Camera GUI")
window.geometry("900x700")
window.configure(bg="#222")

video_label = tk.Label(window, bg="#222")
video_label.pack(pady=10)

recording = False
out = None

# Update frame continuously
def update_frame():
    global frame
    ret, frame = cap.read()
    if ret:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    window.after(15, update_frame)  # 15 ms delay ≈ 60 FPS

# Capture photo
def capture_photo():
    ret, frame = cap.read()
    if ret:
        filename = f"/home/pi/Pictures/photo_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        messagebox.showinfo("Saved", f"📷 Photo saved as:\n{filename}")

# Start/Stop video recording
def toggle_record():
    global recording, out
    if not recording:
        filename = f"/home/pi/Videos/video_{int(time.time())}.avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, 60.0, (1280, 720))
        recording = True
        record_button.config(text="⏹ Stop Recording", bg="#c33")
        threading.Thread(target=record_video, daemon=True).start()
    else:
        recording = False
        record_button.config(text="⏺ Start Recording", bg="#3c3")

# Recording process
def record_video():
    global recording, out
    while recording:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
    out.release()
    messagebox.showinfo("Saved", "🎞️ Video saved successfully!")

# Exit cleanly
def on_close():
    global recording
    recording = False
    cap.release()
    window.destroy()

# Buttons
btn_frame = tk.Frame(window, bg="#222")
btn_frame.pack(pady=20)

photo_button = tk.Button(btn_frame, text="📷 Capture Photo", command=capture_photo, font=("Arial", 14), bg="#3c3", fg="white", width=18)
photo_button.grid(row=0, column=0, padx=10)

record_button = tk.Button(btn_frame, text="⏺ Start Recording", command=toggle_record, font=("Arial", 14), bg="#3c3", fg="white", width=18)
record_button.grid(row=0, column=1, padx=10)

exit_button = tk.Button(btn_frame, text="❌ Exit", command=on_close, font=("Arial", 14), bg="#c33", fg="white", width=18)
exit_button.grid(row=0, column=2, padx=10)

update_frame()
window.protocol("WM_DELETE_WINDOW", on_close)
window.mainloop()
