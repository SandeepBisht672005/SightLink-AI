from flask import Flask, render_template, Response, jsonify
import cv2
import threading
import time
import os
import queue
from ultralytics import YOLO

app = Flask(__name__)

# ── custom trained model ──
model = YOLO("runs/detect/sightlink_model-5/weights/best.pt")
MODEL_CLASSES = model.names
print("✅ Model classes detected:", MODEL_CLASSES)
# ── Speech Queue System  ──
speech_queue = queue.Queue(maxsize=1)

def speech_worker():
    while True:
        text = speech_queue.get()
        if text is None:
            break

        try:
            print(f"🔊 Speaking: {text}")
            os.system(f'say "{text}"')
        except Exception as e:
            print(f"TTS error: {e}")

        speech_queue.task_done()

speech_thread = threading.Thread(target=speech_worker, daemon=True)
speech_thread.start()
def speak(text):
    # Clear queue so latest alert always plays
    while not speech_queue.empty():
        try:
            speech_queue.get_nowait()
            speech_queue.task_done()
        except:
            pass
    try:
        speech_queue.put_nowait(text)
    except queue.Full:
        pass

def estimate_distance(box_area, frame_area):
    ratio = box_area / frame_area

    if ratio > 0.25:
        return "Very Close", "red"
    elif ratio > 0.08:
        return "Near", "orange"
    elif ratio > 0.02:
        return "Approaching", "yellow"
    else:
        return "Far", "green"


def get_cv_color(dist):
    return {
        "Very Close": (0, 0, 255),
        "Near": (0, 165, 255),
        "Approaching": (0, 255, 255),
        "Far": (0, 255, 0)
    }.get(dist, (255, 255, 255))
   

def build_alert_message(label, dist):
    label_clean = label.replace("_", " ").replace("-", " ")
    if dist == "Very Close":
        return f"Warning! {label_clean} very close, stop immediately"
    elif dist == "Near":
        return f"Caution! {label_clean} is near"
    else:
        return f"{label_clean} is approaching"

# ── Shared state ──
latest_detections = []
det_lock    = threading.Lock()
camera      = None
camera_lock = threading.Lock()

def gen_frames():
    global camera, latest_detections
    last_spoken = {}
    SPEAK_GAP = 5

    while True:
        with camera_lock:
            if camera is None or not camera.isOpened():
                break
            ret, frame = camera.read()

        if not ret:
            break

        h, w = frame.shape[:2]
        frame_area = h * w
        results = model(frame, verbose=False)[0]
        now = time.time()
        dets = []
        all_alerts = []

        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < 0.45:
                continue

            label    = MODEL_CLASSES[int(box.cls[0])]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            box_area = (x2 - x1) * (y2 - y1)
            dist, color = estimate_distance(box_area, frame_area)
            cv_color    = get_cv_color(dist)

            cv2.rectangle(frame, (x1, y1), (x2, y2), cv_color, 2)
            cv2.putText(frame, f"{label} | {dist} ({conf:.0%})",
                        (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, cv_color, 2)

            dets.append({"label": label, "distance": dist, "color": color})


            if dist in ("Very Close", "Near", "Approaching"):
                key = f"{label}_{dist}"
                if now - last_spoken.get(key, 0) > SPEAK_GAP:
                    all_alerts.append((label, dist, conf, key))

        # Sort by urgency then confidence — speak most important
        urgency_order = {"Very Close": 0, "Near": 1, "Approaching": 2}
        all_alerts.sort(key=lambda x: (urgency_order.get(x[1], 3), -x[2]))

        if all_alerts:
            label, dist, conf, key = all_alerts[0]
            msg = build_alert_message(label, dist)
            speak(msg)
            last_spoken[key] = now

        # Clean old entries
        last_spoken = {k: v for k, v in last_spoken.items() if now - v < 30}

        with det_lock:
            latest_detections = dets
            cv2.putText(frame, "SightLink AI", (10, 30),
                    cv2.FONT_HERSHEY_DUPLEX, 1, (0, 212, 255), 2)
        cv2.putText(frame, f"Objects: {len(dets)}", (10, 62),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        _, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/start_cam")
def start_cam():
    global camera
    with camera_lock:
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0)
    speak("SightLink AI activated. Scanning environment.")
    return jsonify({"status": "started"})

@app.route("/stop_cam")
def stop_cam():
    global camera
    with camera_lock:
        if camera and camera.isOpened():
            camera.release()
            camera = None
    speak("SightLink AI deactivated.")
    return jsonify({"status": "stopped"})

@app.route("/get_detections")
def get_detections():
    with det_lock:
        return jsonify({"detections": latest_detections})


if __name__ == "__main__":
    print("=" * 50)
    print("  SightLink AI — Starting...")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=False, threaded=True)
    