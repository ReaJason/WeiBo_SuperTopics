"""
用户微博监控更新
更新则通过qq推送消息

    cookie: 通过https://m.weibo.cn/获取
    skey: 通过https://cp.xuthus.cc/获取
    user_id: 通过进入用户微博主页获取，例如https://m.weibo.cn/u/2992978081，user_id则为2992978081
"""
import time
import schedule

from api import WeiBo

mid = None


def monitor(wei, user_id, sckey):
    blog_dict = wei.get_user_first_blog(user_id)
    global mid
    if blog_dict["story_mid"] == mid:
        print("无更新")
        return None
    else:
        if blog_dict["story_create_at"] in ["刚刚", "1分钟前", "2分钟前"]:
            print("有更新l")
            mid = blog_dict["story_mid"]
            print(mid)
            pic = "\n".join(blog["pic_url"])
            msg = f"""微博有更新啦！！
Mid：{blog_dict["story_mid"]}
User：{blog_dict["story_user"]}
Date：{blog_dict["story_create_at"]}
Text：{blog_dict["story_text"]}
Repost：{blog_dict["story_repost_count"]}
Comment：{blog_dict["story_comment_count"]}
Attitude：{blog_dict["story_attitude_count"]}
Url：{blog_dict["story_url"]}
Pic：{pic}
Video：{blog_dict["video_url"]}"""
            print(msg)
            wei.cool_push(sckey, msg)


def run():
    cookie = "**********"
    skey = "*************"
    user_id = "2992978081"
    wei = WeiBo(cookie)
    blog = wei.get_user_first_blog(user_id)
    print(f"User：{blog['story_user']}：正在微博监控中......")
    pic = "\n".join(blog["pic_url"])
    msg = f"""Mid：{blog["story_mid"]}
    User：{blog["story_user"]}
    Date：{blog["story_create_at"]}
    Text：{blog["story_text"]}
    Repost：{blog["story_repost_count"]}
    Comment：{blog["story_comment_count"]}
    Attitude：{blog["story_attitude_count"]}
    Url：{blog["story_url"]}
    Pic：{pic}
    Video：{blog["video_url"]}"""
    print(msg)
    mid = blog["story_mid"]
    schedule.every().minute.do(monitor, wei, user_id, skey)
    while True:
        time.sleep(1)
        schedule.run_pending()


if __name__ == '__main__':
    run()
