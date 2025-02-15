from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
from drive import API
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)  # for flash messages

# Initialize Google Drive API
drive_api = API()

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    try:
        # Get all files from Google Drive
        files = drive_api.get_all_files()
        return render_template('index.html', files=files.get('files', []))
    except Exception as e:
        flash(f'Error loading files: {str(e)}', 'error')
        return render_template('index.html', files=[])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    try:
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        # Upload to Google Drive
        result = drive_api.upload_file(temp_path, filename)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if result:
            flash('File uploaded successfully!', 'success')
        else:
            flash('Error uploading file', 'error')
            
    except Exception as e:
        flash(f'Error uploading file: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/download/<file_id>')
def download_file(file_id):
    try:
        # Download file from Google Drive
        destination = request.args.get('destination', '')

        file_data = drive_api.download_file_stream(file_id, destination)
        if file_data:
            return send_file(
                file_data['file_stream'],
                download_name=file_data['filename'],
                as_attachment=True,
            )
        else:
            flash('Error downloading file', 'error')
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
