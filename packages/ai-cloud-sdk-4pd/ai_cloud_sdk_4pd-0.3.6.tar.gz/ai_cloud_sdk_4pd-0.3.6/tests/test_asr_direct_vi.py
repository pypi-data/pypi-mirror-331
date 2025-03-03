response_map = {}


def on_ready():
    print('ready')


def on_response(response):
    global response_map


def on_completed():
    print('completed')


# def test_asr():
#     print('-------------test asr-------------')
#     token = 'eyJhbGciOiJIUzI1NiJ9.eyJ0ZW5hbnRfaWQiOjEsInRva2VuX2NyZWF0ZWRfYXQiOjE3MzI3NjUxMTMwNjYsImlhdCI6MTczMjc2NTExM30.tboPQVyJoKuPAbZVIOPJxI9wbr5TD5Mtck-8P59Fs2I'
#     call_token = 'eyJhbGciOiJIUzI1NiJ9.eyJ0ZW5hbnRfaWQiOjEsInVzZXJfaWQiOjYsInRva2VuX2NyZWF0ZWRfYXQiOjE3MzMxOTY5Mzg0NTUsImlhdCI6MTczMzE5NjkzOH0.xPt2491jDWZQYCS3TpTSko3ln6xTApqg12m_T-P4FDk'
#     region = 'China'
#     config = ai_cloud_sdk_4pd_models.Config(
#         token=token,
#         call_token=call_token,
#         region=region,
#     )
#     client = ai_cloud_sdk_4pd_client.Client(config=config)
#     # request = ai_cloud_sdk_4pd_models.ASRRequest(
#     #     audio_url='/Users/4paradigm/Desktop/ja.wav',
#     #     language='zh',
#     # )
#     #
#     # await client.asr(
#     #     request=request,
#     #     on_ready=on_ready,
#     #     on_response=on_response,
#     #     on_completed=on_completed,
#     # )
#
#     request = ai_cloud_sdk_4pd_models.ASRRequest(
#         audio_url='/Users/4paradigm/Desktop/output_020.wav',
#         language='vi',
#         final_result=True,
#         timeout=60,
#     )
#     client.asr(
#         request=request,
#         on_ready=on_ready,
#         on_response=on_response,
#         on_completed=on_completed,
#     )
#     print('---------------------------------')
