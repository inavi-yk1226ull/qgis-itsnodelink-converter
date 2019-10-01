# -*- coding: utf-8 -*-
from base64 import b64encode, b64decode
from .Cryptodome.Cipher import AES
from .Cryptodome.Util.Padding import pad, unpad

'''
key       : 사용자의 비밀번호 SHA1 암호화 후 32자리까지 잘라냄
inputText : 웹서버에서 전달받은 데이터
return    : AES256 암호화한 결과값 (Base64 인코딩)
'''
def encrypt_Data(inputText = "", key = ""):
    # 암호화 객체 생성
    # iv = 초기화 벡터, 데이터 첫블록 고유화 목적
    cipher = AES.new(key, AES.MODE_CBC, iv = bytes(16))
    # 암호화, pad는 데이터 블록 사이즈를 맞추기 위함, 1블록 = 16byte
    ciphertext = cipher.encrypt(pad(inputText.encode(), AES.block_size))
    # base64 인코딩 후 반환
    return b64encode(ciphertext).decode('utf-8')

'''
key       : 사용자의 비밀번호 SHA1 암호화 후 32자리까지 잘라냄
inputText : 로컬JSON파일에서 읽은 데이터
return    : 복호화 결과 값
'''
def decrypt_Data(inputText = "", key = ""):
    # 복호화 객체 생성
    # iv = 초기화 벡터, 데이터 첫블록 고유화 목적
    cipher = AES.new(key, AES.MODE_CBC, iv = bytes(16))
    # base64 디코드
    ct = b64decode(inputText)
    # 복호화
    plaintext = cipher.decrypt(ct)
    # 암호화 과정에서 추가한 블록 패딩 삭제
    pt = unpad(plaintext, AES.block_size)
    # 반환
    return pt.decode()
