import requests
from furl import furl
from .exceptions import *
import time

class Judge0:
    def __init__(self, Judge0_ip: str, X_Auth_Token: str, X_Auth_User: str):
        self.__judge0_ip = furl(Judge0_ip)
        self.__session: requests.Session = requests.session()
        self.__session.headers['X-Auth-Token'] = X_Auth_Token
        self.__session.headers['X-Auth-User'] = X_Auth_User
        self.__check_tokens()
        self.__init_languages_dict()

    def __check_tokens(self):
        """
        The method checks if the given tokens are valid. If invalid, it raises a requests.HTTPError exception; otherwise, it returns None. 
        """
        authn_response = self.__session.post(self.__judge0_ip / 'authenticate')
        authn_response.raise_for_status()
        authz_reponse = self.__session.post(self.__judge0_ip / 'authorize')
        authz_reponse.raise_for_status()

    def __init_languages_dict(self):
        languages_list = self.__session.get(self.__judge0_ip / 'languages').json()
        self.__languages = {item['id']: item['name'] for item in languages_list}

    @property
    def languages(self):
        "The method returns a dict of available languages"
        return self.__languages

    def submit_code(self, source_code: str, language_id: int, stdin: str | None = None, compile_timeout: int | None = None, run_timeout: int | None = None, check_timeout: int | None = None):
        if self.languages.get(language_id) is None:
            raise LanguageNotFound('Unknown language id. Use languages property to get a dict of available languages')
        
        data = {
            'source_code': source_code,
            'language_id': language_id
        }

        if stdin is not None:
            data['stdin'] = stdin
        if compile_timeout:
            data['compile_timeout'] = compile_timeout
        if run_timeout:
            data['run_timeout'] = run_timeout
        if check_timeout:
            data['check_timeout'] = check_timeout

        response = self.__session.post(self.__judge0_ip / 'submissions', json=data)
        response.raise_for_status()
        submission_data = response.json()
        return Submission(self, submission_data)
    
    def submit_file(self, source_code: str, language_id: int, stdin: str | None = None, compile_timeout: int | None = None, run_timeout: int | None = None, check_timeout: int | None = None):
        raise NotImplementedError

    def get_info(self, submission_token: str):
        response = self.__session.get(self.__judge0_ip / 'submissions' / submission_token)
        response.raise_for_status()
        return response.json()
    
    def get_status(self, submission: 'Submission'):
        response = self.__session.get(self.__judge0_ip / 'submissions' / submission.token)
        response.raise_for_status()
        return response.json().get('status').get('description')


class Submission:
    def __init__(self, judge0: Judge0, data: dict):
        self.__judge0 = judge0
        self.__token = data.get('token')
        self.__status: dict = data.get('status')
        self.__memory = data.get('memory')
        self.__time = data.get('time')
        self.__compile_output = data.get('compile_output')
        self.__stdout = None
        self.__stderr = None
        self.__message = data.get('message')

    def refresh(self):
        data: dict = self.__judge0.get_info(self.__token)
        self.__status = data.get('status')
        self.__memory = data.get('memory')
        self.__time = data.get('time')
        self.__compile_output = data.get('compile_output')
        self.__message = data.get('message')
        self.__stdout = data.get('stdout')
        self.__stderr = data.get('stderr')

    def get_result(self):
        self.refresh()
        if self.__status.get('id') in [1, 2]:
            raise NotProcessed
        data = self.__judge0.get_info(self.__token)
        return data

    def wait_for_completion(self, poll_interval: int = 1):
        while 1:
            self.refresh()
            if self.__status.get('id') in [1, 2]:
                time.sleep(poll_interval)
                continue
            break

    @property
    def token(self):
        return self.__token