import subprocess
import tempfile
import os
import json

def get_duration(path: str) -> float:
    """Use ffprobe to get video duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "format=duration",
        "-of", "json",
        path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(json.loads(res.stdout)["format"]["duration"])

def has_audio_stream(path: str) -> bool:
    """Check if the input has an audio stream."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=index",
        "-of", "json",
        path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(res.stdout)
    return bool(info.get("streams"))

def generate_speed_ramped_video(
    input_path: str,
    output_path: str,
    speeds: list[float],
    segment_duration: float = 0.5
) -> None:
    """
    Split the input into segments of `segment_duration` seconds,
    apply speed factors (video with setpts; audio only if present),
    and concatenate back together.
    """
    tmpdir = tempfile.mkdtemp(prefix="ffmpeg_ramp_")
    segment_files = []
    total_dur = get_duration(input_path)
    audio_present = has_audio_stream(input_path)

    for idx, speed in enumerate(speeds):
        start = idx * segment_duration
        if start >= total_dur:
            break
        duration = min(segment_duration, total_dur - start)
        out_file = os.path.join(tmpdir, f"seg_{idx:03d}.mp4")

        if audio_present:
            # build video + audio filters
            v_filter = f"[0:v]setpts={1/speed}*PTS[v]"
            # chain atempo filters (0.5–2.0 per filter)
            atempo_steps = []
            s = speed
            while s > 2.0:
                atempo_steps.append("atempo=2.0")
                s /= 2.0
            while s < 0.5:
                atempo_steps.append("atempo=0.5")
                s /= 0.5
            atempo_steps.append(f"atempo={s:.6f}")
            a_filter = "[0:a]" + ",".join(atempo_steps) + "[a]"
            filter_complex = f"{v_filter};{a_filter}"
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(start), "-i", input_path,
                "-t", str(duration),
                "-filter_complex", filter_complex,
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-c:a", "aac",
                out_file
            ]
        else:
            # video only: apply setpts, drop audio
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(start), "-i", input_path,
                "-t", str(duration),
                "-filter:v", f"setpts={1/speed}*PTS",
                "-an",
                "-c:v", "libx264",
                out_file
            ]

        subprocess.run(cmd, check=True)
        segment_files.append(out_file)

    # write concat list
    list_path = os.path.join(tmpdir, "concat_list.txt")
    with open(list_path, "w") as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")

    # concatenate
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        output_path
    ]
    subprocess.run(concat_cmd, check=True)
    print(f"Output at: {output_path} (temp: {tmpdir})")

# Usage example:
# generate_speed_ramped_video_ffmpeg("input.mp4", "output.mp4", [0.94, 1.05, 0.88, ...])


# Example usage:
# generate_speed_ramped_video_ffmpeg("input.mp4", "output_ramped.mp4", [0.94, 0.88, 1.05, ...])
