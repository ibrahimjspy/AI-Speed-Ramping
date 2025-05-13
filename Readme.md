# AI Speed Ramping Flask App

A Flask-based web application that applies **motion-intensity–driven speed ramping** to video clips using **OpenCV**, **NumPy**, and **FFmpeg**. This app allows users to upload a short video or provide a remote video URL, analyze motion across frames using optical flow, and generate a dynamic playback effect—speeding up static moments and slowing down action-packed ones.

---

## 🧠 What It Does

This app intelligently alters video playback speed by analyzing how much movement occurs in each segment of the video:

- **Low-motion segments** (e.g., still frames or minimal camera movement) are played faster (up to 2×).
- **High-motion segments** (e.g., fast action or transitions) are slowed down (down to 0.5×).
- The result is a cinematic “speed ramp” effect—commonly used in sports replays, music videos, and stylistic transitions.

---

## 🚀 Features

- **🎥 Optical Flow Motion Analysis**  
  Uses OpenCV to compute pixel-level motion between frames.
  
- **🧮 Dynamic Speed Mapping**  
  Maps each segment to a speed multiplier based on detected motion.

- **🎞️ FFmpeg Segment Processing**  
  Applies speed changes per segment and stitches them back into a final video.

- **🖥️ Simple Web UI**  
  Upload your clip via a browser, watch it get transformed, and download the result.

- **⚙️ Configurable Parameters**  
  Customize segment duration, minimum/maximum speeds, and file upload limits via `config.py`.

- **🧩 API Methods**  
  Two powerful endpoints to programmatically retrieve speed mapping:
  - Upload a file and get back the motion-based speed list.
  - Send a remote video URL (e.g. S3) and retrieve speed data.

---

## 🧾 Requirements

- Python 3.8+
- [FFmpeg](https://ffmpeg.org/) installed and available in your system PATH
- Virtualenv (recommended)

### Python dependencies (`requirements.txt`):

```text
Flask>=2.0
Werkzeug>=2.0
opencv-python>=4.5
numpy>=1.19
moviepy>=1.0
requests>=2.25
````

---

## 🗂 Project Structure

```
ai-speed-ramping/
├── app.py                # Flask application entrypoint
├── config.py             # Global configuration settings
├── static/
│   └── styles.css        # Basic form styling
├── templates/
│   ├── index.html        # Upload interface
│   └── result.html       # Download page
├── processing/
│   ├── analyzer.py       # Optical flow motion detection and speed mapping
│   └── ffmpeg_utils.py   # FFmpeg segment speed changes and merging
├── uploads/              # Temporary input files
├── output/               # Final processed files
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## ⚙️ Configuration

You can configure the app through `config.py`:

```python
UPLOAD_FOLDER = "uploads/"
OUTPUT_FOLDER = "output/"
ALLOWED_EXTENSIONS = {"mp4", "mov", "avi"}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

MIN_SPEED = 0.5        # Minimum playback speed
MAX_SPEED = 2.0        # Maximum playback speed
SEGMENT_DURATION = 0.5 # Seconds per speed-analyzed segment
```

---

## 🧪 Usage

1. **Start the server**

   ```bash
   flask run
   ```

2. **Open your browser**

   Navigate to:
   `http://127.0.0.1:5000/`

3. **Upload a clip**
   Choose a video and submit. Wait for processing.

4. **Download result**
   After processing, download the ramped video with dynamic speed changes.

---

## 📡 API Endpoints


#### `GET /`

Returns the upload form UI.

#### `POST /process`

Uploads a video, applies speed mapping, and returns a download link for the ramped result.


#### `POST /get-speeds`

**Purpose**: Upload a video and receive the speed mapping JSON.

**Form Fields**:

* `file`: Video file
* `segment_duration`: Optional (defaults to `config.py`)
* `min_speed`: Optional
* `max_speed`: Optional

**Response**:

```json
{
  "speeds": [1.0, 0.6, 2.0, ...],
  "segment_duration": 0.5,
  "min_speed": 0.5,
  "max_speed": 2.0
}
```

---

#### `POST /get-speeds-from-url`

**Purpose**: Provide a video URL (e.g., S3 link), download it, and return the motion-based speed map.

**JSON Payload**:

```json
{
  "video_url": "https://s3.amazonaws.com/your-bucket/video.mp4",
  "segment_duration": 0.5,
  "min_speed": 0.5,
  "max_speed": 2.0
}
```

**Response**:

```json
{
  "speeds": [...],
  "segment_duration": 0.5,
  "min_speed": 0.5,
  "max_speed": 2.0
}
```

---

## 🧹 Maintenance Tips

* Clean out `uploads/` and `output/` regularly or use a cron job to prevent disk fill-up.
* Make use of the cleanup logic built into new API methods.

---

## 🧪 Development

* **Debug Logging**: Adjust print/debug statements in `app.py` or refactor with logging module.
* **Docker Support** (Optional): Add Dockerfile + volume mounting for portability and scalability.

---

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch
   `git checkout -b feature/YourFeature`
3. Commit your changes
   `git commit -am "Add your feature"`
4. Push and create a PR

Include tests or usage examples if adding new logic.

---

## 🪪 License

MIT License. See [LICENSE](LICENSE) for details.


