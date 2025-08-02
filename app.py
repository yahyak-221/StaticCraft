from flask import Flask, render_template, request, redirect, url_for, session, send_file
import markdown2
import os
import zipfile
from datetime import datetime
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "staticcraft_secret"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/editor", methods=["GET", "POST"])
def editor():
    html_preview = ""
    content = ""
    if request.method == "POST":
        content = request.form.get("markdown", "")
        html_preview = markdown2.markdown(content)
        session['content'] = content
        return redirect(url_for('templates_page'))  # <-- ensure this is here
    return render_template("editor.html", content=content, html_preview=html_preview)


@app.route("/templates", methods=["GET", "POST"])
def templates_page():
    content = session.get("content", "")
    html_content = markdown2.markdown(content)
    available_templates = ["basic", "portfolio"]  # Add your template folders here

    if request.method == "POST":
        selected_template = request.form.get("template")
        session["template"] = selected_template
        return redirect(url_for("generate"))

    return render_template("templates.html", templates=available_templates, content=html_content)


@app.route("/preview_template")
def preview_template():
    template = request.args.get("template", "basic")
    content = session.get("content", "")
    html_content = markdown2.markdown(content)
    return render_template(f"{template}/site_template.html", content=html_content)


@app.route("/generate")
def generate():
    content = session.get('content', '')
    template_name = session.get('template', 'basic')
    html_content = markdown2.markdown(content)
    return render_template(f"{template_name}/site_template.html", content=html_content)

@app.route("/download")
def download():
    content = session.get('content', '')
    template_name = session.get('template', 'basic')
    html_content = markdown2.markdown(content)

    rendered_html = render_template(f"{template_name}/site_template.html", content=html_content)

    os.makedirs('generated', exist_ok=True)
    os.makedirs('zips', exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    html_path = f"generated/site_{timestamp}.html"
    zip_path = f"zips/staticcraft_site_{timestamp}.zip"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(html_path, arcname="index.html")

    return send_file(zip_path, as_attachment=True)

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Config for image uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload-image", methods=["POST"])
def upload_image():
    if 'image' not in request.files:
        return "No file part", 400
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"/{UPLOAD_FOLDER}/{filename}"
    return "Invalid file", 400


if __name__ == "__main__":
    app.run(debug=True)
