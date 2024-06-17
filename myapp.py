from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'supersecretkey'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET'])
def welcome():
    return render_template("welcome.html")

@app.route("/greet", methods=['POST'])
def greet():
    name = request.form['name']
    greet = request.form['greet']
    greeting = f"{greet}, {name}"
    return render_template("greet.html", greeting=greeting)

@app.route("/upload", methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            flash('No file part', 'message')
            return redirect(request.url)

        if file.filename == '':
            flash('No selected file', 'message')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            message = f'File successfully uploaded to {file_path}'
            return render_template("upload_result.html", message=message)

        flash('File type not allowed', 'message')
        return redirect(request.url)

    return render_template("upload_form.html")

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
