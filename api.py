import time
import datetime
import hashlib
import random
import re

import requests


class WeiBo:

    def __init__(self, cookie):
        self.index_url = "https://m.weibo.cn/"
        self.profile_url = "https://m.weibo.cn/profile/info"
        self.config_url = "https://m.weibo.cn/api/config"
        self.get_index_url = "https://m.weibo.cn/api/container/getIndex"
        self.check_url = "https://api.weibo.cn/2/page/button"
        self.web_check_url = "https://weibo.com/p/aj/general/button"
        self.day_score_url = "https://huati.weibo.cn/aj/super/receivescore"
        self.active_score_url = "https://chaohua.weibo.cn/remind/active"
        self.get_super_score_url = "https://huati.weibo.cn/aj/super/getscore"
        self.task_center_url = "https://huati.weibo.cn/aj/super/taskcenter"
        self.pick_url = "https://huati.weibo.cn/aj/super/picktop"
        self.detail_story_url = "https://m.weibo.cn/statuses/show"
        self.story_comment_url = "https://m.weibo.cn/comments/hotflow"
        self.parse_comment_url = "https://m.weibo.cn/comments/hotFlowChild"
        self.repost_story_url = "https://m.weibo.cn/api/statuses/repost"
        self.comment_story_url = "https://m.weibo.cn/api/comments/create"
        self.star_story_url = "https://m.weibo.cn/api/attitudes/create"
        self.delete_story_url = "https://m.weibo.cn/profile/delMyblog"
        self.delete_comment_url = "https://m.weibo.cn/comments/destroy"
        self.delete_star_url = "https://m.weibo.cn/api/attitudes/destroy"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/83.0.4103.116 Mobile Safari/537.36 ",
            "cookie": cookie
        }
        self.nickname = None
        self.gsid = re.findall("SUB=(.*?);", cookie)[0] if re.findall("SUB=(.*?);", cookie) else None

    def get_profile(self):
        """
        获取个人信息
        :return:
        """
        profile_res = requests.get(self.profile_url, headers=self.headers)
        content_type = profile_res.headers["Content-Type"]
        if content_type == "application/json; charset=utf-8":
            user = profile_res.json()["data"]["user"]
            user_dict = {
                "user_id": user["id"],
                "user_name": user["screen_name"],
                "user_description": user["description"],
                "user_avatar": user["avatar_hd"],
                "background_img": user["cover_image_phone"],
                "user_gender": "fmale" if user["gender"] == "f" else "male",
                "statuses_count": user["statuses_count"],
                "follow_count": user["follow_count"],
                "followers_count": user["followers_count"],
                "profile_url": user["profile_url"],
                "story_container_id": profile_res.json()["data"]["more"].split("/")[-1],
                "user_msg": f"""ID: {user["id"]}
用户名: {user["screen_name"]}
简介: {user["description"] if user["description"] else "这个人很懒，什么也没有"}
微博数: {user["statuses_count"]}
关注数: {user["follow_count"]}
粉丝数: {user["followers_count"]}"""
            }
            self.nickname = user["screen_name"]
            print(f"User：{self.nickname}")
            return self.req_res(
                status=1,
                res_name="user",
                res=user_dict
            )
        else:
            errmsg = "获取个人信息失败，请设置Cookie后重试"
            return self.req_res(
                status=0,
                errmsg=errmsg
            )

    def get_topic_list(self):
        """
        获取超话关注列表
        :return:
        """
        topic_list = []
        since_id = ""
        while True:
            topic_params = {
                "containerid": "100803_-_followsuper",
                "since_id": since_id
            }
            topic_res = requests.get(
                url=self.get_index_url,
                params=topic_params,
                headers=self.headers
            )
            # print(topic_res.json())
            topic_json = topic_res.json()["data"]["cards"][0]["card_group"]
            for topic in topic_json:
                if topic["card_type"] == "8":
                    topic_dict = {
                        "topic_title": topic["title_sub"],
                        "topic_cover": topic["pic"].replace("thumbnail", "large"),
                        "topic_level": re.findall(r"\d+", topic["desc1"])[0],
                        "topic_status": topic["buttons"][0]["name"],
                        "topic_url": topic["scheme"],
                        "topic_id": re.findall('[0-9a-z]{38}', topic["scheme"])[0],
                        "topic_desc": topic["desc2"]
                    }
                    if topic_dict["topic_status"] != "关注":
                        # msg = '标题：{}，等级：{}级，签到状态：{}'.format(ch_dict["title"], ch_dict["level"], ch_dict["status"])
                        # print(msg)
                        topic_list.append(topic_dict)
            since_id = topic_res.json()["data"]["cardlistInfo"]["since_id"]
            if since_id == "":
                topic_list.sort(key=lambda x: int(x["topic_level"]), reverse=True)
                if topic_list:
                    return topic_list
                else:
                    self.get_topic_list()

    def get_story_list(self, topic_url):
        """
        获取超话微博（第一页）获取多页设置最后if count == 1:中的 1 即可
        :param topic_url: 超话url
        :return:
        """
        count = 0
        since_id = ""
        stories_list = []
        while True:
            index_url = f"https://m.weibo.cn/api/container/getIndex?{topic_url.split('?')[-1]}&since_id={since_id}"
            index_res = requests.get(index_url, headers=self.headers)
            cards = index_res.json()["data"]["cards"]
            scheme_list = []
            for card_group in cards:
                if card_group["itemid"] == "":
                    for card in card_group["card_group"]:
                        if card["card_type"] == "9":
                            scheme_list.append(card["scheme"])
            for scheme in scheme_list:
                story_res = self.parse_story_body(re.findall('[0-9a-zA-Z]{9}', scheme)[0])
                if story_res["status"] == 1:
                    stories_list.append(story_res["story_info"])
            since_id = index_res.json()["data"]["pageInfo"]["since_id"]
            count = count + 1
            if count == 1:
                return stories_list

    def check_in(self, s, topic_dict):
        """
        微博国际版APP签到接口
        :param s: 通过抓取微博国际版签到请求获取
        :param topic_dict: 超话信息字典,具体格式请看get_topic_list函数中
        :return:
        """
        check_data = {
            "c": "weicoabroad",
            "s": s,
            "wm": "2468_1001",
            "gsid": self.gsid,
            "from": "1299295010",
            "source": "4215535043",
            "lang": "zh_CN",
            'ua': "Redmi+K20+Pro+Premium+Edition_10_WeiboIntlAndroid_3610",
            "request_url":
                f"http%3A%2F%2Fi.huati.weibo.com%2Fmobile%2Fsuper%2Factive_checkin%3Fpageid%3D{topic_dict['topic_id']}",
        }
        if topic_dict["topic_status"] == "签到":
            time.sleep(random.randint(2, 4))
            check_res = requests.get(
                url=self.check_url,
                params=check_data,
            )
            if check_res.json().get('errmsg'):
                errmsg = '{check_res.json()["errmsg"]}/s参数设置有误'
                return self.req_res(status=0, errmsg=errmsg)
            if check_res.json()["result"] == 1:
                success_msg = check_res.json()["msg"].replace("\n", "/")
                msg = f'TopicName：{topic_dict["topic_title"]}\nLevel：{topic_dict["topic_level"]}\nMessage：{success_msg}\n'
                return self.req_res(status=1, res_name="msg", res=msg)
            elif check_res.json()["result"] == 388000:
                errmsg = "💢签到异常需要身份验证，暂未找到合适的解决办法"
                return self.req_res(status=0, errmsg=errmsg)
        else:
            msg = f'TopicName：{topic_dict["topic_title"]}\nLevel：{topic_dict["topic_level"]}\nMessage：今日已签到\n'
            return self.req_res(status=1, res_name="msg", res=msg)

    def get_day_score(self):
        """
         超话每日积分领取
        :return:
        """
        day_score_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://huati.weibo.cn'
        }
        day_score_headers.update(self.headers)
        score_data = {
            'type': 'REQUEST',
            'user_score': 999
        }
        day_score_res = requests.post(
            url=self.day_score_url,
            headers=day_score_headers,
            data=score_data
        )
        if day_score_res.json()["code"] == 100000:
            msg = f'今日签到积分获取：{day_score_res.json()["data"]["add_score"]}分'
            return msg
        elif day_score_res.json()["code"] == 386011:
            msg = f'{day_score_res.json()["msg"]}'
            return msg
        elif day_score_res.json()["code"] == 100002:
            msg = f'{day_score_res.json()["msg"]}'
            return msg

    def get_active_score(self):
        """
        微博超话APP登录积分接口
        :return:
        """
        parmas = {'from': '21A7395010', 'ti': str(int(time.time() * 1000))}
        KEY = 'SloRtZ4^OfpVi!#3u!!hmnCYzh*fxN62Nyy*023Z'
        str1 = ''
        for i in parmas:
            str1 += i + ':' + parmas[i] + ','
        str1 = str1 + self.gsid + KEY
        m = hashlib.md5()
        m.update(str1.encode())
        str1 = m.hexdigest()
        st = ''
        for i in range(0, len(str1), 2):
            st += str1[i]
        get_active_score_headers = {'gsid': self.gsid, 'st': st}
        active_res = requests.get(
            self.active_score_url,
            params=parmas,
            headers=get_active_score_headers
        )
        # print(active_res.json())
        if active_res.json()['code'] == 100000:
            if "388000" in active_res.json()['toast']:
                return "微博超话登录积分获取接口验证IP地址是否登录过\n" \
                       "因登录接口需要验证,GitHub Actions上暂无法实现\n" \
                       "如有需求,请Clone到本地再进行操作"
            else:
                msg = f"{[active_res.json()['toast'] if active_res.json()['toast'] else '今日已经登录过了'][0]}"
                return msg

    def get_score_bang(self, topic):
        """
        超话打榜
        :param topic:
        :param topic: 超话信息字典,具体格式请看get_topic_list函数中
        :return:
        """
        if topic:
            topic_dict = topic[0]
            referer_url = f"https://huati.weibo.cn/aj/super/getscore?" \
                          f"page_id={topic_dict['topic_id']}&aid=&from=1110006030"
            get_score_headers = {
                "Referer": referer_url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/84.0.4147.105 Safari/537.36",
                "cookie": self.headers.get("cookie"),
                "X-Requested-With": "XMLHttpRequest"
            }
            score_res = requests.get(referer_url, headers=get_score_headers)
            topic_name = score_res.json()["data"]["topic_name"]
            score = score_res.json()["data"]["score"]
            rank = score_res.json()["data"]["rank"]
            # print(score_res.json())
            if score_res.json()["data"]["user_total_score"] > 100:
                while True:
                    pick_data = {
                        "topic_name": topic_dict["topic_title"],
                        "page_id": topic_dict["topic_id"],
                        "score": "66",
                        "is_pub": "0",
                        "cur_rank": score_res.json()["data"]["rank"],
                        "ctg_id": score_res.json()["data"]["ctg_id"],
                        "topic_score": score_res.json()["data"]["score"],
                        "index": "select66",
                        "user_score": score_res.json()["data"]["user_total_score"],
                        "aid": "",
                        "device": '{"timezone":"Asia/Shanghai","lang":"zh","plat":"Win32","ua":"Mozilla/5.0 (Windows '
                                  'NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/84.0.4147.105 '
                                  'Safari/537.36","screen":"864*1536","aid":"","from":"1110006030"}',
                        "param": score_res.json()["data"]["encryption_param"]
                    }
                    pick_res = requests.post(self.pick_url, headers=get_score_headers, data=pick_data)
                    # print(pick_res.json())
                    if pick_res.json()["code"] == 402001:
                        time.sleep(random.randint(5, 8))
                        continue
                    elif pick_res.json()["code"] == 302001:
                        return pick_res.json()["msg"]
                    elif pick_res.json()["code"] == 382023:
                        return pick_res.json()["msg"]
                    else:
                        msg = f"TopicName：{topic_name}\n" \
                              f"Rank：{rank}/{score}分\n" \
                              f"Msg：{pick_res.json()['data']['add_int_msg']}"
                        return msg
            else:
                msg = f'TopicName：{topic_name}\n' \
                      f'Rank：{rank}/{score}分\n' \
                      f'Message：积分少于66，暂不打榜'
                return msg
        else:
            msg = "未关注该超话，请确认并重新设置打榜超话名"
            return msg

    def task_center(self):
        """
        积分任务中心
        :return:
        """
        task_headers = {
            "Referer": "https://huati.weibo.cn/super/taskcenter?aid=&from=1110006030",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/84.0.4147.105 Safari/537.36",
            "cookie": self.headers.get("cookie"),
            "X-Requested-With": "XMLHttpRequest"
        }
        task_res = requests.get(self.task_center_url, headers=task_headers)
        if task_res.json()["code"] == 100000:
            task_dict = {
                "total_score": task_res.json()["data"]["total_score"],
                "al_get_score": task_res.json()["data"]["al_get_score"],
                "day_score": task_res.json()["data"]["task_per_day"]["request"],
                "be_comment": task_res.json()["data"]["task_per_day"]["be_comment"],
                "lclient_day": task_res.json()["data"]["task_per_day"]["lclient_day"],
                "topic_check": task_res.json()["data"]["task_per_day"]["checkin"],
                "simple_comment": task_res.json()["data"]["task_per_day"]["simple_comment"],
                "simple_repost": task_res.json()["data"]["task_per_day"]["simple_repost"]
            }
            msg = f"""当前积分总额：{task_dict["total_score"]}分
今日积分获取：{task_dict["al_get_score"]}分
每日访问积分：已获取{task_dict["day_score"]}分/{task_res.json()["data"]["request_desc"]}
超话登录积分：已获取{task_dict["lclient_day"]}分/每日上限10分
超话打卡签到：已签到{task_dict["topic_check"]}次/每日上限8次
超话帖子评论：已获取{task_dict["simple_comment"]}分/每日上限12分
超话帖子转发：已获取{task_dict["simple_repost"]}分/每日上限4分
"""
            return msg

    def yu_yan(self, yu_topic):
        story_list = self.get_story_list(yu_topic["topic_url"])
        contents = "喻言@THE9-喻言"
        repost_count = 0
        comment_count = 0
        star_count = 0
        for story in story_list:
            time.sleep(random.randint(5, 8))
            if story["story_user"] != "喻言官方反黑站":
                st = self.get_st()
                repost_res = self.repost_story(story["story_mid"], st, contents)
                if repost_res["status"]:
                    repost_count += 1
                    time.sleep(random.randint(3, 5))
                comment_res = self.comment_story(story["story_mid"], st, contents)
                if comment_res["status"]:
                    comment_count += 1
                    time.sleep(random.randint(3, 5))
                star_res = self.star_story(story["story_mid"], st)
                if star_res["status"]:
                    star_count += 1
                    time.sleep(random.randint(3, 5))
        msg = f"转发成功：{repost_count}条、评论成功：{comment_count}条、点赞成功：{star_count}条\n"
        return msg

    def repost_comment(self, topic_dict):
        """
        转发、评论、点赞超话第一页帖子并删除转发、删除评论、取消点赞
        :param topic_dict: 超话信息字典,具体格式请看get_topic_list函数中
        :return:
        """
        story_list = self.get_story_list(topic_dict["topic_url"])
        contents = "💦"
        repost_count = 0
        comment_count = 0
        star_count = 0
        delete_repost = 0
        delete_comment = 0
        delete_star = 0
        for story in story_list:
            time.sleep(random.randint(5, 8))
            st = self.get_st()
            repost_res = self.repost_story(story["story_mid"], st, contents)
            if repost_res["status"]:
                repost_count += 1
                time.sleep(random.randint(3, 5))
                if self.delete_story(repost_res["repost_dict"]["l_repost_mid"], st):
                    delete_repost += 1
            comment_res = self.comment_story(story["story_mid"], st, contents)
            if comment_res["status"]:
                comment_count += 1
                time.sleep(random.randint(3, 5))
                if self.delete_comment(comment_res["comment_dict"]["comment_cid"], st):
                    delete_comment += 1
            star_res = self.star_story(story["story_mid"], st)
            if star_res["status"]:
                star_count += 1
                time.sleep(random.randint(3, 5))
                if self.delete_star(star_res["star_dict"]["star_story_mid"], st):
                    delete_star += 1
        msg = f"转发成功：{repost_count}条、评论成功：{comment_count}条、点赞成功：{star_count}条\n" \
              f"删除转发：{delete_repost}条、删除评论：{delete_comment}条、取消点赞：{delete_star}条"
        return msg

    def get_st(self):
        """
        获取st参数,用于转发评论与点赞
        :return: st
        """
        st_response = requests.get(self.config_url, headers=self.headers)
        if st_response.json()["ok"] == 1:
            if str(st_response.json()["data"]["login"]) == "True":
                st = st_response.json()["data"]["st"]
                return st
            else:
                return None
        else:
            return None

    def get_user_first_blog(self, user_id):
        """
        获取用户第一条微博，用来监控微博更新
        :param user_id:
        :return:
        """
        get_id_params = {
            "type": "uid",
            "value": user_id
        }
        get_id_res = requests.get(
            url=self.get_index_url,
            params=get_id_params,
            headers=self.headers
        )
        data = get_id_res.json()["data"]
        container_id = data["tabsInfo"]["tabs"][1]["containerid"]
        blog_params = {
            "type": "uid",
            "value": user_id,
            "containerid": container_id
        }
        blog_res = requests.get(
            url=self.get_index_url,
            params=blog_params,
            headers=self.headers
        )
        cards = blog_res.json()["data"]["cards"]
        for card in cards:
            if card["card_type"] == 9:
                if card["mblog"].get("isTop"):
                    continue
                story_res = self.parse_story_body(card["mblog"]["mid"])
                if story_res["status"]:
                    return story_res["story_info"]

    def parse_story(self, story_id):
        """
        解析微博所有信息（包括微博主体以及评论以及评论的评论）信息采集会受限
        :param story_id: 微博mid
        :return:
        """
        story_body = self.parse_story_body(story_id)
        story_comment = self.parse_story_comment(story_id)
        if story_body["status"]:
            story = {
                "story_body": story_body["story_info"],
                "story_comment": {
                    "total_num": len(story_comment),
                    "comments": story_comment
                }
            }
            return self.req_res(
                status=1,
                res_name="story",
                res=story
            )
        else:
            return story_body

    def parse_story_body(self, story_id):
        """
        解析微博主体信息
        :param story_id: 微博mid
        :return:
        """
        parse_params = {
            "id": story_id
        }
        detail_res = requests.get(self.detail_story_url, params=parse_params, headers=self.headers)
        if detail_res.headers["content-type"] == "application/json; charset=utf-8":
            # print(detail_res.json())
            detail_data = detail_res.json()["data"]
            page_type = detail_data["page_info"]["type"] if detail_data.get("page_info", None) else None
            story_dict = {
                "story_mid": detail_data["id"],
                "story_create_at": detail_data["created_at"],
                "story_user": detail_data["user"]["screen_name"],
                "story_text": re.sub(r'<.*?>', "", detail_data["text"]),
                "story_repost_count": detail_data["reposts_count"],
                "story_comment_count": detail_data["comments_count"],
                "story_attitude_count": detail_data["attitudes_count"],
                "story_url": "https://m.weibo.cn/status/{}".format(detail_data["bid"]),
                "pic_url": [f"https://wx3.sinaimg.cn/large/{pic_id}.jpg" for pic_id in detail_data["pic_ids"]]
                if detail_data["pic_num"] else None,
                # "video_url": [item[1] for item in detail_data["page_info"]["urls"].items()][0]
                # if page_type == "video" else None
            }
            # print(story_dict)
            return self.req_res(
                status=1,
                res_name="story_info",
                res=story_dict
            )
        else:
            errmsg = "未找到该微博或获取信息失败"
            return self.req_res(
                status=0,
                errmsg=errmsg
            )

    def parse_story_comment(self, story_id):
        """
        解析微博评论信息
        :param story_id: 微博mid
        :return:
        """
        story_comment_list = []
        max_id = 0
        while True:
            time.sleep(random.randint(5, 10))
            comment_params = {
                "id": story_id,
                "mid": story_id,
                "max_id": max_id,
                "max_id_type": "0"
            }
            story_comment_headers = {
                "referer": f"https://m.weibo.cn/compose/repost?id={story_id}"
            }
            story_comment_headers.update(self.headers)
            story_comment_res = requests.get(self.story_comment_url, params=comment_params,
                                             headers=story_comment_headers)
            if story_comment_res.json()["ok"]:
                data_list = story_comment_res.json()["data"]["data"]
                max_id = story_comment_res.json()["data"]["max_id"]
                for data in data_list:
                    comment_dict = {
                        "comment_user": data["user"]["screen_name"],
                        "comment_create_at": data["created_at"],
                        "comment_text": re.sub(r'<.*?>', "", data["text"])
                        if re.sub(r'<.*?>', "", data["text"]) else "<icon>",
                        "comment_pic": data["pic"]["large"]["url"] if data.get("pic", None) else None,
                        "comment_like_count": data["like_count"],
                        "comment_reply": self.parse_comment(story_id, data["id"])
                        if data["total_number"] else None

                    }
                    # print(comment_dict)
                    story_comment_list.append(comment_dict)
                if max_id == 0:
                    return story_comment_list
            else:
                return story_comment_list

    def parse_comment(self, mid, cid):
        """
        解析微博评论的评论
        :param mid: 微博mid
        :param cid: 评论cid
        :return:
        """
        comment_list = []
        max_id = 0
        while True:
            time.sleep(random.randint(2, 4))
            comment_params = {
                "cid": cid,
                "max_id": max_id,
                "max_id_type": "0"
            }
            comment_headers = {
                "referer": f"https://m.weibo.cn/detail/{mid}?cid={cid}"
            }
            comment_headers.update(self.headers)
            comment_res = requests.get(self.parse_comment_url, params=comment_params, headers=comment_headers)
            if comment_res.json()["ok"]:
                data_list = comment_res.json()["data"]
                for data in data_list:
                    comment_dict = {
                        "comment_user": data["user"]["screen_name"],
                        "comment_create_at": data["created_at"],
                        "comment_text": data["reply_original_text"]
                        if data.get("reply_original_text", None) else re.sub(r'<.*?>', "", data["text"]),
                        "comment_like_count": data["like_count"],
                        "comment_pic": re.findall('href="(.*?)"', data["text"])[0]
                        if re.findall('href="(.*?)"', data["text"]) else None
                    }
                    # print(comment_dict)
                    comment_list.append(comment_dict)
                if max_id == 0:
                    return comment_list
            else:
                return comment_list

    def repost_story(self, mid, st, content):
        """
         转发微博
        :param mid: 微博mid
        :param st: get_st()获取
        :param content: 评论内容
        :return:
        """
        repost_data = {
            "id": mid,
            "content": content,
            "mid": mid,
            "st": st,
            "_spr": "screen:411x731"
        }
        repost_headers = {
            "referer": f"https://m.weibo.cn/compose/repost?id={mid}"
        }
        repost_headers.update(self.headers)
        repost_res = requests.post(self.repost_story_url, headers=repost_headers, data=repost_data)
        if repost_res.json()["ok"] == 1:
            repost_dict = {
                "b_repost_mid": mid,
                "l_repost_mid": repost_res.json()["data"]["id"],
                "created_at": repost_res.json()["data"]["created_at"],
            }
            return self.req_res(
                status=1,
                res_name="repost_dict",
                res=repost_dict
            )
        else:
            errmsg = {repost_res.json()['msg']}
            return self.req_res(
                status=0,
                errmsg=errmsg
            )

    def comment_story(self, mid, st, content):
        """
        评论微博
        :param mid: 微博mid
        :param st: get_st()获取
        :param content: 转发描述
        :return:
        """
        comment_story_data = {
            "content": content,
            "mid": mid,
            "st": st,
            "_spr": "screen:411x731"
        }
        comment_story_headers = {
            "referer": f"https://m.weibo.cn/detail/{mid}"
        }
        comment_story_headers.update(self.headers)
        comment_story_res = requests.post(self.comment_story_url, headers=comment_story_headers,
                                          data=comment_story_data)
        if comment_story_res.json()["ok"] == 1:
            comment_story_dict = {
                "comment_story_mid": mid,
                "comment_cid": comment_story_res.json()['data']['id'],
                "created_at": comment_story_res.json()['data']['created_at']
            }
            return self.req_res(
                status=1,
                res_name="comment_dict",
                res=comment_story_dict
            )
        else:
            errmsg = comment_story_res.json()['msg']
            return self.req_res(
                status=0,
                errmsg=errmsg
            )

    def star_story(self, mid, st):
        """
        点赞微博
        :param mid: 微博mid
        :param st: get_st()获取
        :return:
        """
        star_data = {
            "id": mid,
            "attitudes": "heart",
            "st": st,
            "_spr": "screen:411x731"
        }
        star_headers = {
            "referer": f"https://m.weibo.cn/detail/{mid}"
        }
        star_headers.update(self.headers)
        star_res = requests.post(url=self.star_story_url, headers=star_headers, data=star_data)
        if star_res.json()["ok"] == 1:
            star_dict = {
                "star_story_mid": mid,
                "star_id": star_res.json()["data"]["id"],
                "created_at": star_res.json()["data"]["created_at"],

            }
            return self.req_res(
                status=1,
                res_name="star_dict",
                res=star_dict
            )
        else:
            errmsg = "点赞失败"
            return self.req_res(
                status=0,
                errmsg=errmsg
            )

    def delete_story(self, mid, st):
        """
        删除微博
        :param mid: 微博mid
        :param st: get_st()获取
        :return:
        """
        delete_story_data = {
            "mid": mid,
            "st": st,
            "_spr": "screen:411x731"
        }
        delete_story_headers = {
            "referer": f"https://m.weibo.cn/detail/{mid}"
        }
        delete_story_headers.update(self.headers)
        delete_story_res = requests.post(
            url=self.delete_story_url,
            headers=delete_story_headers,
            data=delete_story_data
        )
        if delete_story_res.json()["ok"] == 1:
            return True
        else:
            return False

    def delete_comment(self, cid, st):
        """
        删除评论
        :param cid: 评论cid
        :param st: get_st()获取
        :return:
        """
        delete_comment_data = {
            "cid": cid,
            "st": st,
            "_spr": "screen:411x731"
        }
        delete_comment_headers = {
            "referer": f"https://m.weibo.cn/detail/{cid}"
        }
        delete_comment_headers.update(self.headers)
        delete_comment_res = requests.post(
            url=self.delete_comment_url,
            headers=delete_comment_headers,
            data=delete_comment_data
        )
        if delete_comment_res.json()["ok"] == 1:
            return True
        else:
            return False

    def delete_star(self, mid, st):
        """
        取消点赞
        :param mid: 微博mid
        :param st: get_st()获取
        :return:
        """
        delete_star_data = {
            "id": mid,
            "attitude": "heart",
            "st": st,
            "_spr": "screen:411x731"
        }
        delete_star_headers = {
            "referer": f"https://m.weibo.cn/detail/{mid}"
        }
        delete_star_headers.update(self.headers)
        delete_star_res = requests.post(
            url=self.delete_star_url,
            headers=delete_star_headers,
            data=delete_star_data
        )
        if delete_star_res.json()["ok"] == 1:
            return True
        else:
            return False

    def server_push(self, sckey, log):
        """
        Sever酱推送：https://sc.ftqq.com/3.version
        :param sckey:
        :param log:
        :return:
        """
        now_time = datetime.datetime.now()
        bj_time = now_time + datetime.timedelta(hours=8)
        test_day = datetime.datetime.strptime('2020-12-26 00:00:00', '%Y-%m-%d %H:%M:%S')
        date = (test_day - bj_time).days
        text = f"微博超话打卡---{bj_time.strftime('%m/%d')}"
        desp = f"""
------
#### 🚁Now：
```
{bj_time.strftime("%Y-%m-%d %H:%M:%S %p")}
```
{log}

#### 🚀Deadline:
```
考研倒计时--{date}天
```

>
> [GitHub项目地址](https://github.com/ReaJason/WeiBo_SuperTopics) 
>
>期待你给项目的star✨
"""
        server_push_headers = {
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        send_url = f"https://sc.ftqq.com/{sckey}.send"
        params = {
            "text": text,
            "desp": desp
        }
        response = requests.post(send_url, data=params, headers=server_push_headers)
        if response.json()["errmsg"] == 'success':
            print("微信推送成功")
        else:
            print("微信推送失败")

    def cool_push(self, skey, log):
        """
        CoolPush推送：https://cp.xuthus.cc/
        :param skey:
        :param log:
        :return:
        """
        push_url = f"https://push.xuthus.cc/send/{skey}"
        data = {
            "c": log.encode("utf-8")
        }
        push_response = requests.post(push_url, data)
        # print(push_response.json())
        if push_response.json()["code"] == 200:
            print("QQ推送成功")

    def req_res(self, status, res_name=None, res=None, errmsg=None):
        """
        封装响应数据，便于做数据判断
        :param status:
        :param res_name:
        :param res:
        :param errmsg:
        :return:
        """
        if errmsg:
            restful = {
                "status": status,
                "errmsg": errmsg,
                "result": res
            }
        else:
            restful = {
                "status": status,
                res_name: res
            }
        return restful

    # 每日超话签到+每日积分获取+超话APP登录积分+超话打榜+超话评论转发+任务中心
    def daily_task(self, s, pick, sckey):
        log = []
        user = self.get_profile()
        log.append("#### 💫‍User：")
        if user["status"]:
            log.append("```")
            log.append(user["user"]["user_msg"])
            log.append("```")
            topic_list = self.get_topic_list()
            print("开始超话签到")
            log.append("#### ✨CheckIn：")
            log.append("```")
            for topic in topic_list:
                check_dict = self.check_in(s, topic)
                if check_dict["status"]:
                    log.append(check_dict["msg"])
                else:
                    log.append(check_dict["errmsg"])
                    break
            log.append("```")
            print("获取每日积分")
            log.append("#### 🔰DailyScore：")
            log.append("```")
            log.append(self.get_day_score())
            log.append("```")
            print("获取登录积分")
            log.append("#### 🔰LoginScore：")
            log.append("```")
            log.append(self.get_active_score())
            log.append("```")
            print("超话评论转发")
            log.append("#### ✅Post：")
            log.append("```")
            log.append(self.repost_comment(topic_list[-1]))
            log.append("```")
            print("指定超话打榜")
            log.append("#### 💓Pick：")
            log.append("```")
            log.append(self.get_score_bang([topic for topic in topic_list if topic["topic_title"] == pick]))
            log.append("```")
            print("积分任务中心")
            log.append("#### 🌈TaskCenter：")
            log.append("```")
            log.append(self.task_center())
            log.append("```")
            self.server_push(sckey, "\n".join(log))
        else:
            log.append("```")
            log.append(user["errmsg"])
            log.append("```")
            self.server_push(sckey, "\n".join(log))
