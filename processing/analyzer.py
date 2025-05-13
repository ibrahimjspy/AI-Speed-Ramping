import cv2
import numpy as np

def smooth_speeds(speeds, window=5):
    """
    Simple moving average smoothing with same-length output.
    Pads the ends so the result list is the same length as input.
    """
    if len(speeds) < window:
        return speeds.copy()
    pad = window // 2
    padded = [speeds[0]] * pad + speeds + [speeds[-1]] * pad
    kernel = np.ones(window) / window
    smoothed = np.convolve(padded, kernel, mode='valid')
    return smoothed.tolist()

def analyze_motion_and_map_speeds(
    video_path,
    segment_duration=0.5,
    min_speed=0.5,
    max_speed=2.0
):
    """
    Analyze optical flow on the video and return a smoothed, clamped
    list of speed factors—one value per segment.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        cap.release()
        raise ValueError("Could not determine FPS of video")
    seg_frames = int(segment_duration * fps)
    flow_magnitudes = []

    # Read first frame
    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        raise ValueError("Couldn't read first frame from video")

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Compute frame-to-frame flow magnitudes
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, gray,
            None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        mag, _ = cv2.cartToPolar(flow[...,0], flow[...,1])
        flow_magnitudes.append(np.mean(mag))
        prev_gray = gray

    cap.release()

    if not flow_magnitudes:
        return []

    # Determine global min/max for normalization
    global_min = float(np.min(flow_magnitudes))
    global_max = float(np.max(flow_magnitudes))
    ptp = global_max - global_min + 1e-6

    # Map each segment to a raw speed value
    raw_speeds = []
    for i in range(0, len(flow_magnitudes), seg_frames):
        segment = flow_magnitudes[i:i + seg_frames]
        if not segment:
            continue
        avg_flow = float(np.mean(segment))
        norm = (avg_flow - global_min) / ptp
        speed = min_speed + norm * (max_speed - min_speed)
        raw_speeds.append(speed)

    if not raw_speeds:
        return []

    # 1) Clamp extreme jumps (>20% change between neighboring segments)
    clamped = [raw_speeds[0]]
    for prev, curr in zip(raw_speeds, raw_speeds[1:]):
        max_delta = 0.2 * prev
        delta = curr - prev
        if abs(delta) > max_delta:
            curr = prev + np.sign(delta) * max_delta
        clamped.append(curr)

    # 2) Smooth the clamped speed curve
    smoothed = smooth_speeds(clamped, window=5)
    return smoothed
