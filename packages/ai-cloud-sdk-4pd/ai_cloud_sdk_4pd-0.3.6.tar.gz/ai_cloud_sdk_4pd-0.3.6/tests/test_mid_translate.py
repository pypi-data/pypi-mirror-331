import datetime

import ai_cloud_sdk_4pd.client as ai_cloud_sdk_4pd_client
import ai_cloud_sdk_4pd.models as ai_cloud_sdk_4pd_models


def test_translate():
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
    request = ai_cloud_sdk_4pd_models.TranslateTextRequest(
        text=["大家好"],
        source="zh",
        target="tr",
    )
    print(datetime.datetime.now())
    response = client.translate_text(request=request)
    print(datetime.datetime.now())
    assert response.data['transResults'][0] == 'Herkese merhaba'

    request = ai_cloud_sdk_4pd_models.TranslateTextRequest(
        text=["Hello everyone"],
        source="en",
        target="zh",
    )
    response = client.translate_text(request=request)
    assert response.data['transResults'][0] == '大家好'

    request = ai_cloud_sdk_4pd_models.TranslateTextRequest(
        text=["大家好，我是一个学生，你好吗？"],
        source="zh",
        target="fa",
    )
    response = client.translate_text(request=request)
    print(response.data)
    assert (
        response.data['transResults'][0]
        == 'سلام به همه، من دانشجو هستم، حال شما چطور است؟'
    )


if __name__ == '__main__':
    test_translate()
