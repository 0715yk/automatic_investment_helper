import os
import jwt
import uuid
import requests
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 API 키와 서버 URL 가져오기
access_key = os.getenv('UPBIT_OPEN_API_ACCESS_KEY')
secret_key = os.getenv('UPBIT_OPEN_API_SECRET_KEY')
server_url = os.getenv('UPBIT_OPEN_API_SERVER_URL')


def get_account_info():
    # JWT 페이로드 생성
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),  # 고유한 요청 식별자
    }

    # JWT 토큰 생성

    jwt_token = jwt.encode(payload, secret_key, algorithm="HS256")
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
        'Authorization': authorization,
    }

    # 업비트 계좌 정보 조회 요청
    try:
        res = requests.get(server_url + '/v1/accounts', headers=headers)
        res.raise_for_status()  # 요청 실패 시 예외 발생
        account_info = res.json()

        return account_info
    except requests.exceptions.RequestException as e:
        print("Failed to fetch account information:", e)