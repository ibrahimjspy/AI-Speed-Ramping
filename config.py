import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

# Speed mapping settings
MIN_SPEED = 0.8    # slowest (50% of original)
MAX_SPEED = 1.2    # fastest (200% of original)

# Segment length in seconds for analysis & filtering
SEGMENT_DURATION = 0.5
