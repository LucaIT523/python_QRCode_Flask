import os
import json
import shutil
import cv2
import numpy as np
import argparse
import pdf2image
import pytesseract
from pyzbar.pyzbar import decode
from PIL import Image
import platform

# from paddleocr import PaddleOCR
plt = platform.system()
if plt == "Windows":
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

#
pdf_data_info = []
QR_info_list = []
IMG_PATH = ""
"""
    Get QR code
"""
def GetQRInfo(image_path):
    QRData = ''

    decocdeQR = decode(Image.open(image_path))
    if len(decocdeQR) > 0:
        QRData = decocdeQR[0].data.decode('ascii')

    return QRData

"""
    Get Page Information
"""
def GetPageInfo(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))

    cur_page = 0
    total_page = 0

    try:
        # search "Page"
        pos = str(text).find('Page ')
        if pos >= 0 :
            temp_str = text[pos + 5 :]

            temp_str = temp_str.replace("I" , '1')
            temp_str = temp_str.replace("ft" , '1')
            temp_str = temp_str.replace("[" , '1')
            temp_str = temp_str.replace("]" , '1')
            temp_str = temp_str.replace("|" , '1')
            temp_str = temp_str.replace("l" , '1')
            temp_str = temp_str.replace("t" , '1')
            temp_str = temp_str.replace("Z" , '2')
            temp_str = temp_str.replace("z" , '2')
            temp_str = temp_str.replace("S" , '5')
            temp_str = temp_str.replace("s" , '5')
            temp_str = temp_str.replace("T" , '7')
            temp_str = temp_str.replace("$" , '8')

            # search "of"
            pos_of = str(temp_str).find(' of ')
            if(pos_of >= 0):
                strtemp = temp_str[:pos_of]
                cur_page = int(strtemp)

                temp_str = temp_str[pos_of + 4 :]
                pos_of_1 = str(temp_str).find(' ')
                pos_of_2 = str(temp_str).find('\n')
                if( pos_of_1 < 0):
                    pos_of = pos_of_2
                elif( pos_of_2 < 0):
                    pos_of = pos_of_1
                elif pos_of_1 >= 0 and pos_of_2 >= 0:
                    pos_of = min(pos_of_1, pos_of_2)
                else :
                    pos_of = -1
                if(pos_of >= 0):
                    total_page = int(temp_str[:pos_of])
            else:
                pos_of = str(temp_str).find(' ')
                strtemp = temp_str[:pos_of]
                cur_page = int(strtemp)
    except:
        cur_page = 0
        total_page = 0

    return cur_page, total_page

"""
    recognize QR image
"""
def image_proc(img_path):
    global IMG_PATH

    resultData = []
    QR_Info = ''
    in_img = Image.open(img_path)
    img_w,  img_h = in_img.size

    opencvImage = cv2.imread(img_path)
    h_cut = img_h // 5
    img_header = opencvImage[ :h_cut, :]
    img_bottom = opencvImage[h_cut * 4 :, :]

    img_header = cv2.resize(img_header, (int(img_w / 0.5), int(h_cut / 0.5)), interpolation=cv2.INTER_AREA)
    img_bottom = cv2.resize(img_bottom, (int(img_w / 0.5), int(h_cut / 0.5)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(f'{IMG_PATH}/header.png', img_header)
    cv2.imwrite(f'{IMG_PATH}/bottom.png', img_bottom)

    QR_hd = GetQRInfo(f'{IMG_PATH}/header.png')
    QR_bt = GetQRInfo(f'{IMG_PATH}/bottom.png')
    if len(QR_hd) > 0 :
        QR_Info = QR_hd
        # print(' QR_hd : ' + QR_hd)
    if len(QR_bt) > 0 :
        QR_Info = QR_bt
        # print(' QR_bt : ' + QR_bt)

    # ocr = PaddleOCR(use_angle_cls=True, lang='en')  # need to run only once to download and load model into memory
    # img_path = './image/bottom.png'
    # result = ocr.ocr(img_path, cls=False)
    # for idx in range(len(result)):
    #     res = result[idx]
    #     for line in res:
    #         print(line)

    cur_page, total_page = GetPageInfo(f'{IMG_PATH}/bottom.png')
    # print(' cur_page : ' + str(cur_page))
    # print(' total_page : ' + str(total_page))

    print(' QR_Info : ' + QR_Info)
    resultData.append(QR_Info)
    resultData.append(cur_page)
    resultData.append(total_page)

    return resultData

"""
    create pdf file by QR information
"""
def create_sub_pdf(start, end, qr_info, result_path):
    global IMG_PATH

    str_path = f'{IMG_PATH}/image_' + str(start) + '.png'
    im1 = Image.open(str_path)
    image_list = []
    for i in range(int(start)+1, int(end) + 1):
        str_path = f'{IMG_PATH}/image_' + str(i) + '.png'
        image_list.append(Image.open(str_path))

    qr_info = str(result_path) + "/" + str(start) + "~" + str(end) + "_" + qr_info + ".pdf"
    im1.save(qr_info, save_all=True, append_images=image_list)

"""
    Add QR info
"""
def add_qr_list(qr_info_liat, qr_info):
    if len(qr_info) <= 0 :
        return

    data_len = len(qr_info_liat)
    bFind = False
    for i in range(data_len) :
        if qr_info_liat[i] == qr_info :
            bFind = True
            break

    if bFind == False:
        qr_info_liat.append(qr_info)

def full_search_sub_info(pdf_data, qr_info):
    search_start = 0
    page_str = ''

    while True:
        start_num, end_num, search_start = search_sub_info(pdf_data, qr_info, search_start)
        if(int(search_start) < 0 ):
            break
        for i in range(start_num + 1, end_num + 2):
            page_str = page_str + str(i) + ','

    page_str = page_str[:len(page_str) - 1]
    return page_str


"""
    search files using QR information
"""
def search_sub_info(pdf_data, qr_info, search_start):
    data_len = len(pdf_data)
    start_pos = -1
    end_pos = -1
    b_find = False

    for i in range(data_len) :
        if i < int(search_start):
            continue

        if pdf_data[i][0] == qr_info:
            b_find = True
            if start_pos < 0 :
                start_pos = i
            end_pos = i

    if b_find == True:
        # modify end_pos
        if int(end_pos) == int(data_len) - 2:
            if pdf_data[end_pos + 1][0] == '' and pdf_data[end_pos + 1][2] == 0  :
                end_pos += 1
        elif int(end_pos) < int(data_len) - 2:
            if pdf_data[end_pos + 1][0] == '' and pdf_data[end_pos + 1][2] == 0 and len(pdf_data[end_pos + 2][0]) > 0 :
                end_pos += 1
            if pdf_data[end_pos + 1][0] == '' and (pdf_data[end_pos][2] - pdf_data[end_pos][1]) > 0 and pdf_data[end_pos][2] > 1 :
                end_pos += pdf_data[end_pos][2] - pdf_data[end_pos][1]

        # modify start_pos
        if pdf_data[start_pos][1] > 1 and pdf_data[start_pos][2] == 0:
            start_pos -= pdf_data[start_pos][1] - 1

        elif pdf_data[start_pos][1] > 1 and pdf_data[start_pos][2] > 0:
            if(pdf_data[start_pos][2] <= end_pos - start_pos):
                k = 0
            else:
                start_pos -= pdf_data[start_pos][1] - 1

        return start_pos, end_pos, end_pos + 1

    else:
        return start_pos, end_pos, -1

def delete_files_in_folder(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)


def set_state_info(file_path, data_info):
    # Open the file in write mode
    with open(file_path, 'w') as file:
        data = str(data_info)  # Data to be written
        file.write(data)


"""
    Main Function
"""
if __name__ == '__main__':

    # check argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, default=None, help='input pdf')
    parser.add_argument('-dir', type=str, default=None,  help='work folder')
    args = parser.parse_args()

    print("args.dir")
    print("args.i")
    work_dir = args.dir
    work_dir = "./work/" + work_dir

    input_path = args.i
    if os.path.exists(str(input_path)) == False:
        print("option : -i input pdf file")
    else:
        isExist = os.path.exists(work_dir)
        if not isExist:
            os.makedirs(work_dir)

        temp_path = work_dir + '/temp'
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        os.makedirs(temp_path)

        IMG_PATH = work_dir + "/image"
        isExist = os.path.exists(IMG_PATH)
        if not isExist:
            os.makedirs(IMG_PATH)

        # analysis for PDF file
        input_pdf = input_path
        print("Input file : " + input_pdf)
        # analysis for image
        print("pdf2image starting ...  ")
        set_state_info(f'{work_dir}/state', 10)
        images = pdf2image.convert_from_path(input_pdf, output_folder=temp_path)
        set_state_info(f'{work_dir}/state', 30)

        page_num = len(images)
        for i in range(page_num):
            print("Converting : " + f'image_{i+1}.png')
            images[i].save(f'{IMG_PATH}/image_{i+1}.png', 'PNG')

        set_state_info(f'{work_dir}/state', 48)

        # get needed information
        for i in range(page_num ):
            img_path = f'{IMG_PATH}/image_' + str(i+1) + '.png'
            print("Page processing : " + img_path)
            result = image_proc(img_path)
            pdf_data_info.append(result)
            add_qr_list(QR_info_list, result[0])

            val_state = int(50 + (int(i) * 100 / int(page_num)) * 5 / 10)
            set_state_info(f'{work_dir}/state', val_state)

        # search
        QR_JSON_Info = []
        for i in range(len(QR_info_list)):
            page_str = full_search_sub_info(pdf_data_info, QR_info_list[i])
            print("create pdf file : " + QR_info_list[i])
            # # create sub pdf file
            # create_sub_pdf(start_num + 1, end_num + 1, QR_info_list[i], result_path)
            # page_info = str(start_num + 1) + "-" + str(end_num + 1)
            QR_JSON_Info.append({f'{QR_info_list[i]}': page_str})

        json_data = json.dumps(QR_JSON_Info)
        set_state_info(f'{work_dir}/result', json_data)
        set_state_info(f'{work_dir}/state', 100)

        # delete temp file
        delete_files_in_folder(temp_path)
        delete_files_in_folder(IMG_PATH)


    print('-----END ------')






