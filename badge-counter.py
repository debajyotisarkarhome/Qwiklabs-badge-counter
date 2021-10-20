import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, current_app
from werkzeug.utils import secure_filename
import pandas as pd
import uuid

UPLOAD_FOLDER = os.getcwd() + "/temp"
ALLOWED_EXTENSIONS = {"xlsx", "xls", "odt", "csv"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def compute_badges(list):
    main_list=[]
    for url in list:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        badges = soup.findAll("span", attrs={"class": "ql-subhead-1 l-mts"})
        for i in range(0,len(badges)):
            badges[i] = badges[i].text.strip()

        main_list.append([len(badges)] + badges) 
    return main_list


def main_work(sheetFilePath, column):
    print(sheetFilePath)
    df = pd.read_excel(sheetFilePath)
    url_list=df[column].tolist()
    data= compute_badges(url_list)
    number_of_badges=[]
    badge_names=[]
    for userdata in data:
        number_of_badges.append(userdata[0])
        badge_names.append(userdata[1:])
    df["Number of badges"]=number_of_badges
    df["badge_names"]=badge_names
    df.to_excel(sheetFilePath)
    return('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCP Badge Counter</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-F3w7mX95PdgyTmZZMECAngseQB83DfGTowi0iMjiWaeVhAn4FJkqJByhZMI3AhiU" crossorigin="anonymous">
</head>
<body>
    <h1>GCP Badge Counter</h1>
    <br>
    <button onclick="location.href = '{}';" class="btn btn-primary" >Download Updated Sheet</button>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/js/bootstrap.bundle.min.js" integrity="sha384-/bQdsTh/da6pkI1MST/rWKFNjaCP5gBSY4sEBT38Q/9RBh9AH40zEOg7Hlq2THRZ" crossorigin="anonymous"></script>
</body>
</html>'''.format("/uploads/"+sheetFilePath[sheetFilePath.find("/temp/")+6:]))



@app.route("/")
def uploader_file():
    return render_template("upload.html")


@app.route("/uploader", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = str(uuid.uuid4().hex)+".xlsx"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            # Here return what's required
            return main_work(os.getcwd()+"/temp/"+filename,"qwiklabs_url")


@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    # Returning file from appended path
    return send_from_directory(directory=uploads, path=filename)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)