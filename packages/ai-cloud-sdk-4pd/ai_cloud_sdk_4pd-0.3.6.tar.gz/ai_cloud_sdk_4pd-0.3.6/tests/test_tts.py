import ai_cloud_sdk_4pd.client as ai_cloud_sdk_4pd_client
import ai_cloud_sdk_4pd.models as ai_cloud_sdk_4pd_models


def test_tts():
    print('-------------test client-------------')
    token = 'eyJhbGciOiJIUzI1NiJ9.eyJ0ZW5hbnRfaWQiOjEsInRva2VuX2NyZWF0ZWRfYXQiOjE3MzI3NjUxMTMwNjYsImlhdCI6MTczMjc2NTExM30.tboPQVyJoKuPAbZVIOPJxI9wbr5TD5Mtck-8P59Fs2I'
    call_token = 'eyJhbGciOiJIUzI1NiJ9.eyJ0ZW5hbnRfaWQiOjEsInVzZXJfaWQiOjYsInRva2VuX2NyZWF0ZWRfYXQiOjE3MzMxOTY5Mzg0NTUsImlhdCI6MTczMzE5NjkzOH0.xPt2491jDWZQYCS3TpTSko3ln6xTApqg12m_T-P4FDk'

    region = 'China'
    config = ai_cloud_sdk_4pd_models.Config(
        token=token,
        call_token=call_token,
        region=region,
    )
    client = ai_cloud_sdk_4pd_client.Client(config=config)
    request = ai_cloud_sdk_4pd_models.TTSRequest(
        transcription='你好啊,我是张三',
        language='zh',
        voice_name='zh-f-sweet-2',
    )
    response = client.tts(request=request)
    # save the response to a file
    with open('tts.wav', 'wb') as f:
        f.write(response.content)


if __name__ == '__main__':
    test_tts()
