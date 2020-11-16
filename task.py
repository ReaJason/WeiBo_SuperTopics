import logging
from api import WeiBo


def run():
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format="[%(levelname)s]; %(message)s")
    log = []
    cookie = "_T_WM=53241720233; XSRF-TOKEN=646ec4; WEIBOCN_FROM=1110006030; SCF=Anoy4ZLg_wBfQIVCklg20zxHbfR5sUoo4N6F-rF5rBMmBqcpmXe3Nv4rilbBtGlXJSzogwU6cqMKyIY8tq339ws.; SUB=_2A25yttk0DeRhGeNL6VoY-S3FzTuIHXVuWOd8rDV6PUJbktANLRX8kW1NSQ6IkDLOmG8L-Lw1DO4iwlZmlelGQ3yT; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5gNbWkaYeKefh9X8j0feB-5NHD95QfSKzR1K.01KqNWs4Dqcjz-JHyCJ80dcRt; SSOLoginState=1605544292; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D102803%26uicode%3D20000174"
    s = "22222222"
    pick = "喻言"
    sckey = "SCU90543Ta7d070aba5fa5f6976b8f05dd98b32085e7615bc0f542"
    wb = WeiBo(cookie)
    user = wb.get_profile()
    log.append("#### 💫‍User：")
    if not user['status']:
        logging.warning(user['errmsg'])
        return
    logging.info("获取个人信息成功✔")
    topic_list = wb.get_topic_list()
    # log.append("```")
    # log.append(user["user"]["user_msg"])
    # log.append("```")
    # logging.info("开始超话签到")
    # log.append("#### ✨CheckIn：")
    # log.append("```")
    # for topic in topic_list:
    #     check_dict = wb.check_in(s, topic)
    #     if check_dict["status"]:
    #         log.append(check_dict["msg"])
    #         logging.info(check_dict)
    #     else:
    #         log.append(check_dict["errmsg"])
    #         logging.warning(check_dict["errmsg"])
    #         break
    # log.append("```")
    # logging.info("获取每日积分")
    # log.append("#### 🔰DailyScore：")
    # log.append("```")
    # daily_res = wb.get_daily_score()
    # if daily_res['status']:
    #     log.append(daily_res['msg'])
    #     logging.info(daily_res['msg'])
    # else:
    #     log.append(daily_res['msg'])
    #     logging.warning(daily_res['msg'])
    # log.append("```")
    logging.info("超话评论转发（正在执行，需要一点时间......）")
    log.append("#### ✅Post：")
    log.append("```")
    repost = wb.repost_comment(topic_list[-1])
    logging.info(repost)
    log.append(repost)
    log.append("```")
    # logging.info("指定超话打榜")
    # log.append("#### 💓Pick：")
    # log.append("```")
    # picks = [topic for topic in topic_list if topic["topic_title"] == pick]
    # if not picks:
    #     errmsg = f"未关注【{pick}】该超话，请检查超话名字是否正确"
    #     logging.warning(errmsg)
    #     log.append(errmsg)
    #     return
    # pick_res = wb.pick_topic(picks[0], "select66")
    # if pick_res['status']:
    #     log.append(pick_res['result']['msg'])
    #     logging.info(pick_res['result']['msg'])
    # else:
    #     log.append(pick_res['errmsg'])
    #     logging.warning(pick_res['errmsg'])
    # log.append("```")
    # logging.info("查询任务中心")
    # log.append("#### 🌈TaskCenter：")
    # log.append("```")
    # task_dict = wb.task_center()
    # if task_dict['status']:
    #     log.append(task_dict['task_dict']['msg'])
    #     logging.info(task_dict['task_dict']['msg'])
    # else:
    #     log.append(task_dict['task_res.text'])
    #     logging.info(task_dict['task_res.text'])
    # log.append("```")
    # wb.server_push(sckey, "\n".join(log))


if __name__ == '__main__':
    run()
