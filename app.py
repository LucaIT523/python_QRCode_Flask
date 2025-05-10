
from flask import Flask, request, jsonify
import os
import uuid
import subprocess
import threading
import platform

SERVER_PORT = 8900


# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

def execute_python_file(file_path, parameters):
    plt = platform.system()

    # Execute the Python file using subprocess
    try:
        if plt == "Windows":
            result = subprocess.run(['python', file_path] + parameters, capture_output=True, text=True, check=True)
        else:
            result = subprocess.run(['python3', file_path] + parameters, capture_output=True, text=True, check=True)
        #print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Execution failed with error:", e)


@app.route('/api/qr_state', methods=['POST'])
def handle_state_request():
    response_data = {"state": '-1'}
    request_key = ''
    state_data = ""

    request_data = request.get_json()
    print(request_data)
    request_key = request_data.get("request_key")

    if (request_key is None):
        return jsonify(response_data)

    state_file = "./work/" + request_key + "/state"
    try:
        with open(state_file, 'r') as file:
            state_data = file.read()
    except :
        state_data = "5"

    if int(state_data) < 100 :
        # Create the response data
        response_data = {"state": f'{state_data}'}
        return jsonify(response_data)

    elif int(state_data) == 100 :
        response_data = {"state": f'100'}
        result_file = "./work/" + request_key + "/result"
        try:
            with open(result_file, 'r') as file:
                file_data = file.read()
        except:
            response_data = {'': ''}
        else:
            response_data.update({'result': f'{file_data}'})

        return jsonify(response_data)


@app.route('/api/qr_upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'key': 'error - no uploaded'})

    try:
        file = request.files['file']
        unique_id = str(uuid.uuid4())
        unique_filename = unique_id  + '_' + file.filename
        # create work dir
        work_dir = "./work"
        isExist = os.path.exists(work_dir)
        if not isExist:
            os.makedirs(work_dir)
        work_dir = work_dir + f'/{unique_id}'
        isExist = os.path.exists(work_dir)
        if not isExist:
            os.makedirs(work_dir)
        # save uploaded file
        file_save_path = f'{work_dir}/{unique_filename}'
        file.save(file_save_path)

        # Start a new thread to execute the Python file asynchronously
        parameters = ['-i', f'{file_save_path}', '-dir', f'{unique_id}']
        print(parameters)
        thread = threading.Thread(target=execute_python_file, args=('./pdf_qrcode_flask.py', parameters))
        thread.start()

        # Return the result as JSON
        result = {'key': f'{unique_id}' }
    except:
        result = {'key': 'error upload_file' }

    return jsonify(result)

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'QR-PDF Flask Server'


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(host='0.0.0.0', port=SERVER_PORT)