import requests
import os
import time
import argparse

#
server_key_len = 36
url_upload = 'http://127.0.0.1:8900/api/qr_upload'  # upload server URL
url_state = 'http://127.0.0.1:8900/api/qr_state'  # state server URL


# upload pdf file to server
def upload_pdf(file_path):
    response_key = ''
    upload_ok = False

    # Open the file to be uploaded
    file = open(file_path, 'rb')

    try:
        # Send the file to the server
        response = requests.post(url_upload, files={'file': file})
        # Receive and parse the JSON response
        result = response.json()
        # Get Server State
        response_key = result.get("key")

        # Recived response_key
        if(response_key is None):
           print('error ... response url_upload')
        elif(len(response_key) < server_key_len):
            print(f'error ... {response_key}')
        else:
            print(f'pdf key id ... {response_key}')
            upload_ok = True

    except:
        print('Error ... connect server')

    return upload_ok, response_key

# This obtains status information using the key received from the server.
def get_server_pdf_state(response_key):

    result_json_info = []

    try:
        # Recived response_key
        if(response_key is None):
           print('error ... response url_upload')
        elif(len(response_key) < server_key_len):
            print(f'error ... {response_key}')

        else:
            state = 0
            while int(state) < 100 :
                request_data = {
                    "request_key": f'{response_key}'
                }
                response = requests.post(url_state, json=request_data)
                # Receive and parse the JSON response
                result = response.json()
                state = result.get("state")
                if(state is None):
                    break

                print('processing status : ' + state)
                time.sleep(5)
                if(int(state) < 0):
                    print("Server State Error.")
                    break

            # OK
            if int(state) == 100 :
                result_json_info = result.get("result")
                return result_json_info

    except:
        print('Error ... connect server')
        return result_json_info


# main driver function
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, default=None, help='input pdf')
    args = parser.parse_args()

    input_path = args.i
    key_file_path = './key_id'
    key_info = ''

    # if there is no parameter option or there is no file, the stored key_id is used.
    if os.path.exists(str(input_path)) == False:
        # read previous response key
        if os.path.exists(key_file_path):
            with open(key_file_path, 'r') as file:
                key_info = file.read()

        if len(key_info) < server_key_len:
            # if no exist
            print("option : -i input pdf file")
        else:
            # get results for server key_id
            print(f'pdf key id : {key_info}')
            result_json_info = get_server_pdf_state(key_info)
            print(result_json_info)

    else:
        # upload
        upload_state, key_info = upload_pdf(str(input_path))
        if upload_state == True:
            # Save Key
            with open(key_file_path, 'w') as file:
                file.write(key_info)

            # get results for server key_id
            result_json_info = get_server_pdf_state(key_info)
            print(result_json_info)
