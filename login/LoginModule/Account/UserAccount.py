# -*- coding: utf-8 -*-
import enum
import urllib.request  # 서버 API 호출
import os # 사용자별 경로
import datetime  # 오프라인 사용시 날짜 기간 확인용
from ..JsonToTuple import convertStrToTuple  # 서버의 JSON데이터 튜플로 반환
import hashlib  # 비밀번호 SHA1 암호화
from ..CryptAES256 import encrypt_Data, decrypt_Data  # 암호화/복호화


class ErrorPointAccount:
    id = ""
    tims_id = ""
    email = ""
    user_name = ""
    permission = False
    pass


class Apps(enum.Enum):
    Juliet = 1
    Romeo = 2
    Mario = 3
    Laputa = 4
    PlugIn = 5
    pass


class UserAccount():

    def __init__(self, app):
        self._app = app
        self._id = None
        self._name = None
        self._teamName = None
        self._userColor = 0
        self._workFlagIndex = 0
        self._commentary = None
        self._serverMode = False
        self._timeToChangePassWord = False
        self._errorPointAccount = None
        self._teamList = list()
        self._authorityList = list()
        self._LeaderTeamList = list()
        self._loginServerIp = "http://10.10.82.42:8000"
        self._telegramKey = None
        self._telegramChatId = None
        pass

    # Json 저장용 폴더 생성하기
    def createfolder(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: 폴더 생성 ' + directory)

    # 웹 연결 및 정보 취득
    def getresponse(self, web=""):
        try:
            request = urllib.request.Request(web)
            response = urllib.request.urlopen(request)
            response_body = response.read()
            return response_body.decode('unicode_escape')
            pass
        except:
            return None
            pass

    # 권한 확인 (업무 명칭 or 팀장 권한인 팀 명칭)
    def CheckAuthority(self, workauthority):

        # 지도기술개발팀 우선 허용
        if self._teamName == "지도기술개발팀":
            pass

        # 팀장 여부
        for leaderTeam in self._LeaderTeamList:
            # TODO : 0722 왜 글자 수로 비교? 확인 필요.
            if workauthority == leaderTeam:
                return True
            pass

        # 권한 존재 여부
        for auth in self._authorityList:
            if workauthority == auth:
                return True
            pass
        return False

    def ServerLogin(self, id, password):
        # get Path
        path = "{0}\\Inavi\\_Login".format(os.getenv('APPDATA'))
        self.createfolder(path)

        # 생성된 디렉토리의 권한 취득
        os.chmod(path, 777)
        print(path)

        filepath = path + "\\" + id + ".JSON"
        print(filepath)

        # 파일 존재시 삭제? 왜?

        # id, pw 0글자 확인
        if len(id) == 0 and len(password) == 0:
            return False, "ID/비밀번호를 확인해주세요."

        sha1password = hashlib.sha1(password.encode("utf-8")).hexdigest()
        print(sha1password)

        appname = self._app.upper()

        try:
            loginurl = "{0}/account/api/login?user_id={1}&password={2}&client={3}".format(self._loginServerIp, id, sha1password, appname)
            response = self.getresponse(loginurl)
            if response is None:
                return False, "잘못된 JSON입니다."
            _tuple = convertStrToTuple(response)

            # 정보 확인
            is_right_information = True if _tuple.ret == 0 else False
            error_message = _tuple.msg

            if is_right_information:  # 정보확인 성공
                encrypt_write = encrypt_Data(response, str(sha1password[0:32]).encode())

                # 로컬 접속(비상)을 대비한 파일 작성
                with open(filepath, "w") as f:
                    f.write(encrypt_write)

                # 튜플에서 값 가져옴
                telegram_key = _tuple.data.telegram_key
                telegram_chat_id = _tuple.data.telegram_chat_id
                name = _tuple.data.name
                team_leader = _tuple.data.teamLeader
                groups = _tuple.data.group
                permission_groups = _tuple.data.permission_group

                if telegram_key is not None:
                    self._telegramKey = telegram_key
                    pass
                if telegram_chat_id is not None:
                    self._telegramChatId = telegram_chat_id
                    pass
                if name is not None:
                    self._name = name
                    pass
                if team_leader is not None:
                    self._LeaderTeamList.append(team_leader)
                    pass
                if groups is not None:
                    self._teamName = groups
                    pass
                if permission_groups is not None:
                    self._authorityList.append(permission_groups)
                    pass

                # 이거 3개 다 왜하는지 모르겠다. 기본에 있는거같은데..?
                team_leader_url = "{0}/account/api/check-teamleader?user_id={1}".format(self._loginServerIp, id)
                groups_url = "{0}/account/api/groups?user_id={1}".format(self._loginServerIp, id)
                permission_groups_url = "{0}/account/api/permission-groups?user_id={1}".format(self._loginServerIp, id)
                pass
            else:
                return False, error_message
                pass
            return True, "로그인 성공"
        except Exception as ex:
            return False, "서버가 응답이 없습니다."
        pass

    def LocalLogin(id, password):
        return False, "message"
    pass

pass
