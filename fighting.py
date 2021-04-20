import io
import os
import PyPDF2
import pikepdf
from google.cloud import vision_v1
from openpyxl import Workbook
from flask import Flask, jsonify, request  # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import


source_path = "./input/"
destination_path = "./output/"

file_list = os.listdir(source_path)

def create_app():

    app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
    @app.route('/')  # 데코레이터 이용, '/hello' 경로에 클래스 등록
        
    def hello():
        name = str(request.args['name'])
        file_name = name + ".pdf"

        for i in range(len(file_list)):
            client = vision_v1.ImageAnnotatorClient()
            file_path = source_path + file_name

            # Supported mime_type: application/pdf, image/tiff, image/gif
            mime_type = "application/pdf"

            try:
                with io.open(file_path, "rb") as f:
                    content = f.read()
                    pdf_reader = PyPDF2.PdfFileReader(open(file_path, "rb"), strict = False)
            #         pdf_reader = PyPDF2.PdfFileReader(f)
                    num_of_pages = pdf_reader.numPages

            except:
                output_path = source_path + "decrypted_" + file_list[i]
                file_path = source_path + file_name
                pdf = pikepdf.Pdf.new()

                for _, page in enumerate(input_pdf.pages):
                    pdf.pages.append(page)

                pdf.save(output_path)
                input_pdf.close()
                print("saved at : {}".format(output_path))

                file_path = source_path + "decrypted_" + file_list[i]

                with io.open(file_path, "rb") as f:
                    content = f.read()
                    pdf_reader = PyPDF2.PdfFileReader(open(file_path, "rb"), strict = False)
            #         pdf_reader = PyPDF2.PdfFileReader(f)
                    num_of_pages = pdf_reader.numPages


            input_config = {"mime_type": mime_type, "content": content}
            features = [{"type_": vision_v1.Feature.Type.DOCUMENT_TEXT_DETECTION}]


        def pdf2txt_w(path_num):
            pages = [1,2,3,4,5]
            requests = [{"input_config": input_config, "features": features, "pages": pages}]
            response = client.batch_annotate_files(requests=requests)

            for num, image_response in enumerate(response.responses[0].responses):
        #         print(u"Full text: {}".format(image_response.full_text_annotation.text))
                if (num==0):
                    with open(destination_path + file_name[0:-4] + '.txt', "w",encoding='UTF-8') as f:
                        f.write(response.responses[0].responses[num].full_text_annotation.text)
                else:
                    with open(destination_path + file_name[0:-4] + '.txt', "a",encoding='UTF-8') as f:
                        f.write(response.responses[0].responses[num].full_text_annotation.text)

                    
        # 6페이지 이상인 파일은 아래 함수를 호출하여 텍스트 추출
        def pdf2txt(page, path_num):
            pages = [i for i in range(page, page+5)]
            requests = [{"input_config": input_config, "features": features, "pages": pages}]
            response = client.batch_annotate_files(requests=requests)

            for num, image_response in enumerate(response.responses[0].responses):
        #         print(u"Full text: {}".format(image_response.full_text_annotation.text))

                with open(destination_path + file_name[0:-4] + '.txt', "a",encoding='UTF-8') as f:
                        f.write(response.responses[0].responses[num].full_text_annotation.text)

        for p in range(1, num_of_pages+1, 5):
            if(p==1):
                pdf2txt_w(1)
            else:
                pdf2txt(p, 1)

        path = destination_path + name + ".txt"
        r = open(path, 'rt', encoding='UTF-8')
        
        return jsonify(name, 
                        r.read())
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0')