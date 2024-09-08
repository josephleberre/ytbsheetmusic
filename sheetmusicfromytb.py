import numpy
import re
import yt_dlp
import cv2 as cv
from fpdf import FPDF
from moviepy.editor import VideoFileClip
from skimage.metrics import structural_similarity as ssim
import os, sys, zipfile, io
from math import floor
from flask import jsonify

#VARIABLES GLOBALES

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

folder_path = None
video_filename = None

#FONCTIONS UTILITAIRES

def get_valid_filename(name):
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    return s

def get_folderpath():
    global folder_path
    return folder_path

def extract_video_id(url):
    match = re.search(r'[?&]v=([^&]+)', url)
    return match.group(1) if match else None

def clean_old_directories(new_dir_prefix, base_path, current_folder):
    for item in os.listdir(os.path.join(BASE_DIR, base_path)):
        item_path = os.path.join(BASE_DIR, base_path, item)
        if item.startswith(new_dir_prefix) and os.path.isdir(item_path) and item != current_folder:
            for root, dirs, files in os.walk(item_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(item_path)

# IMPORT THE YOUTUBE VIDEO

def video_download(link):
    global folder_path, video_filename
    video_id = extract_video_id(link)
    if not video_id:
        return jsonify({"error": "Identifiant de vidéo non trouvé dans l'URL"}), 400

    base_path = 'static/run'
    folder_name = f"sm_{video_id}"
    folder_path = os.path.join(BASE_DIR, base_path, folder_name)
    

    # Ensure folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    clean_old_directories("sm_", base_path, folder_name)

    yt_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(folder_path, f"{video_id}.%(ext)s"),
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            ydl.download([link])
        
        # Identify the actual downloaded file
        for filename in os.listdir(folder_path):
            if filename.startswith(video_id) and filename.split('.')[-1] in ['mp4', 'webm', 'mkv', 'avi', 'mov']:
                video_filename = os.path.join(folder_path, filename)
                break

    except Exception as e:
        return jsonify({"error": f"Erreur lors du téléchargement de la vidéo : {str(e)}"}), 500

    return jsonify({"message": "Vidéo téléchargée avec succès."})

def generate_thumbnail(video_url):
    global folder_path, video_filename
    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Identifiant de vidéo non trouvé dans l'URL", "thumbnailUrl": "/static/img/problem.png"}), 400

    base_path = 'static/run'
    folder_name = f"sm_{video_id}"
    folder_path = os.path.join(BASE_DIR, base_path, folder_name)
    thumbnail_path = os.path.join(folder_path, f"{video_id}_thumbnail.jpg")

    # Ensure folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if os.path.exists(thumbnail_path):
        return jsonify({"thumbnailUrl": f"{base_path}/{folder_name}/{video_id}_thumbnail.jpg"})

    clean_old_directories("sm_", base_path, folder_name)

    # Identify the actual downloaded file if not already set
    if video_filename is None or not os.path.exists(video_filename):
        yt_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(folder_path, f"{video_id}.%(ext)s"),
            'noplaylist': True,
        }

        try:
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                ydl.download([video_url])
            
            for filename in os.listdir(folder_path):
                if filename.startswith(video_id) and filename.split('.')[-1] in ['mp4', 'webm', 'mkv', 'avi', 'mov']:
                    video_filename = os.path.join(folder_path, filename)
                    break

        except Exception as e:
            return jsonify({"error": f"Erreur lors du téléchargement de la vidéo : {str(e)}", "thumbnailUrl": "/static/img/problem.png"}), 500

    cap = cv.VideoCapture(video_filename)
    if not cap.isOpened():
        return jsonify({"error": "Impossible de lire la vidéo", "thumbnailUrl": "/static/img/problem.png"}), 500

    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    middle_frame_number = total_frames // 2
    cap.set(cv.CAP_PROP_POS_FRAMES, middle_frame_number)
    
    ret, frame = cap.read()
    if not ret:
        return jsonify({"error": "Impossible de lire le frame de la vidéo", "thumbnailUrl": "/static/img/problem.png"}), 500
    
    cv.imwrite(thumbnail_path, frame)
    return jsonify({"thumbnailUrl": f"{base_path}/{folder_name}/{video_id}_thumbnail.jpg"})


#CONVERT VIDEO INTO A LIST OF FRAMES

def extract_frames(frequency):
    global video_filename
    cap = cv.VideoCapture(video_filename)
    if not cap.isOpened():
        raise Exception("Impossible d'ouvrir la vidéo.")

    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    frame_rate = float(frequency)  # Desired frame rate in frames per second
    fps = cap.get(cv.CAP_PROP_FPS)
    frame_interval = int(1000 / frame_rate)  # Frame interval in milliseconds
    duration = round(total_frames / fps)

    frames_list = []
    current_time = 0

    while True:
        cap.set(cv.CAP_PROP_POS_MSEC, current_time)
        ret, frame = cap.read()
        if not ret:
            print("Plus de vignettes. Fin du processus...")
            break
        frames_list.append(frame)
        print(round(current_time / 1000), "/", duration, "s")
        current_time += frame_interval

    return frames_list

def get_different_frames(threshold, list, color, crop):
    global folder_path
    comparison = []
    listcolor = []
    listframes = []

    for i in range(0, len(list)):
            listcolor.append(cv.cvtColor(list[i], cv.COLOR_BGR2GRAY))
            _, binary_frame = cv.threshold(listcolor[i], 127, 255, cv.THRESH_BINARY)
            comparison.append(binary_frame)
    
    if color==0:
        listcolor = comparison
    elif color == 2:
        listcolor = list

    output_file = f"{folder_path}/frame_0.jpg"
    cv.imwrite(output_file, list[0])
    listframes.append(listcolor[0])
    print(f"La vignette 0 a été sauvegardée.")
    for i in range(1, len(list)-1):
        score, _ = ssim(comparison[i][int(crop[1]):comparison[i].shape[0]-int(crop[3]), int(crop[0]):comparison[i].shape[1]-int(crop[2])], comparison[i+1][int(crop[1]):comparison[i].shape[0]-int(crop[3]), int(crop[0]):comparison[i].shape[1]-int(crop[2])], full=True)
        if(score < float(threshold)):
            output_file = f"{folder_path}/frame_{len(listframes)}.jpg"
            cv.imwrite(output_file, list[i+1])
            listframes.append(listcolor[i+1])
            print(f"La vignette {i} a été sauvegardée.")
    return listframes

def save_into_pdf(listframe, title, nbr, color, deformation, numerotation, settitle, imgcrop, change = False, black = 127):
    global folder_path
    pages = []
    if change == True:
        listframes = []
        for i in listframe:
            filename = f"{folder_path}/frame_{int(i)}.jpg"
            if os.path.exists(filename):
                if color != 2:
                    img = cv.imread(filename, cv.IMREAD_GRAYSCALE)
                    if color == 0:
                        _, img = cv.threshold(img, int(black), 255, cv.THRESH_BINARY)
                else:
                    img = cv.imread(filename)
                listframes.append(img)
            else:
                break

        if listframes == []:
            print("Aucune image trouvée.")
            return
    else :
        listframes = listframe

    if color !=2:
        h, w = listframes[0][int(imgcrop[1]):listframes[0].shape[0]-int(imgcrop[3]), int(imgcrop[0]):listframes[0].shape[1]-int(imgcrop[2])].shape
    else:
        h, w, _ = listframes[0][int(imgcrop[1]):listframes[0].shape[0]-int(imgcrop[3]), int(imgcrop[0]):listframes[0].shape[1]-int(imgcrop[2])].shape
    if int(nbr) == 0:
        coef = 2443/w
        nbr = floor(3508/(h*coef))
    
    if(len(listframes)%int(nbr) != 0):
        if color != 2:
            img = numpy.ones((listframes[0].shape[0], listframes[0].shape[1]), dtype=numpy.uint8) * 255
        else:
            img = numpy.ones((listframes[0].shape[0], listframes[0].shape[1], 3), dtype=numpy.uint8) * 255
        for i in range(nbr - (len(listframes)%nbr)):
            listframes.append(img)

    pages = []
    for i in range(len(listframes)//nbr):
        page = listframes[i*nbr][int(imgcrop[1]):listframes[i*nbr].shape[0]-int(imgcrop[3]), int(imgcrop[0]):listframes[i*nbr].shape[1]-int(imgcrop[2])]
        for l in range(nbr-1):
            page = numpy.concatenate((page, listframes[i*nbr+l+1][int(imgcrop[1]):listframes[i*nbr+l+1].shape[0]-int(imgcrop[3]), int(imgcrop[0]):listframes[i*nbr+l+1].shape[1]-int(imgcrop[2])]), axis=0)
        output_file = f"{folder_path}/pages{i}.jpg"
        pages.append(output_file)
        cv.imwrite(output_file, page)
        print(f"La page {i} a été sauvegardée.")
    
    save_images_as_pdf(pages, f"{folder_path}/{get_valid_filename(title)}.pdf", numerotation, deformation, title, settitle)


def save_images_as_pdf(image_files, output_pdf, numberpage, deformation, title, settitle):
    
    output_dir = os.path.dirname(output_pdf)
    for file in os.listdir(output_dir):
        if file.endswith(".pdf"):
            os.remove(os.path.join(output_dir, file))
    
    pdf = FPDF()
    pdf.set_auto_page_break(False, margin = 0.0)

    for i, img_file in enumerate(image_files):
        pdf.add_page()
        img = cv.imread(img_file)
        img_height, img_width, _ = img.shape
        img_ratio = img_width / img_height
        
        page_width, page_height = 190, 275
        page_ratio = page_width / page_height

        if deformation == "on" or deformation == True:
            fit_width, fit_height = page_width, page_height
        else:
            if img_ratio > page_ratio:
                fit_width = page_width
                fit_height = fit_width / img_ratio
            else:
                fit_height = page_height
                fit_width = fit_height * img_ratio
        if (settitle == "on" or settitle == True) and i == 0:
            pdf.set_y(8)
            pdf.set_font("Arial", "B", 32)
            pdf.cell(0, 10, f'{title}', 0, 0, 'C')
            if deformation == "on" or deformation == True:
                fit_height = 265
                x_offset = (210 - fit_width) / 2
                y_offset = (297 - fit_height) / 2 + 5
            else:
                if img_ratio < page_ratio:
                    fit_height = 265
                    fit_width = fit_height * img_ratio
                    x_offset = (210 - fit_width) / 2
                    y_offset = (297 - fit_height) / 2 + 5
                else:
                    x_offset = (210 - fit_width) / 2
                    y_offset = (297 - fit_height) / 2 - 1
        else:
            x_offset = (210 - fit_width) / 2
            y_offset = (297 - fit_height) / 2 - 1


        pdf.image(img_file, x_offset, y_offset, fit_width, fit_height)
        print(folder_path)

        if numberpage == "on" or numberpage == True:
            pdf.set_y(283)
            pdf.set_font("Arial", "I", 8)
            pdf.cell(0, 10, f'{title} - Page {i + 1}', 0, 0, 'R')
    
    pdf.output(output_pdf)
    print(f"Le PDF a été sauvegardé sous {output_pdf}")

def extract_audio(title):
    global folder_path, video_filename

    # Générer le nom du fichier MP3 attendu
    new_audio_filename = f"{get_valid_filename(title)}.mp3"
    new_audio_filepath = os.path.join(folder_path, new_audio_filename)

    # Vérifier si des fichiers MP3 existent déjà dans le dossier
    existing_mp3_files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]
    print(folder_path)

    if existing_mp3_files:
        # Remplacer les fichiers existants par le nouveau nom
        for old_mp3 in existing_mp3_files:
            old_mp3_path = os.path.join(folder_path, old_mp3)
            os.rename(old_mp3_path, new_audio_filepath)
        print(f"Le fichier audio existant a été renommé en {new_audio_filename}.")
    else:
        # Extraire l'audio et le sauvegarder si aucun fichier MP3 n'existe
        audio = VideoFileClip(video_filename).audio
        audio.write_audiofile(new_audio_filepath)
        audio.close()
        print("Audio extrait et sauvegardé !")

def create_zip(title):
    global folder_path

    for file in os.listdir(folder_path):
        if file.endswith(".zip"):
            os.remove(os.path.join(folder_path, file))
            print(f"{file} supprimé.")

    # Créer un buffer en mémoire pour le fichier zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as z:
        pdf_path = f"{folder_path}/{get_valid_filename(title)}.pdf"
        mp3_path = f"{folder_path}/{get_valid_filename(title)}.mp3"
        z.write(pdf_path, os.path.basename(pdf_path))
        z.write(mp3_path, os.path.basename(mp3_path))
    
    # Réinitialiser le pointeur du buffer
    zip_buffer.seek(0)

    # Sauvegarder le buffer dans un fichier .zip
    zip_filename = f"{folder_path}/{get_valid_filename(title)}.zip"
    with open(zip_filename, "wb") as f:
        f.write(zip_buffer.getvalue())
    
    print(f"Fichier zip créé : {zip_filename}")

def create_frameszip(title, selectedframesid, color, imgcrop):
    global folder_path
    print(folder_path)

    for file in os.listdir(folder_path):
        if file.endswith(".zip"):
            os.remove(os.path.join(folder_path, file))
            print(f"{file} supprimé.")

    # Créer un buffer en mémoire pour le fichier zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as z:
        for frame in selectedframesid:
            path = f"{folder_path}/frame_{frame}.jpg"
            image = cv.imread(path)
            image = image[int(imgcrop[1]):image.shape[0]-int(imgcrop[3]), int(imgcrop[0]):image.shape[1]-int(imgcrop[2])]
            if int(color) == 0:
                newimage = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
                _, newimage = cv.threshold(newimage, 127, 255, cv.THRESH_BINARY)
            elif int(color) == 1:
                newimage = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            else:
                newimage = image
            temp_path = f"{folder_path}/frame{frame}.jpg"
            cv.imwrite(temp_path, newimage)
            z.write(temp_path, os.path.basename(temp_path))
            os.remove(temp_path)
    
    # Réinitialiser le pointeur du buffer
    zip_buffer.seek(0)

    # Sauvegarder le buffer dans un fichier .zip
    zip_filename = f"{folder_path}/frames_{get_valid_filename(title)}.zip"
    with open(zip_filename, "wb") as f:
        f.write(zip_buffer.getvalue())
    
    print(f"Fichier zip créé : {zip_filename}")