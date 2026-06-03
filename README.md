# SightLink AI

🚶‍♂️ AI-powered assistive navigation system designed to help visually impaired individuals detect obstacles in real time.

## Features

- Real-time object detection using YOLOv8
- Distance estimation (Far, Approaching, Near, Very Close)
- Voice alerts for detected obstacles
- Flask-based web dashboard
- Custom-trained obstacle detection model
- Live camera feed monitoring

## Detectable Objects

- Person
- Car
- Motorcycle
- Bicycle
- Dog
- Tree
- Traffic Sign
- Undercover Manhole

## Tech Stack

- Python
- Flask
- OpenCV
- YOLOv8 (Ultralytics)
- HTML
- CSS
- JavaScript

## Project Structure

```text
SightLink-AI/
│
├── app.py
├── train.py
├── templates/
│   └── index.html
│
├── Obstacle detection.yolov8/
│   ├── data.yaml
│   └── README.roboflow.txt
│
└── .gitignore
```

## Installation

```bash
git clone https://github.com/SandeepBisht672005/SightLink-AI.git

cd SightLink-AI

pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Future Improvements

- Mobile application integration
- GPS navigation support
- Bluetooth earphone alerts
- Improved distance estimation
- Edge-device deployment

## Author

**Sandeep Bisht**

B.Tech Computer Science & Engineering

GitHub:
https://github.com/SandeepBisht672005
