class Config:
    """
    Model for initing client
    """

    def __init__(
        self,
        token: str = None,
        call_token: str = None,
        endpoint: str = None,
        region: str = None,
    ):
        self.token = token
        self.call_token = call_token
        self.endpoint = endpoint
        self.region = region


class BaseRequest:
    """
    Model for BaseRequest
    """

    def __init__(self):
        self.api = None
        self.method = None
        self.content_type = None
        self.payload = None
        self.is_file = False


class BaseResponse:
    """
    Model for BaseResponse
    """

    def __init__(
        self, code: int = None, data: dict = None, message: str = None, **kwargs
    ):
        self.code = code
        self.data = data
        self.message = message


class TestRequest(BaseRequest):

    def __init__(self):
        super().__init__()
        self.api = '/ai/cpp/api/v1/audio-language-detection/test'
        self.method = 'POST'
        self.content_type = 'application/json'
        self.payload = {}


class TestResponse(BaseResponse):

    def __init__(self, response: BaseResponse = None, **kwargs):
        super().__init__(
            code=response.code if response else None,
            data=response.data if response else None,
            message=response.message if response else None,
            **kwargs,
        )


class AudioLanguageDetectionRequest(BaseRequest):
    """
    Model for AudioLanguageDetectionRequest

    语种识别服务提供全球137种语言的语种识别，帮助您快速判断音频所属语言。结合机器翻译服务，可通过自动的语种识别，快速定位需要翻译的内容，有效提升整体效率。
    """

    def __init__(self, audio: str = None, metadata: str = None, choices: list = None):
        """
        Args:
            audio: 音频文件的本地路径，长度需在5s以内，支持WAV、PCM
            metadata: 音频文件的额外元数据，如音频采样率
        """

        self.audio = audio
        self.metadata = metadata
        self.choices = choices

        super().__init__()
        self.api = '/ai/cpp/api/v1/audio-language-detection'
        self.method = 'POST'
        self.content_type = 'multipart/form-data'


class AudioLanguageDetectionResponse(BaseResponse):
    """
    Model for AudioLanguageDetectionResponse
    """

    def __init__(self, response: BaseResponse = None, **kwargs):
        super().__init__(
            code=response.code if response else None,
            data=response.data if response else None,
            message=response.message if response else None,
            **kwargs,
        )


class TranslateTextRequest(BaseRequest):
    """
    Model for TranslateTextRequest

    文本翻译服务提供全球137种语言的文本翻译，支持多种语言间的互译，帮助您快速实现多语言间的文本翻译。
    """

    def __init__(self, text: list = None, source: str = None, target: str = None):
        """
        Args:
            text: list[str] 待翻译的文本
            source: 源语言
            target: 目标语言
        """

        self.text = text
        self.source = source
        self.target = target

        super().__init__()
        self.api = f'/ai/cpp/api/v1/translate/{source}/{target}'
        self.method = 'POST'
        self.content_type = 'application/json'


class TranslateTextResponse(BaseResponse):
    """
    Model for TranslateTextResponse
    """

    def __init__(self, response: BaseResponse = None, **kwargs):
        super().__init__(
            code=response.code if response else None,
            data=response.data if response else None,
            message=response.message if response else None,
            **kwargs,
        )


class ASRRequest(BaseRequest):
    """
    Model for ASRRequest

    语音识别提供高准确率、低时延的语音转文字服务，包含实时语音识别、一句话识别和录音文件识别等多款产品。适用于智能客服、质检、会议纪要、实时字幕等多个企业应用场景。
    """

    def __init__(
        self,
        language: str = None,
        audio_url: str = None,
        batch_directory: str = None,
        final_result: bool = True,
        timeout: int = 10,
    ):
        """
        Args:
            language: 语种
            audio_url: 音频文件地址
            batch_directory: 批量音频文件目录
            final_result: 是否返回最终结果
            timeout: 超时时间
        """

        self.language = language
        self.audio_url = audio_url
        self.batch_directory = batch_directory
        self.final_result = final_result
        self.timeout = timeout

        super().__init__()
        self.api = f'/ai/cpp/api/v1/asr/stream'
        self.method = 'POST'
        self.content_type = 'application/json'
        # self.payload = {'audio_url': self.audio_url}


class ASRResponse(BaseResponse):
    """
    Model for ASRResponse
    """

    def __init__(self, response: BaseResponse = None, **kwargs):
        super().__init__(
            code=response.code if response else None,
            data=response.data if response else None,
            message=response.message if response else None,
            **kwargs,
        )


class TTSRequest(BaseRequest):
    """
    Model for TTSRequest

    语音合成服务提供多种音色、多种音频格式的语音合成服务，支持多种语言的语音合成，帮助您快速实现多语言的语音合成。
    """

    def __init__(
        self, transcription: str = None, voice_name: str = None, language: str = None
    ):
        """
        Args:
            transcription: str 待合成的文本
            voice_name: str 音色
            language: str 语种
        """

        self.transcription = transcription
        self.voice_name = voice_name
        self.language = language

        super().__init__()
        self.api = f'/ai/cpp/api/v1/tts'
        self.method = 'POST'
        self.content_type = 'application/json'


class TTSResponse(BaseResponse):
    """
    Model for TTSResponse
    """

    def __init__(self, response: BaseResponse = None, **kwargs):
        super().__init__(
            code=response.code if response else None,
            data=response.data if response else None,
            message=response.message if response else None,
            **kwargs,
        )


class ASRTaskCreateRequest(BaseRequest):
    """
    Model for ASRTaskRequest

    语音识别提供高准确率、低时延的语音转文字服务，包含实时语音识别、一句话识别和录音文件识别等多款产品。适用于智能客服、质检、会议纪要、实时字幕等多个企业应用场景。
    """

    def __init__(
        self,
        language: str = None,
        audio_url: str = None,
    ):
        """
        Args:
            language: 语种
            audio_url: 音频文件地址
        """

        self.language = language
        self.audio_url = audio_url

        super().__init__()
        self.api = f'/ai/cpp/api/v1/asr/task'
        self.method = 'POST'
        self.content_type = 'multipart/form-data'


class ASRTaskCreateResponse(BaseResponse):
    """
    Model for ASRResponse
    """

    def __init__(self, response: BaseResponse = None, **kwargs):
        super().__init__(
            code=response.code if response else None,
            data=response.data if response else None,
            message=response.message if response else None,
            **kwargs,
        )


class ASRTaskStatusRequest(BaseRequest):
    """
    Model for ASRTaskStatusRequest

    语音识别提供高准确率、低时延的语音转文字服务，包含实时语音识别、一句话识别和录音文件识别等多款产品。适用于智能客服、质检、会议纪要、实时字幕等多个企业应用场景。
    """

    def __init__(
        self,
        task_id: str = None,
    ):
        """
        Args:
            task_id: 任务id
        """

        self.task_id = task_id

        super().__init__()
        self.api = f'/ai/cpp/api/v1/asr/task/query/status'
        self.method = 'GET'
        self.content_type = 'application/json'


class ASRTaskStatusResponse(BaseResponse):
    """
    Model for ASRResponse
    """

    def __init__(self, response: BaseResponse = None, **kwargs):
        super().__init__(
            code=response.code if response else None,
            data=response.data if response else None,
            message=response.message if response else None,
            **kwargs,
        )


class ASRTaskCancelRequest(BaseRequest):
    """
    Model for ASRTaskCancelRequest

    语音识别提供高准确率、低时延的语音转文字服务，包含实时语音识别、一句话识别和录音文件识别等多款产品。适用于智能客服、质检、会议纪要、实时字幕等多个企业应用场景。
    """

    def __init__(
        self,
        task_id: int = None,
    ):
        """
        Args:
            task_id: 任务id
        """

        self.task_id = task_id

        super().__init__()
        self.api = f'/ai/cpp/api/v1/asr/stream/{task_id}'
        self.method = 'DELETE'
        self.content_type = 'application/json'


class ASRTaskCancelResponse(BaseResponse):
    """
    Model for ASRResponse
    """

    def __init__(self, response: BaseResponse = None, **kwargs):
        super().__init__(
            code=response.code if response else None,
            data=response.data if response else None,
            message=response.message if response else None,
            **kwargs,
        )
