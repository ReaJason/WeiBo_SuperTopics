"""
接口主要抓自https://m.weibo.cn/, cookie也来自于此
"""
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
        self.delete_follow_url = "https://m.weibo.cn/api/container/btn?module=follow&uid={}&cardid={}"
        self.get_all_photo_url = "https://photo.weibo.com/photos/get_all"
        self.get_all_comments_url = "https://m.weibo.cn/message/myCmt?page={}"
        self.get_all_stories_url = "https://m.weibo.cn/api/container/getIndex?containerid={}&page_type=03&page={}"
        self.get_all_follow_url = "https://m.weibo.cn/api/container/getIndex?containerid=231093-selffollowed&page={}"
        self.cookie = cookie
        self.nickname = None
        self.gsid = re.findall("SUB=(.*?);", cookie)[0] if re.findall("SUB=(.*?);", cookie) else None

    def get_headers(self, method='android', dict=None, **kwargs):
        android_user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Mobile Safari/537.36'
        ]
        windows_user_agent = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36 Edg/86.0.622.68',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'
        ]
        if method == 'android':
            headers = {'User-Agent': random.choice(android_user_agents), 'cookie': self.cookie}
            headers.update(kwargs)
            if dict:
                headers.update(dict)
            return headers
        elif method == 'windows':
            headers = {'User-Agent': random.choice(windows_user_agent), 'cookie': self.cookie}
            headers.update(kwargs)
            if dict:
                headers.update(dict)
            return headers
        else:
            return None

    @staticmethod
    def wrap_request(method, url, timeout=10, **kwargs):
        try:
            res = requests.request(
                method=method,
                url=url,
                timeout=timeout, **kwargs)
            return res
        except requests.exceptions.ConnectionError:
            return {"status": 0, "errmsg": '无法访问网络，获取失败'}
        except Exception as e:
            return {"status": 0, "errmsg": f'错误类型：{e}\n错误详情：{e.__class__}'}

    def get_profile(self):
        profile_res = self.wrap_request('get', self.profile_url, headers=self.get_headers())
        if isinstance(profile_res, dict):
            return profile_res
        content_type = profile_res.headers["Content-Type"]
        if content_type == "application/json; charset=utf-8":
            user = profile_res.json()["data"]["user"]
            self.nickname = user["screen_name"]
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
            return {'status': 1, 'user': user_dict}
        else:
            return {'status': 0, 'errmsg': '获取个人信息失败，请设置Cookie后重试'}

    def get_topic_list(self):
        topic_list = []
        since_id = ""
        while True:
            topic_params = {"containerid": "100803_-_followsuper", "since_id": since_id}
            topic_res = self.wrap_request('get', url=self.get_index_url, params=topic_params,
                                          headers=self.get_headers())
            if isinstance(topic_res, dict):
                return topic_res
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
                        topic_list.append(topic_dict)
            since_id = topic_res.json()["data"]["cardlistInfo"]["since_id"]
            if since_id == "":
                topic_list.sort(key=lambda x: int(x["topic_level"]), reverse=True)
                if topic_list:
                    return topic_list
                else:
                    self.get_topic_list()

    def get_story_list(self, topic_id):
        """
        获取超话微博（第一页）获取多页设置最后if count == 1:中的 1 即可
        :param topic_id: 超话id
        :return:
        """
        count = 0
        since_id = ""
        stories_list = []
        while True:
            index_res = self.parse_topic(topic_id=topic_id, since_id=since_id)
            if index_res["status"]:
                scheme_list = index_res["topic_info"]["cards_id"]
                for scheme in scheme_list:
                    story_res = self.parse_story_body(re.findall('[0-9a-zA-Z]{9}', scheme)[0])
                    if story_res["status"] == 1:
                        stories_list.append(story_res["story_info"])
                since_id = index_res["topic_info"]["since_id"]
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
        check_data = {"c": "weicoabroad", "s": s, "wm": "2468_1001", "gsid": self.gsid,
                      "from": "1299295010", "source": "4215535043", "lang": "zh_CN",
                      'ua': "Redmi+K20+Pro+Premium+Edition_10_WeiboIntlAndroid_3610",
                      "request_url": f"http%3A%2F%2Fi.huati.weibo.com%2Fmobile%2Fsuper%2Factive_checkin%3Fpageid%3D{topic_dict['topic_id']}",
                      }
        if topic_dict["topic_status"] == "签到":
            time.sleep(random.randint(1, 2))
            check_res = self.wrap_request('get', url=self.check_url, headers=self.get_headers(),
                                          params=check_data)
            # print(check_res.json())
            if check_res.json().get('errmsg'):
                return dict(status=0, errmsg=f'{check_res.json()["errmsg"]}')
            if check_res.json()["result"] == '1':
                success_msg = check_res.json()["msg"].replace("\n", "/")
                msg = f'TopicName：{topic_dict["topic_title"]}\nLevel：{topic_dict["topic_level"]}\nMessage：{success_msg}\n'
                return dict(status=1, msg=msg)
            elif check_res.json()["result"] == 388000:
                print(check_res.json())
                errmsg = "💢签到异常需要滑块验证，暂未找到合适的解决办法"
                return dict(status=0, errmsg=errmsg)
        else:
            msg = f'TopicName：{topic_dict["topic_title"]}\nLevel：{topic_dict["topic_level"]}\nMessage：今日已签到\n'
            return dict(status=1, msg=msg)

    def get_daily_score(self):
        """
         超话每日积分领取
        :return:
        """
        day_score_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://huati.weibo.cn'
        }

        score_data = {'type': 'REQUEST', 'user_score': 999}
        day_score_res = self.wrap_request('post', url=self.day_score_url,
                                          headers=self.get_headers(dict=day_score_headers),
                                          data=score_data
                                          )
        if isinstance(day_score_res, dict):
            return day_score_res
        if day_score_res.json()["code"] == 100000:
            msg = f'今日签到积分获取：{day_score_res.json()["data"]["add_score"]}分'
            return dict(status=1, msg=msg)
        elif day_score_res.json()["code"] == 386011:  # {'status': 0, 'msg': '该任务今日已领取过'}
            msg = f'{day_score_res.json()["msg"]}'
            return dict(status=0, msg=msg)
        elif day_score_res.json()["code"] == 100002:
            msg = f'{day_score_res.json()["msg"]}'
            return dict(status=0, msg=msg)
        else:
            return dict(status=0, msg=f"获取失败：{day_score_res.text}")

    def get_active_score(self):
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
        active_res = self.wrap_request('get', self.active_score_url, params=parmas,
                                       headers=self.get_headers(dict=get_active_score_headers)
                                       )
        if isinstance(active_res, dict):
            return active_res
        # print(active_res.json())
        if active_res.json()['code'] == 100000:
            if "388000" in active_res.json()['toast']:
                return dict(status=0, msg="请确保该设备登录过")
            else:
                if active_res.json()['toast']:
                    return dict(status=1, msg=active_res.json()['toast'])
                else:
                    return dict(status=0, msg='该任务今日已领取过')
        else:
            return

    def pick_topic(self, topic_dict, pick_score):
        pick_dict = {
            "select1": 1,
            "select10": 10,
            "select66": 66,
            "select256": 0
        }
        referer_url = f"https://huati.weibo.cn/aj/super/getscore?" \
                      f"page_id={topic_dict['topic_id']}&aid=&from=1110006030"
        get_score_headers = {
            "Referer": referer_url,
            "X-Requested-With": "XMLHttpRequest",
            'cookie': self.cookie
        }
        score_res = self.wrap_request('get', referer_url,
                                      headers=self.get_headers(method='windows', dict=get_score_headers))
        if isinstance(score_res, dict):
            return score_res
        if score_res.json()['code'] == 201001:  # {'code': 100002, 'msg': '系统繁忙，请稍后再试！'}
            return dict(status=0, msg=f"{topic_dict['topic_title']} {score_res.json()['msg']}")
        elif score_res.json()['code'] == 100002:  # {'code': 100002, 'msg': '请登录后再进行操作'}
            return dict(status=0, msg=f"{topic_dict['topic_title']} {score_res.json()['msg']}")
        elif score_res.json()['code'] == 386007:  # {'code': 100002, 'msg': '这类话题不支持打榜'}
            return dict(status=0, msg=f"{topic_dict['topic_title']} {score_res.json()['msg']}")
        topic_name = score_res.json()["data"]["topic_name"]
        rank = score_res.json()["data"]["rank"]
        # print(score_res.json())
        if score_res.json()["data"]["user_total_score"] > pick_dict[pick_score]:
            while True:
                pick_data = {
                    "topic_name": topic_dict["topic_title"],
                    "page_id": topic_dict["topic_id"],
                    "score": str(pick_dict[pick_score]) if str(pick_dict[pick_score]) != '0' else str(
                        score_res.json()["data"]["user_total_score"]),
                    "is_pub": "0",
                    "cur_rank": score_res.json()["data"]["rank"],
                    "ctg_id": score_res.json()["data"]["ctg_id"],
                    "topic_score": score_res.json()["data"]["score"],
                    "index": pick_score,
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
                elif pick_res.json()["code"] == 383137:  # {"code":383137,"msg":"系统繁忙，请稍后重试！"}
                    time.sleep(random.randint(5, 8))
                    continue
                elif pick_res.json()["code"] == 302001:
                    return dict(status=0, errmsg=pick_res.json()["msg"])
                elif pick_res.json()["code"] == 382023:  # {'code': 382023, 'msg': '你最近的行为存在异常，请先验证身份后再进行操作。'}
                    return dict(status=0, errmsg=pick_res.json()["msg"])
                elif pick_res.json()["code"] == 100000:
                    return dict(status=1, result={'topic_name': topic_name, 'rank': rank,
                                                  'msg': f"{pick_res.json()['data'].get('add_int_msg') if pick_res.json()['data'].get('add_int_msg', None) else pick_res.json()['data'].get('msg', f'打榜成功 此次打榜积分：{pick_dict[pick_score]}')}"}
                                )
                else:
                    return dict(status=0, errmsg=f'打榜失败{pick_res.text}')
        else:
            return dict(status=1, result={'topic_name': topic_name, 'rank': rank,
                                          'msg': f"积分少于{pick_score}，无法打榜"}
                        )

    def task_center(self):
        """
        积分任务中心
        :return:
        """
        task_headers = {
            "Referer": "https://huati.weibo.cn/super/taskcenter?aid=&from=1110006030",
            "X-Requested-With": "XMLHttpRequest"
        }
        task_res = self.wrap_request('get', self.task_center_url,
                                     headers=self.get_headers('windows', dict=task_headers))
        if isinstance(task_res, dict):
            return task_res
        if task_res.json()["code"] == 100000:
            task_dict = {
                "total_score": task_res.json()["data"]["total_score"],
                "al_get_score": task_res.json()["data"]["al_get_score"],
                "day_score": task_res.json()["data"]["task_per_day"]["request"],
                "be_comment": task_res.json()["data"]["task_per_day"]["be_comment"],
                "lclient_day": task_res.json()["data"]["task_per_day"]["lclient_day"],
                "topic_check": task_res.json()["data"]["task_per_day"]["checkin"],
                "simple_comment": task_res.json()["data"]["task_per_day"]["simple_comment"],
                "simple_repost": task_res.json()["data"]["task_per_day"]["simple_repost"],
                "msg": f"""当前积分总额：{task_res.json()["data"]["total_score"]}分
今日积分获取：{task_res.json()["data"]["al_get_score"]}分
每日访问积分：已获取{task_res.json()["data"]["task_per_day"]["request"]}分/{task_res.json()["data"]["request_desc"]}
超话登录积分：已获取{task_res.json()["data"]["task_per_day"]["lclient_day"]}分/每日上限10分
超话打卡签到：已签到{task_res.json()["data"]["task_per_day"]["checkin"]}次/每日上限8次
超话帖子评论：已获取{task_res.json()["data"]["task_per_day"]["simple_comment"]}分/每日上限12分
超话帖子转发：已获取{task_res.json()["data"]["task_per_day"]["simple_repost"]}分/每日上限4分
"""
            }
            return dict(status=1, task_dict=task_dict)
        else:
            return dict(status=0, errmsg=task_res.text)

    def repost_comment(self, topic_dict):
        """
        转发、评论、点赞超话第一页帖子并删除转发、删除评论、取消点赞
        :param topic_dict: 超话信息字典,具体格式请看get_topic_list函数中
        :return:
        """
        story_list = self.get_story_list(topic_dict["topic_id"])
        contents = "💦"
        repost_count = 0
        comment_count = 0
        star_count = 0
        delete_repost = 0
        delete_comment = 0
        delete_star = 0
        for story in story_list:
            time.sleep(random.randint(5, 7))
            st = self.get_st()
            if repost_count < 2:
                repost_res = self.repost_story(story["story_mid"], st, contents)
                if repost_res["status"]:
                    repost_count += 1
                    time.sleep(random.randint(5, 7))
                    if self.delete_story(repost_res["repost_dict"]["l_repost_mid"], st):
                        delete_repost += 1
            if comment_count < 6:
                comment_res = self.comment_story(story["story_mid"], st, contents)
                if comment_res["status"]:
                    comment_count += 1
                    time.sleep(random.randint(5, 7))
                    if self.delete_comment(comment_res["comment_dict"]["comment_cid"], st):
                        delete_comment += 1
            star_res = self.star_story(story["story_mid"], st)
            if star_res["status"]:
                star_count += 1
                time.sleep(random.randint(5, 7))
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
        st_response = self.wrap_request('get', self.config_url, headers=self.get_headers())
        if isinstance(st_response, dict):
            return None
        if st_response.json()["ok"] == 1:
            if str(st_response.json()["data"]["login"]) == "True":
                st = st_response.json()["data"]["st"]
                return st
            else:
                return None
        else:
            return None

    def get_user_first_blog(self, user_id):
        get_id_params = {
            "type": "uid",
            "value": user_id
        }
        get_id_res = self.wrap_request('get', url=self.get_index_url, params=get_id_params, headers=self.get_headers())
        if isinstance(get_id_res, dict):
            return get_id_res
        data = get_id_res.json()["data"]
        container_id = data["tabsInfo"]["tabs"][1]["containerid"]
        blog_params = {
            "type": "uid",
            "value": user_id,
            "containerid": container_id
        }
        blog_res = self.wrap_request('get', url=self.get_index_url, params=blog_params, headers=self.get_headers())
        if isinstance(blog_res, dict):
            return blog_res
        cards = blog_res.json()["data"]["cards"]
        for card in cards:
            if card["card_type"] == 9:
                if card["mblog"].get("isTop"):
                    continue
                return self.parse_story_body(card["mblog"]["mid"])

    def parse_topic(self, topic_id, since_id=None):
        topic_params = {
            "since_id": since_id,
            "containerid": topic_id
        }
        topic_res = self.wrap_request('get', url=self.get_index_url, params=topic_params, headers=self.get_headers())
        if isinstance(topic_res, dict):
            return topic_res
        if topic_res.json()["ok"]:
            pageinfo = topic_res.json()["data"]["pageInfo"]
            cards = topic_res.json()["data"]["cards"]
            pageinfo_dict = {
                "nick": pageinfo["nick"],
                "portrait_hd": pageinfo["portrait_hd"],
                "portrait_sub_text": pageinfo["portrait_sub_text"],
                "desc_more": pageinfo["desc_more"],
                "detail_desc": pageinfo["detail_desc"],
                "containerid": pageinfo["containerid"],
                "since_id": pageinfo["since_id"],
                "select_id": pageinfo["select_id"],
                "cards_id": [card["scheme"].split("?")[0].split("/")[-1]
                             for card_group in
                             [card_group["card_group"] for card_group in cards if not card_group["itemid"]]
                             for card in card_group
                             if card["card_type"] == '9']

            }
            return dict(status=1, topic_info=pageinfo_dict)
        else:
            return dict(status=0, errmsg="这里还没有内容")

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
            return dict(status=1, story=story)
        else:
            return story_body

    def parse_story_body(self, story_id):
        parse_params = {
            "id": story_id
        }
        detail_res = self.wrap_request('get', self.detail_story_url, params=parse_params, headers=self.get_headers())
        if isinstance(detail_res, dict):
            return detail_res
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
            return dict(status=1, story_info=story_dict)
        else:
            return dict(status=0, errmsg="未找到该微博或获取信息失败")

    def parse_story_comment(self, story_id):
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
            story_comment_res = self.wrap_request('get', self.story_comment_url, params=comment_params,
                                                  headers=self.get_headers(dict=story_comment_headers))
            if isinstance(story_comment_res, dict):
                return story_comment_res
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
        comment_list = []
        max_id = 0
        while True:
            time.sleep(random.randint(2, 3))
            comment_params = {
                "cid": cid,
                "max_id": max_id,
                "max_id_type": "0"
            }
            comment_headers = {
                "referer": f"https://m.weibo.cn/detail/{mid}?cid={cid}"
            }
            comment_res = self.wrap_request('get', self.parse_comment_url, params=comment_params,
                                            headers=self.get_headers(dict=comment_headers))
            if isinstance(comment_res, dict):
                return comment_res
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
        repost_res = self.wrap_request('post', self.repost_story_url, headers=self.get_headers(dict=repost_headers),
                                       data=repost_data)
        if isinstance(repost_res, dict):
            return repost_res
        if repost_res.json()["ok"] == 1:
            repost_dict = {
                "b_repost_mid": mid,
                "l_repost_mid": repost_res.json()["data"]["id"],
                "created_at": repost_res.json()["data"]["created_at"],
            }
            return dict(status=1, repost_dict=repost_dict)
        else:
            return dict(status=0, errmsg=repost_res.json()['msg'])

    def comment_story(self, mid, st, content):
        comment_story_data = {
            "content": content,
            "mid": mid,
            "st": st,
            "_spr": "screen:411x731"
        }
        comment_story_headers = {
            "referer": f"https://m.weibo.cn/detail/{mid}"
        }
        comment_story_res = self.wrap_request('post', self.comment_story_url,
                                              headers=self.get_headers(dict=comment_story_headers),
                                              data=comment_story_data)
        if isinstance(comment_story_res, dict):
            return comment_story_res
        if comment_story_res.json()["ok"] == 1:
            comment_story_dict = {
                "comment_story_mid": mid,
                "comment_cid": comment_story_res.json()['data']['id'],
                "created_at": comment_story_res.json()['data']['created_at']
            }
            return dict(status=1, comment_dict=comment_story_dict)
        else:
            return dict(status=0, errmsg=comment_story_res.json()['msg'])

    def star_story(self, mid, st):
        star_data = {
            "id": mid,
            "attitudes": "heart",
            "st": st,
            "_spr": "screen:411x731"
        }
        star_headers = {
            "referer": f"https://m.weibo.cn/detail/{mid}"
        }
        star_res = self.wrap_request('post', url=self.star_story_url, headers=self.get_headers(dict=star_headers),
                                     data=star_data)
        if isinstance(star_res, dict):
            return star_res
        if star_res.json()["ok"] == 1:
            star_dict = {
                "star_story_mid": mid,
                "star_id": star_res.json()["data"]["id"],
                "created_at": star_res.json()["data"]["created_at"],

            }
            return dict(status=1, star_dict=star_dict)
        else:
            return dict(status=0, errmsg=f"点赞失败/{star_res.text}")

    def delete_story(self, mid, st):
        delete_story_data = {
            "mid": mid,
            "st": st,
            "_spr": "screen:411x731"
        }
        delete_story_headers = {
            "referer": f"https://m.weibo.cn/detail/{mid}",
        }
        delete_story_res = self.wrap_request('post', url=self.delete_story_url,
                                             headers=self.get_headers(dict=delete_story_headers),
                                             data=delete_story_data)
        if delete_story_res.json()["ok"] == 1:
            return dict(status=1, msg="微博删除成功")
        else:
            return dict(status=0, errmsg=f'微博删除失败/{delete_story_res.text}')

    def delete_comment(self, cid, st):
        delete_comment_data = {
            "cid": cid,
            "st": st,
            "_spr": "screen:411x731"
        }
        delete_comment_headers = {
            "referer": f"https://m.weibo.cn/detail/{cid}"
        }
        delete_comment_res = self.wrap_request('post', url=self.delete_comment_url,
                                               headers=self.get_headers(dict=delete_comment_headers),
                                               data=delete_comment_data)
        if isinstance(delete_comment_res, dict):
            return delete_comment_res
        if delete_comment_res.json()["ok"] == 1:
            return dict(status=1, msg="评论删除成功")
        else:
            return dict(status=0, errmsg=f'评论删除失败/{delete_comment_res.text}')

    def delete_star(self, mid, st):
        delete_star_data = {
            "id": mid,
            "attitude": "heart",
            "st": st,
            "_spr": "screen:411x731"
        }
        delete_star_headers = {
            "referer": f"https://m.weibo.cn/detail/{mid}"
        }
        delete_star_res = self.wrap_request('post', url=self.delete_star_url,
                                            headers=self.get_headers(dict=delete_star_headers), data=delete_star_data)
        if isinstance(delete_star_res, dict):
            return delete_star_res
        if delete_star_res.json()["ok"] == 1:
            return dict(status=1, msg="取消点赞成功")
        else:
            return dict(status=0, errmsg=f"取消点赞失败/{delete_star_res.text}")

    def web_check(self, cookie, ch_dict):
        check_data = {
            "ajwvr": "6",
            "api": "http://i.huati.weibo.com/aj/super/checkin",
            "texta": "签到",
            "textb": "已签到",
            "status": "0",
            "id": ch_dict["id"],
            "location": "page_100808_super_index",
            "timezone": "GMT 0800",
            "lang": "zh-cn",
            "plat": "Win32",
            "ua": "Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20"
                  "(KHTML,%20like%20Gecko)%20Chrome/84.0.4147.89%20Safari/537.36",
            "screen": "1536*864",
            "__rnd": str(int(round(time.time() * 1000))),
        }
        web_headers = {
            "cookie": cookie,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
        }
        try:
            web_res = requests.get(
                url=self.web_check_url,
                headers=web_headers,
                params=check_data)
            return dict(status=1, msg=web_res.json()["msg"])
        except Exception as e:
            print(e.__class__)
            print(e)
            return dict(status=0, errmsg="网络连接错误")

    def delete_follow(self, follow_dict, st):
        delete_follow_data = {
            "uid": follow_dict["uid"],
            "sub_type": "1",
            "st": st,
            "_spr": "screen:1536x864"
        }
        delete_follow_headers = {
            "referer": "https://m.weibo.cn/p/index?containerid=231093_-_selffollowed"}
        delete_follow_res = self.wrap_request('post',
                                              data=delete_follow_data,
                                              url=self.delete_follow_url.format(
                                                  follow_dict["uid"],
                                                  follow_dict["cardid"]),
                                              headers=self.get_headers(dict=delete_follow_headers))
        if isinstance(delete_follow_res, dict):
            return delete_follow_res
        if delete_follow_res.json()["data"]["button"]["sub_type"] == 0:
            return dict(status=1, msg=f"{follow_dict['name']}取关成功")
        else:
            return dict(status=0, msg=f"{follow_dict['name']}取关失败/{delete_follow_res.text}")

    def get_all_comments(self):
        comments_list = []
        all_comments_headers = {
            "upgrade-insecure-requests": "1"
        }
        for page in range(1, 200):
            print(f"正在获取第{page}页~~~")
            time.sleep(random.randint(1, 2))
            res = self.wrap_request('get', self.get_all_comments_url.format(page),
                                    headers=self.get_headers(dict=all_comments_headers))
            if isinstance(res, dict):
                return res
            data = res.json()["data"]
            if data:
                for item in data:
                    comment_dict = {
                        "cid": item["id"],
                        "text": item["text"]
                    }
                    comments_list.append(comment_dict)
            else:
                return dict(status=1, comments_list=comments_list)

    def delete_all_comments(self):
        comment_list = self.get_all_comments()
        st = self.get_st()
        for item in range(len(comment_list['comments_list'])):
            if item % 10 == 0:
                time.sleep(20)
            self.delete_comment(comment_list['comments_list'][item]["cid"], st)

    def get_all_stories(self, container_id):
        stories_list = []
        all_stories_headers = {
            "referer": f"https://m.weibo.cn/p/{container_id}"
        }
        for page in range(1, 2000):
            print(f"正在获取第{page}页~~~")
            res = self.wrap_request('get', self.get_all_stories_url.format(container_id, page),
                                    headers=self.get_headers(dict=all_stories_headers))
            if isinstance(res, dict):
                return res
            cards = res.json()["data"]["cards"]
            st = self.get_st()
            for card in cards:
                if card["card_type"] == 9:
                    story_dict = {
                        "mid": card["mblog"]["id"],
                        "text": card["mblog"]["text"]
                    }
                    time.sleep(random.randint(2, 3))
                    self.delete_story(story_dict["mid"], st)
                    stories_list.append(story_dict)
                elif card["card_type"] == 58:
                    return dict(status=1, stories_list=stories_list)

    def delete_all_stories(self):
        container_id = self.get_profile()["wei_container_id"]
        story_list = self.get_all_stories(container_id)
        st = self.get_st()
        for item in range(len(story_list['stories_list'])):
            if item % 10 == 0:
                time.sleep(20)
            time.sleep(random.randint(2, 3))
            self.delete_story(story_list['stories_list'][item]["mid"], st)

    def get_all_self_follows(self):
        self_follow_list = []
        all_follow_headers = {
            "referer": "https://m.weibo.cn/p/index?containerid=231093_-_selffollowed"}
        page = 1
        while True:
            time.sleep(random.randint(1, 2))
            res = self.wrap_request('get', self.get_all_follow_url.format(page),
                                    headers=self.get_headers(dict=all_follow_headers))
            if isinstance(res, dict):
                return res
            if res.json()["ok"] == 1:
                print(f"正在获取第{page}页~~~")
                page += 1
                cards = res.json()["data"]["cards"]
                for card_group in cards:
                    for card in card_group["card_group"]:
                        if card["card_type"] == 10:
                            follow_dict = {
                                "id": card["user"]["id"],
                                "name": card["user"]["screen_name"],
                                "avatar": f'https://wx1.sinaimg.cn/large/'
                                          f'{card["user"]["profile_image_url"].split("?")[0].split("/")[-1]}',
                                "desc": card["desc1"],
                                "uid": card["actionlog"]["oid"],
                                "cardid": card["actionlog"]["cardid"],
                                "home": card["scheme"]}
                            self_follow_list.append(follow_dict)
            else:
                return dict(status=1, self_follow_list=self_follow_list)

    def delete_all_follow(self):
        follow_list = self.get_all_self_follows()
        st = self.get_st()
        for follow_dict in follow_list:
            time.sleep(random.randint(2, 3))
            self.delete_follow(follow_dict, st)

    def get_all_photo(self, uid, album_id):
        page = 1
        url_list = []
        while True:
            params = {
                "uid": uid,
                "album_id": album_id,
                "count": 30,
                "page": page,
                "type": 1,
                "__rnd": round(time.time() * 1000)
            }
            try:
                time.sleep(random.randint(1, 2))
                res = requests.get(self.get_all_photo_url, headers=self.get_headers(),
                                   params=params).json()
                page += 1
            except:
                return None
            photo_list = res['data']['photo_list']
            if photo_list:
                for photo in photo_list:
                    url_list.append(f"{photo.pic_host}/large/{photo.pic_name}")
            else:
                return url_list

    def server_push(self, sckey, log):
        """
        Server酱服务：https://sc.ftqq.com/3.version
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
        try:
            response = requests.post(send_url, data=params, headers=server_push_headers)
            if response.json()["errmsg"] == 'success':
                print("微信推送成功")
            else:
                print("微信推送失败")
        except:
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
        try:
            push_response = requests.post(push_url, data)
            if push_response.json()["code"] == 200:
                print("QQ推送成功")
            else:
                print('QQ推送失败')
        except:
            print('QQ推送失败')

