import base64
import datetime
import json
import logging

import requests

from ai_cloud_sdk_4pd import models as ai_cloud_sdk_4pd_models


class Client:
    def __init__(
        self,
        config: ai_cloud_sdk_4pd_models.Config,
    ):
        self._token = config.token
        self._call_token = config.call_token

        self._blacklist_token = []
        self._blacklist_call_token = []

        # proxies 格式 {"China": ["http://localhost:port"], "HongKong": [], "Other": []}
        self._proxies = None
        # self._proxies = {"China": ["http://bj-aiyun.4paradigm.com"]}
        self._endpoint = config.endpoint
        self._region = config.region if config.region else 'China'

        self.__get_proxy_ip_config()
        self.__set_region_and_endpoint()
        self.__verify_tokens()

    def __set_region_and_endpoint(self) -> None:
        # 如果endpoint已给出且合法，则直接返回
        if self._endpoint:
            for region, endpoints in self._proxies.items():
                if self._endpoint in endpoints:
                    self._region = region
                    return

        # 如果endpoint未给出或不合法，且region存在且合法，则根据region确定endpoint
        if self._region:
            for region, endpoints in self._proxies.items():
                if self._region == region:
                    self._endpoint = endpoints[0]
                    return

        # 如果endpoint未给出或不合法，且region不存在或不合法，则默认endpoint(China)
        self._region = 'China'
        self._endpoint = self._proxies.get('China')[0]
        return

    def __verify_tokens(self) -> None:
        # 如果token或call_token未给出，则抛出异常
        if self._token is None or self._call_token is None:
            raise ValueError('token and call_token is required')

    def __get_proxy_ip_config(self) -> None:

        region_map = {
            'China': 'http://bj-aiyun.4paradigm.com/4pd_aiclound/config',
            'HongKong': 'http://hk-aiyun.4paradigm.com/4pd_aiclound/config',
        }

        proxy_config_url = region_map.get(self._region, region_map['China'])

        try:
            response = requests.get(proxy_config_url)
            response_json = response.json()
            data = response_json.get('data', {})
            proxies = data.get('proxies', {})
            self._proxies = proxies
        except Exception as e:
            raise e

    def audio_language_detection(
        self,
        request: ai_cloud_sdk_4pd_models.AudioLanguageDetectionRequest = None,
    ) -> ai_cloud_sdk_4pd_models.AudioLanguageDetectionResponse:

        # 如果token或call_token在黑名单中，则抛出异常
        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f'{self._endpoint}{request.api}'

        headers = {
            'token': self._token,
            'call_token': self._call_token,
        }

        file_url = request.audio
        metadata = request.metadata
        choices = request.choices
        files = {'audio': (file_url, open(file_url, 'rb'))}

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data={'metadata': metadata, 'choices': choices},
            files=files,
        )

        # 如果返回码为503，则将token和call_token加入黑名单
        if (
            response.json().get('code', None) == 503
            and response.json().get('message', None) == '非法token'
        ):
            self._blacklist_token.append(self._token)
            self._blacklist_call_token.append(self._call_token)
            raise ValueError('token or call_token is invalid')

        base_resp = ai_cloud_sdk_4pd_models.BaseResponse(
            code=response.json().get('code', None),
            data=response.json().get('data', None),
            message=response.json().get('message', None),
        )
        return ai_cloud_sdk_4pd_models.AudioLanguageDetectionResponse(
            response=base_resp
        )

    def asr(
        self,
        request: ai_cloud_sdk_4pd_models.ASRRequest = None,
        on_ready: callable = None,
        on_response: callable = None,
        on_completed: callable = None,
    ) -> None:

        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f"{self._endpoint}{request.api}"
        headers = {
            'token': self._token,
            'call_token': self._call_token,
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
        }

        file_url = request.audio_url
        try:
            with open(file_url, 'rb') as f:
                audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data)
                audio_base64 = audio_base64.decode('utf-8')
        except FileNotFoundError:
            raise ValueError('File not found. Please check the path and try again.')

        # 发送音频数据
        message = {
            "enableWords": True,
            "lang": request.language,
            "fileBase64": audio_base64,
            "finalResult": 'true' if request.final_result else 'false',
        }

        message = json.dumps(message)

        try:
            session = requests.Session()
            with session.post(
                full_url,
                data=message,
                headers=headers,
                stream=True,
                timeout=600,
            ) as response:
                if response.status_code == 200:
                    logging.info('HTTP STREAM connection established')

                if (
                    response.status_code == 503
                    and response.json().get('message') == '非法token'
                ):
                    self._blacklist_token.append(self._token)
                    self._blacklist_call_token.append(self._call_token)
                    raise ValueError('token or call_token is invalid')

                for chunk in response.iter_lines():
                    if chunk:
                        chunk_str = chunk.decode('utf-8')
                        chunk_json = chunk_str.split(":", 1)[1]
                        resp = json.loads(chunk_json)
                        if 'success' in resp and bool(resp['success']):
                            on_ready()
                            continue

                        if 'end' in resp and bool(resp['end']):
                            on_completed()
                            break

                        if request.final_result is False:
                            on_response(resp)
                            continue

                        if (
                            'asr_results' in resp
                            and 'final_result' in resp['asr_results']
                            and bool(resp['asr_results']['final_result'])
                        ):
                            on_response(resp)
                            continue
        except Exception as e:
            print(e)
            print(datetime.datetime.now())

    def translate_text(
        self,
        request: ai_cloud_sdk_4pd_models.TranslateTextRequest = None,
    ) -> ai_cloud_sdk_4pd_models.TranslateTextResponse:

        # 如果token或call_token在黑名单中，则抛出异常
        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f'{self._endpoint}{request.api}'
        headers = {
            'token': self._token,
            'call_token': self._call_token,
            'content-type': request.content_type,
        }

        payload = {'text': request.text}

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data=json.dumps(payload),
        )

        # 如果返回码为503，则将token和call_token加入黑名单
        if (
            response.json().get('code', None) == 503
            and response.json().get('message', None) == '非法token'
        ):
            self._blacklist_token.append(self._token)
            self._blacklist_call_token.append(self._call_token)
            raise ValueError('token or call_token is invalid')

        base_resp = ai_cloud_sdk_4pd_models.BaseResponse(
            code=response.json().get('code', None),
            data=response.json().get('data', None),
            message=response.json().get('message', None),
        )
        return ai_cloud_sdk_4pd_models.TranslateTextResponse(response=base_resp)

    def tts(
        self,
        request: ai_cloud_sdk_4pd_models.TTSRequest = None,
    ):

        # 如果token或call_token在黑名单中，则抛出异常
        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f'{self._endpoint}{request.api}'
        headers = {
            'token': self._token,
            'call_token': self._call_token,
            'content-type': request.content_type,
        }

        payload = {
            'transcription': str(request.transcription),
            'voiceName': request.voice_name,
            'language': request.language,
        }

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data=json.dumps(payload),
        )

        return response

    def create_asr_task(self, request: ai_cloud_sdk_4pd_models.ASRTaskCreateRequest):

        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f'{self._endpoint}{request.api}'
        headers = {
            'token': self._token,
            'call_token': self._call_token,
        }

        files = {'file': (request.audio_url, open(request.audio_url, 'rb'))}

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data={'language': request.language},
            files=files,
        )

        if (
            response.json().get('code', None) == 503
            and response.json().get('message', None) == '非法token'
        ):
            self._blacklist_token.append(self._token)
            self._blacklist_call_token.append(self._call_token)
            raise ValueError('token or call_token is invalid')

        base_resp = ai_cloud_sdk_4pd_models.BaseResponse(
            code=response.json().get('code', None),
            data=response.json().get('data', None),
            message=response.json().get('message', None),
        )

        return ai_cloud_sdk_4pd_models.ASRTaskCreateResponse(response=base_resp)

    def get_asr_task_status(
        self, request: ai_cloud_sdk_4pd_models.ASRTaskStatusRequest
    ):

        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f'{self._endpoint}{request.api}?taskId={request.task_id}'
        headers = {
            'token': self._token,
            'call_token': self._call_token,
            'content-type': request.content_type,
        }

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
        )

        if (
            response.json().get('code', None) == 503
            and response.json().get('message', None) == '非法token'
        ):
            self._blacklist_token.append(self._token)
            self._blacklist_call_token.append(self._call_token)
            raise ValueError('token or call_token is invalid')

        base_resp = ai_cloud_sdk_4pd_models.BaseResponse(
            code=response.json().get('code', None),
            data=response.json().get('data', None),
            message=response.json().get('message', None),
        )

        return ai_cloud_sdk_4pd_models.ASRTaskStatusResponse(response=base_resp)

    def cancel_asr_task(self, request: ai_cloud_sdk_4pd_models.ASRTaskCancelRequest):

        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f'{self._endpoint}{request.api}'
        headers = {
            'token': self._token,
            'call_token': self._call_token,
            'content-type': request.content_type,
        }

        payload = {
            'task_id': request.task_id,
        }

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data=json.dumps(payload),
        )

        if (
            response.json().get('code', None) == 503
            and response.json().get('message', None) == '非法token'
        ):
            self._blacklist_token.append(self._token)
            self._blacklist_call_token.append(self._call_token)
            raise ValueError('token or call_token is invalid')

        base_resp = ai_cloud_sdk_4pd_models.BaseResponse(
            code=response.json().get('code', None),
            data=response.json().get('data', None),
            message=response.json().get('message', None),
        )

        return ai_cloud_sdk_4pd_models.ASRTaskCancelResponse(response=base_resp)
