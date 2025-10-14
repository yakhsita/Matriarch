import cv2, time, datetime, os

os.makedirs("/home/pi/Pictures", exist_ok=True)

WIDTH, HEIGHT, FPS = 640, 480, 60
pipeline = (
    f"libcamerasrc ! video/x-raw,width={WIDTH},height={HEIGHT},framerate={FPS}/1 ! "
    f"videoconvert ! appsink"
)

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
cv2.namedWindow("Camera", cv2.WINDOW_OPENGL)

prev = time.time()
frames = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frames += 1
    if frames >= 10:
        now = time.time()
        fps_actual = frames / (now - prev)
        prev, frames = now, 0
    cv2.putText(frame, f"{fps_actual:.1f} FPS", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Camera", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break
    elif key == 32:  # SPACE
        filename = f"/home/pi/Pictures/photo_{datetime.datetime.now():%Y%m%d_%H%M%S}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")

cap.release()
cv2.destroyAllWindows()
