import datetime
import time

import ai_cloud_sdk_4pd.client as ai_cloud_sdk_4pd_client
import ai_cloud_sdk_4pd.models as ai_cloud_sdk_4pd_models

count1 = 0


def on_ready1():
    print('1 ready')
    print(datetime.datetime.now())


file1 = '/Users/4paradigm/Desktop/vvv000.txt'


def on_response1(response):
    global count1
    print('---------------1----------------------')
    print(datetime.datetime.now())
    print(count1)
    count1 += 1
    # write to file
    with open(file1, 'a') as f:
        res_str = str(response)
        f.write(res_str + '\n')
    print('-----------------1--------------------')


def on_completed1():
    print('1 completed')
    print(datetime.datetime.now())


def on_ready2():
    print('2 ready')
    print(datetime.datetime.now())


count2 = 0
file2 = '/Users/4paradigm/Desktop/vvv014.txt'


def on_response2(response):
    global count2
    print('---------------2----------------------')
    print(datetime.datetime.now())
    print(count2)
    count2 += 1
    # write to file
    with open(file2, 'a') as f:
        # convert dict to str
        res_str = str(response)
        f.write(res_str + '\n')
    print('-----------------2--------------------')


def on_completed2():
    print('2 completed')
    print(datetime.datetime.now())


def on_ready3():
    print('3 ready')
    print(datetime.datetime.now())


count3 = 0
file3 = '/Users/4paradigm/Desktop/vvv001.txt'


def on_response3(response):
    global count3
    print('---------------3----------------------')
    print(datetime.datetime.now())
    print(count3)
    count3 += 1
    # write to file
    with open(file3, 'a') as f:
        # convert dict to str
        res_str = str(response)
        f.write(res_str + '\n')
    print('-----------------3--------------------')


def on_completed3():
    print('3 completed')
    print(datetime.datetime.now())


def on_ready4():
    print('4 ready')
    print(datetime.datetime.now())


count4 = 0
file4 = '/Users/4paradigm/Desktop/vvv020.txt'


def on_response4(response):
    global count4
    print('---------------4----------------------')
    print(datetime.datetime.now())
    print(count4)
    count4 += 1
    # write to file
    with open(file4, 'a') as f:
        # convert dict to str
        res_str = str(response)
        f.write(res_str + '\n')
    print('-----------------4--------------------')


def on_completed4():
    print('4 completed')
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
    #
    requset2 = ai_cloud_sdk_4pd_models.ASRRequest(
        audio_url='/Users/4paradigm/Desktop/output_vi_014.wav',
        language='vi',
        final_result=True,
        timeout=60,
    )
    request3 = ai_cloud_sdk_4pd_models.ASRRequest(
        audio_url='/Users/4paradigm/Desktop/output_vi_001.wav',
        language='vi',
        final_result=True,
        timeout=60,
    )
    request4 = ai_cloud_sdk_4pd_models.ASRRequest(
        audio_url='/Users/4paradigm/Desktop/output_vi_020.wav',
        language='vi',
        final_result=True,
        timeout=60,
    )

    client.asr(request1, on_ready1, on_response1, on_completed1)
    time.sleep(10)
    client.asr(requset2, on_ready2, on_response2, on_completed2)
    time.sleep(10)
    client.asr(request3, on_ready3, on_response3, on_completed3)
    time.sleep(10)
    client.asr(request4, on_ready4, on_response4, on_completed4)
    time.sleep(10)

    # t1 = threading.Thread(
    #     target=client.asr, args=(request1, on_ready1, on_response1, on_completed1)
    # )
    # t2 = threading.Thread(
    #     target=client.asr, args=(requset2, on_ready2, on_response2, on_completed2)
    # )
    # t3 = threading.Thread(
    #     target=client.asr, args=(request3, on_ready3, on_response3, on_completed3)
    # )
    # t4 = threading.Thread(
    #     target=client.asr, args=(request4, on_ready4, on_response4, on_completed4)
    # )
    #
    # t1.start()
    # t2.start()
    # t3.start()
    # t4.start()
    # t1.join()
    # t2.join()
    # t3.join()
    # t4.join()

    # client.asr(
    #     request=requset2,
    #     on_ready=on_ready2,
    #     on_response=on_response2,
    #     on_completed=on_completed2,
    # )
    #
    # client.asr(
    #     request=requset2,
    #     on_ready=on_ready1,
    #     on_response=on_response1,
    #     on_completed=on_completed1,
    # )
    # print('---------------------------------')


if __name__ == '__main__':
    test_asr()
