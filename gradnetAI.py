import pandas as pd
import numpy as np
import os
import re
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

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

DATA_IN_PATH = './data_in/'
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

r = open("./output/TOEIC.txt", 'rt', encoding='UTF-8')
testTEXT = []
testTEXT.append(preprocessing(r.read(), remove_stopwords = True))

test_data_features = vectorizer.transform(testTEXT)


if not os.path.exists(DATA_OUT_PATH):
    os.makedirs(DATA_OUT_PATH)
    
# 위에서 만든 랜덤 포레스트 분류기를 통해 예측값을 가져온다.
result = forest.predict(test_data_features)

if result[0] == 0 :
    print("TOEIC성적표 입니다.")
else:
    print("TOEIC성적표가 아닙니다.")
