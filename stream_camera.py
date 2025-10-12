# stream_camera.py
# Live stream your Raspberry Pi Camera in browser
# Tested on Raspberry Pi OS (Trixie / Bookworm) with rpicam or libcamera

from flask import Flask, Response
import cv2

app = Flask(__name__)

# Initialize camera
camera = cv2.VideoCapture(0)

# Set camera properties for higher FPS and resolution
camera.set(3, 1280)  # Width
camera.set(4, 720)   # Height
camera.set(5, 60)    # FPS (may vary based on module and lighting)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Yield frame in streaming-compatible format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # Video streaming route
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
        <html>
        <head><title>Raspberry Pi Camera Stream</title></head>
        <body style="text-align:center; background-color:#111; color:white;">
        <h2>📷 Raspberry Pi Live Stream</h2>
        <img src="/video_feed" width="80%" />
        </body>
        </html>
    '''

if __name__ == '__main__':
    # Run Flask server on all interfaces
    app.run(host='0.0.0.0', port=8000)
