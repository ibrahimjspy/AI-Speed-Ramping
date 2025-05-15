import os
import uuid
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
from werkzeug.utils import secure_filename
from processing.analyzer import analyze_motion_and_map_speeds
from processing.ffmpeg_utils import generate_speed_ramped_video
import config

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = os.urandom(24)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uid = uuid.uuid4().hex
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], uid + "_" + filename)
        out_path = os.path.join(app.config['OUTPUT_FOLDER'], uid + "_ramped.mp4")
        file.save(in_path)
        print(f"Processing file: {in_path}")

        # 1) analyze motion & build speed map
        speeds = analyze_motion_and_map_speeds(
            in_path,
            segment_duration=app.config['SEGMENT_DURATION'],
            min_speed=app.config['MIN_SPEED'],
            max_speed=app.config['MAX_SPEED']
        )

        print(f"Speed mapping: {speeds}")

        # 2) generate ramped video via ffmpeg
        generate_speed_ramped_video(in_path, out_path, speeds, app.config['SEGMENT_DURATION'])

        return render_template('result.html', output_file=os.path.basename(out_path))
    else:
        flash('Unsupported file type')
        return redirect(request.url)

@app.route('/output/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/get-speeds', methods=['POST'])
def get_speeds():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uid = uuid.uuid4().hex
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], uid + "_" + filename)
        file.save(in_path)

        segment_duration = float(request.form.get('segment_duration', app.config['SEGMENT_DURATION']))
        min_speed = float(request.form.get('min_speed', app.config['MIN_SPEED']))
        max_speed = float(request.form.get('max_speed', app.config['MAX_SPEED']))

        speeds = analyze_motion_and_map_speeds(in_path, segment_duration, min_speed, max_speed)

        os.remove(in_path)  # Cleanup

        return {
            'speeds': speeds,
            'segment_duration': segment_duration,
            'min_speed': min_speed,
            'max_speed': max_speed
        }
    return {'error': 'Unsupported file type'}, 400


import requests

@app.route('/get-speeds-from-url', methods=['POST'])
def get_speeds_from_url():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config.get('OUTPUT_FOLDER', 'output'), exist_ok=True)
    data = request.get_json()
    video_url = data.get('video_url')
    if not video_url:
        return {'error': 'Missing video_url'}, 400

    segment_duration = float(data.get('segment_duration', app.config['SEGMENT_DURATION']))
    min_speed = float(data.get('min_speed', app.config['MIN_SPEED']))
    max_speed = float(data.get('max_speed', app.config['MAX_SPEED']))

    try:
        uid = uuid.uuid4().hex
        filename = uid + ".mp4"
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Download the video
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        with open(in_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Analyze speeds
        speeds = analyze_motion_and_map_speeds(in_path, segment_duration, min_speed, max_speed)

        os.remove(in_path)  # Cleanup

        return {
            'speeds': speeds,
            'segment_duration': segment_duration,
            'min_speed': min_speed,
            'max_speed': max_speed
        }

    except Exception as e:
        if os.path.exists(in_path):
            os.remove(in_path)
        return {'error': str(e)}, 500



if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True)
