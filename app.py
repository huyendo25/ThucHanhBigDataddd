from pickle import NONE

from cv2 import fastNlMeansDenoising
from flask import Flask, flash, request, redirect, url_for , jsonify , send_file ,send_from_directory
from werkzeug.utils import secure_filename
from crm import *
import json
import time

class DataModel:
    def __init__(self, result, message, item):
        self.result = result
        self.message = message
        self.item = item

class ErrorModel:
    def __init__(self, result, message,item):
        self.result = result
        self.message = message
        self.item = item

class ResponseModel:
    def __init__(self, data, error):
        self.data = data
        self.error = error

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'docx','doc','pdf'}

app = Flask(__name__, static_url_path='/static')
app.config['upload_folder'] = UPLOAD_FOLDER 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

input_file = {}
dic_new_text = {}

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    error = None
    data = None
    time_t = time.time()
    sess_id = request.args.get('sess_id')
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print('filename - ',filename)
            file_name, file_end = os.path.splitext(filename)
            path_file_name = file_name + '_' + sess_id
            path_file = os.path.join(app.config['upload_folder'], path_file_name )
            if not os.path.exists(path_file):
                os.makedirs(path_file)
            input_file[sess_id] = os.path.join(path_file, filename)
            print('save_path - ',input_file[sess_id])
            file.save(input_file[sess_id])
            img_org_base64 = start(input_file[sess_id])

            item = {"sess_id": sess_id , "image" : img_org_base64}
            print(type(img_org_base64))
            data = DataModel(True, " Xử lí file thành công ", item)
    time_s = time.time()
    print("Time upload file : {}".format(time_s-time_t))
    if error is not None:
        error = vars(error)
    if data is not None:
        data = vars(data)
    response = ResponseModel(data, error)
    return json.dumps(vars(response))

@app.route('/search', methods=['GET', 'POST'])
def search():
    error = None
    data = None
    sess_id = request.args.get('sess_id')
    if request.method == 'POST':
        key = request.form['text_change']
        try:
            img_base64, countKey = stage2(input_file[sess_id],key)
        except:
            item = {"sess_id": sess_id}
            data = DataModel(False, " Không tìm thấy tập tin! ", item)
            if error is not None:
                error = vars(error)
            if data is not None:
                data = vars(data)
            response = ResponseModel(data, error)
        else:
            if countKey == 0:
                item = {"sess_id": sess_id, "number_img": countKey}
                data = DataModel(False, " Không có chuỗi khớp ", item)
                if error is not None:
                    error = vars(error)
                if data is not None:
                    data = vars(data)
                response = ResponseModel(data, error)
            else:
                item = {"sess_id": sess_id, "number_img": countKey, "image":  img_base64}
                data = DataModel(True, " Ảnh trả về ", item)
                if error is not None:
                    error = vars(error)
                if data is not None:
                    data = vars(data)
                response = ResponseModel(data, error)
        return json.dumps(vars(response))

@app.route('/replace_file', methods=['GET', 'POST'])
def replace():
    error = None
    data = None
    sess_id = request.args.get('sess_id')
    contents = request.json
    numberList = []
    for content in contents:
        numberList.append(content['index'])
    key = contents[0]['name']
    value = contents[0]['replace_with']
    img_org_base64,output_file = stage3(input_file[sess_id],key,value,numberList)
    item = {"sess_id" : sess_id , "img_org_base64": img_org_base64,"url": output_file}
    data = DataModel(True, "File thay đổi thành công ", item)
    if error is not None:
        error = vars(error)
    if data is not None:
        data = vars(data)
    response = ResponseModel(data, error)
    return json.dumps(vars(response))

'''@app.route("/delete" ,methods=['GET', 'POST'])
def delete():
    error = None
    data = None
    path = './static/uploads'
    sess_id = request.args.get('sess_id')
    dirs = os.listdir(path)
    for folder in dirs:
        folder_id = folder.split('_')[-1]
        if sess_id == folder_id:
            path_del = os.path.join(path, folder)
            shutil.rmtree(path_del)
            item = {"sess_id": sess_id}
            data = DataModel(True, "Xóa file thành công ", item)
        else:
            item = {"sess_id": sess_id}
            error = ErrorModel(False, "File không tồn tại", item)
    if error is not None:
        error = vars(error)
    if data is not None:
        data = vars(data)
    response = ResponseModel(data, error)
    return json.dumps(vars(response))'''

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    app.run (host='0.0.0.0', port=4000)