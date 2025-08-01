from flask import Flask, render_template, request, redirect, url_for, session
import markdown2
import os

app = Flask(__name__)
app.secret_key = "staticcraft_secret"  # Needed for session storage

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
    return render_template("editor.html", content=content, html_preview=html_preview)

@app.route("/templates", methods=["GET", "POST"])
def templates_page():
    if request.method == "POST":
        selected_template = request.form.get("template")
        session['template'] = selected_template
        return redirect(url_for('generate'))
    return render_template("templates.html")

@app.route("/generate")
def generate():
    content = session.get('content', '')
    template_name = session.get('template', 'basic')
    html_content = markdown2.markdown(content)

    return render_template(f"{template_name}/site_template.html", content=html_content)

if __name__ == "__main__":
    app.run(debug=True)
