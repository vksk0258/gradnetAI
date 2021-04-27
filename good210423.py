import io
import os
import re
import PyPDF2
import pikepdf
import pandas as pd
import numpy as np
from google.cloud import vision_v1
from openpyxl import Workbook
from flask import Flask, jsonify, request  # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

source_path = "./input/"
destination_path = "./output/"


def create_app():

    app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
    @app.route('/')  # 데코레이터 이용, '/hello' 경로에 클래스 등록

    def TOEIC():
        name = str(request.args['name'])
        type = str(request.args['type'])
        file_name = name + ".pdf"
        
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
            output_path = source_path + "decrypted_" + file_name
            file_path = source_path + file_name
            pdf = pikepdf.Pdf.new()

            for _, page in enumerate(input_pdf.pages):
                pdf.pages.append(page)

            pdf.save(output_path)
            input_pdf.close()
            print("saved at : {}".format(output_path))

            file_path = source_path + "decrypted_" + file_name

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

        def preprocessing(text, remove_stopwords = False ): 
            # 불용어 제거는 옵션으로 선택 가능하다.
            

            # 2. 영어가 아닌 특수문자들을 공백(" ")으로 바꾸기
            text = re.sub("[^ ㄱ-ㅣ가-힣A-Za-z0-9]", " ",text)

            # 3. 대문자들을 소문자로 바꾸고 공백단위로 텍스트들 나눠서 리스트로 만든다.
            words = text.lower().split()

            if remove_stopwords: 
                # 4. 불용어들을 제거
            
                #영어에 관련된 불용어 불러오기
                stops = set(stopwords.words("english"))
                # 불용어가 아닌 단어들로 이루어진 새로운 리스트 생성
                words = [w for w in words if not w in stops]
                # 5. 단어 리스트를 공백을 넣어서 하나의 글로 합친다.	
                clean_review = ' '.join(words)

            else: # 불용어 제거하지 않을 때
                clean_review = ' '.join(words)

            return clean_review

        DATA_IN_PATH = './'+type+'/'
        DATA_OUT_PATH = './data_out/'
        TRAIN_CLEAN_DATA = 'train_clean.csv'
        TEST_SIZE = 0.2
        RANDOM_SEED = 42

        train_data = pd.read_csv(DATA_IN_PATH + TRAIN_CLEAN_DATA)

        # 결측값 제거를 위해 판다스 데이터프레임으로 변환
        train_data1 = pd.DataFrame(train_data)

        train_data = train_data1.dropna()

        texts = list(train_data['text'])
        y = np.array(train_data['label'])

        vectorizer = CountVectorizer(analyzer = "word", max_features = 5000) 

        train_data_features = vectorizer.fit_transform(texts)

        train_input, eval_input, train_label, eval_label = train_test_split(train_data_features, y, test_size=TEST_SIZE, random_state=RANDOM_SEED)

        # 랜덤 포레스트 분류기에  100개 의사 결정 트리를 사용한다.
        forest = RandomForestClassifier(n_estimators = 100) 

        # 단어 묶음을 벡터화한 데이터와 정답 데이터를 가지고 학습을 시작한다.
        forest.fit( train_input, train_label )

        testTEXT = []
        testTEXT.append(preprocessing(r.read(), remove_stopwords = True))

        test_data_features = vectorizer.transform(testTEXT)


        if not os.path.exists(DATA_OUT_PATH):
            os.makedirs(DATA_OUT_PATH)
            
        # 위에서 만든 랜덤 포레스트 분류기를 통해 예측값을 가져온다.
        result = forest.predict(test_data_features)

        if result[0] == 0 :
            msg = type +" 입니다."
        else:
            msg = type+" 아닙니다"
        
        return jsonify(name, 
                        testTEXT,
                        msg)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=88)