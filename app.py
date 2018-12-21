import os
from flask import Flask, request
from pprint import pprint as pp
import requests
import random

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

api_url = 'https://api.hphk.io/telegram'
token = os.getenv('TELE_TOKEN')

@app.route(f'/{token}', methods=['POST'])
def telegram():
    # naver api를 사용하기 위한 변수
    naver_client_id = os.getenv('NAVER_ID')
    naver_client_secret = os.getenv('NAVER_SECRET')
    
    # tele_dict = 데이터 덩어리
    tele_dict = request.get_json()
    pp(request.get_json())
    
    # 유저 정보
    chat_id = tele_dict["message"]["from"]["id"]
    # print(chat_id)
    # 유저가 입력한 데이터
    text = tele_dict.get("message").get("text")
    #안녕하세요
    #로또
    #번역 안녕하세요 =>번역
    
    # print(text)
    
    #사진인지아닌지>>번역인지아닌지>>
    
    tran = False
    img = False
     #사용자가 이미지를 넣었는지 체크
    #if tele_dict['message']['photo'] is not None:
    if tele_dict.get('message').get('photo') is not None:
    # None 이 아니면 이미지
        img = True 
     
    #text(유저가입력한데이터) 제일 앞 두글자가 번역
    else:
        if text[:2]=="번역":
        # 번역 안녕하세요
            tran = True
            text = text.replace("번역","")
        #번역을 빈스트링으로 바꿈
        #  안녕하세요
        
    
    
    if tran:
        papago = requests.post("https://openapi.naver.com/v1/papago/n2mt",
                    headers = {
                        "X-Naver-Client-Id":naver_client_id,
                        "X-Naver-Client-Secret":naver_client_secret
                    },
                    data = {
                        'source':'ko',
                        'target':'en',
                        'text':text
                    }
        )
        pp(papago.json())
        text = papago.json()['message']['result']['translatedText']
        
    elif img:
        text = "사용자가 이미지를 넣었어요"
        
        #텔레그램에서 사진정보 가져오기
        file_id = tele_dict['message']['photo'][-1]['file_id']
        file_path = requests.get(f"{api_url}/bot{token}/getFile?file_id={file_id}").json()['result']['file_path']
        file_url = f"{api_url}/file/bot{token}/{file_path}"
        print(file_url)\
        
        #사진을 유명인 인식 api로 넘겨주기
        file = requests.get(file_url, stream=True) 
        clova = requests.post("https://openapi.naver.com/v1/vision/celebrity",
                    headers = {
                        "X-Naver-Client-Id":naver_client_id,
                        "X-Naver-Client-Secret":naver_client_secret
                    },
                    files = {
                        'image':file.raw.read()
                    }
        )
        #가져온 데이터중에서 필요한 정보 빼오기
        pp(clova.json())
        # 인식이 되었을때
        if clova.json().get('info').get('faceCount'):
            text = clova.json()['faces'][0]['celebrity']['value']
        # 인식이 되지 않았을때
        else:
            text = "얼굴이 없어요 ㅠㅠㅠ"
    
    elif text=="메뉴":
        menu_list = ["한식","중식","양식","분식","선택식"]
        text = random.choice(menu_list)
    elif text=="로또":
        numbers = list(range(1,46))
        text = random.sample(numbers,6)
    
    

    
    
    
    # 유저에게 그대로 돌려주기
    requests.get(f'{api_url}/bot{token}/sendMessage?chat_id={chat_id}&text={text}')
    
    
    return '', 200
    
app.run(host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',8080)))
        