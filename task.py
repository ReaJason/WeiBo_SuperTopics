from api import WeiBo


def run():
    # cookie = input()
    # s = input()
    # pick = input()
    # sckey = input()
    cookie = "SUB=_2A25yVn6SDeRhGeNL6VoY-S3FzTuIHXVRuQLarDV6PUJbktANLVXRkW1NSQ6IkGQkKcgtYSurxDi7o8n8V3Br6Jx2; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5gNbWkaYeKefh9X8j0feB-5NHD95QfSKzR1K.01KqNWs4Dqcjz-JHyCJ80dcRt; SUHB=0u5RIApk3b7HhI; _T_WM=64253077786; XSRF-TOKEN=0be317; WEIBOCN_FROM=1110006030; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D20000174%26uicode%3D20000174%26fid%3D2304135528993967_-_WEIBO_SECOND_PROFILE_WEIBO"
    s = "22222222"
    pick = "喻言"
    sckey = "SCU90543Ta7d070aba5fa5f6976b8f05dd98b32085e7615bc0f542"
    wei = WeiBo(cookie)
    wei.daily_task(s, pick, sckey)


if __name__ == '__main__':
    run()
