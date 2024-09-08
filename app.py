from flask import Flask, stream_with_context, render_template, Response, request, make_response, send_file, session, jsonify
from flaskwebgui import FlaskUI
import sheetmusicfromytb as sm
import os
import numpy as np


#INITIALISATION
app = Flask(__name__, static_folder='./static', template_folder='./templates')
app.secret_key = "25f2fc511531d5bbfb0685224ccd7ac81863fec116de16b1ab3c8bbd39218f88"

#GESTIONS DES PAGES ET DES REQUETES

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@stream_with_context
def generate(title, url, frequency, threshold, color, numberimg, numerotation, deformation, settitle, crop, imgcrop):
    yield "data: 5\n\n"
    sm.video_download(url)
    yield "data: 20\n\n"
    frames_list = sm.extract_frames(frequency)
    yield "data: 40\n\n"
    listframes = sm.get_different_frames(threshold, frames_list, color, crop)
    yield "data: 80\n\n"
    yield f"frames: {len(listframes)}\n\n"
    sm.save_into_pdf(listframes, title, numberimg, color, deformation, numerotation, settitle, imgcrop, False, 127)
    yield "data: 90\n\n"
    sm.extract_audio(title)
    yield "data: 100\n\n"

@app.route("/traitement/", methods=['POST'])
def traitement():

    title, url = request.form.get('title'), request.form.get('url')
    threshold, frequency, color, numberimg = float(request.form.get('threshold')), float(request.form.get('frequency')), int(request.form.get('color')), int(request.form.get('numberimg'))
    numerotation, deformation, settitle = request.form.get('numerotation'), request.form.get('deformation'), request.form.get('settitle')
    crop = [request.form.get('cropLeft_ech'), request.form.get('cropTop_ech'), request.form.get('cropRight_ech'), request.form.get('cropBottom_ech')]
    imgcrop = [request.form.get('cropLeft_pre'), request.form.get('cropTop_pre'), request.form.get('cropRight_pre'), request.form.get('cropBottom_pre')]

    if title and url and 0 <= threshold <= 1 and frequency:
        session["title"] = title
        session['url'] = url
        return Response(generate(title, url, frequency, threshold, color, numberimg, numerotation, deformation, settitle, crop, imgcrop), mimetype='text/event-stream')
    else:
        return "<p>Il y a une erreur dans les informations saisies</p>"

@app.route("/download/<filename>",  methods = ['GET', 'POST'])
def download_file(filename):
    if filename == "mp3":
        return send_file(f"{sm.get_folderpath()}/{sm.get_valid_filename(session['title'])}.mp3", as_attachment=True)
    elif filename == "pdf":
        return send_file(f"{sm.get_folderpath()}/{sm.get_valid_filename(session['title'])}.pdf", as_attachment=True)
    elif filename == "zip":
        sm.create_zip(session['title'])
        return send_file(f"{sm.get_folderpath()}/{sm.get_valid_filename(session['title'])}.zip", as_attachment=True)
    elif filename == "frames":
        data = request.get_json() 
        selectedframes_id = data.get('selectedFrameIds')
        color = data.get('color')
        cropper_value = data.get('cropper_value')
        sm.create_frameszip(session['title'], selectedframes_id, color, cropper_value)
        zip_filename = f"frames_{sm.get_valid_filename(session['title'])}.zip"
        zip_path = os.path.join(sm.get_folderpath(), zip_filename)
        response = make_response(send_file(zip_path, as_attachment=True))
        response.headers['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response
    else:
        return jsonify({"error": "Un problème est survenu"}), 400

@app.route('/pdf/')
def get_pdf():
    print(session['title'])
    try:
        return send_file(f"{sm.get_folderpath()}/{sm.get_valid_filename(session['title'])}.pdf", as_attachment=False, mimetype='application/pdf')
    except Exception as e:
        return f"An error occurred: {e}", 500
    
@app.route('/img/<step>')
def get_img(step):
    try:
        return send_file(f"{sm.get_folderpath()}/frame_{step}.jpg", as_attachment=False, mimetype='image/jpeg')
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route('/changepdf', methods=['POST'])
def change_pdf():
    data = request.get_json() 
    cropper_value = data.get('cropper_value')
    frames = data.get('frames')
    title = data.get("title")
    session['title'] = title
    settitle = data.get("settitle")
    color = int(data.get("color"))
    numberimg = int(data.get("numberimg"))
    numerotation = data.get("numerotation")
    deformation = data.get("deformation")
    black = data.get("black")
    print(black)
    sm.save_into_pdf(frames, title, numberimg, color, deformation, numerotation, settitle, cropper_value, True, black)
    sm.extract_audio(title)
    return "PDF généré avec succès!", 200

@app.route('/generate-thumbnail', methods=['POST'])
def thumbnail():
    data = request.json
    video_url = data.get('url')
    if video_url:
        return sm.generate_thumbnail(video_url)
    else:
        return jsonify({"error": "URL manquante", "thumbnailUrl": "/static/img/problem.png"}), 400

if __name__ == '__main__':
    FlaskUI(app=app, server="flask").run()
