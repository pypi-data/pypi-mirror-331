import datetime

import ai_cloud_sdk_4pd.client as ai_cloud_sdk_4pd_client
import ai_cloud_sdk_4pd.models as ai_cloud_sdk_4pd_models

count1 = 0


def on_ready1():
    print('1 ready')
    print(datetime.datetime.now())


def on_response1(response):
    global count1
    print('---------------1----------------------')
    print(datetime.datetime.now())
    print(count1)
    count1 += 1
    print(response)
    print('-----------------1--------------------')


def on_completed1():
    print('1 completed')
    print(datetime.datetime.now())


def test_asr():
    print('-------------test asr-------------')
    token = 'eyJhbGciOiJIUzI1NiJ9.eyJ0ZW5hbnRfaWQiOjEsInRva2VuX2NyZWF0ZWRfYXQiOjE3MzI3NjUxMTMwNjYsImlhdCI6MTczMjc2NTExM30.tboPQVyJoKuPAbZVIOPJxI9wbr5TD5Mtck-8P59Fs2I'
    call_token = 'eyJhbGciOiJIUzI1NiJ9.eyJ0ZW5hbnRfaWQiOjEsInVzZXJfaWQiOjYsInRva2VuX2NyZWF0ZWRfYXQiOjE3MzMxOTY5Mzg0NTUsImlhdCI6MTczMzE5NjkzOH0.xPt2491jDWZQYCS3TpTSko3ln6xTApqg12m_T-P4FDk'
    region = 'China'
    config = ai_cloud_sdk_4pd_models.Config(
        token=token,
        call_token=call_token,
        region=region,
    )
    client = ai_cloud_sdk_4pd_client.Client(config=config)

    request1 = ai_cloud_sdk_4pd_models.ASRRequest(
        audio_url='/Users/4paradigm/Desktop/output_vi_000.wav',
        language='vi',
        final_result=True,
        timeout=60,
    )

    client.asr(
        request=request1,
        on_ready=on_ready1,
        on_response=on_response1,
        on_completed=on_completed1,
    )


if __name__ == '__main__':
    test_asr()
