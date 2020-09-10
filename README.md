## 🎐WeiBo_SuperTopics

> ✨欢迎star，有问题可以提issue一起学习交流
>
> 💫每日积分获取40+积分
>
> 💢超话签到连续签到7天之后好像账户会异常需要验证……



### 🌍功能简介

- 关注超话签到 +16分+6点以后签到随机积分
- 每日积分获取 +8分
- 微博超话APP登录积分 +10分【验证设备】
- 超话帖子评论转发点赞 +16分
- 超话打榜 -66分
- 任务中心查询积分
- 微信推送消息



### 🚀运作流程

##### 1、Secrets

```python
# 设置如下secrets字段:

COOKIE  # 通过登录https://m.weibo.cn/获取cookie
S  # 通过抓包微博国际版APP签到请求获取
PICK  # 设置自己打榜的超话名字,例如：喻言
SCKEY  # 通过https://sc.ftqq.com/3.version获取
```

##### 2、Schedule

```python
# 设置早上6点进行每日任务，有一定延迟
# 五位数(空格分隔)分别为分钟、小时、天、月、一个星期的第几天
# 国际时与北京时的查询网站：http://www.timebie.com/cn/universalbeijing.php

schedule:
	- cron: 0 22 * * *
```

##### 3、DailyTask

```python
# 有能力可以自定义自己的每日任务
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
            log.append(self.check_in(s, topic))
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
```



### 🚧使用步骤

1. 获取cookie
   - Chrome登录[微博手机版](https://m.weibo.cn/)
   - F12抓取任意请求获取cookie字段
2. 获取s参数
   - 有Root手机下载Httpcanary抓取微博国际版app的签到请求包
   - 使用mumu模拟器+Fiddle或mumu模拟器+Httpcanary抓取微博国际版app的签到请求包
3. 获取sckey
   - 进入[Server酱](https://sc.ftqq.com/3.version)
   - GIthub账号登陆并绑定微信获取sckey
4. fork本仓库
5. 设置secrets字段
   - COOKIE
   - S
   - PICK
   - SCKEY
6. 开启Actions
   - 找到自己fork的库，点击Settings->Action->I understand...
   - 回到项目主页，修改README.md触发Actions



### 🏝功能详情

1. 关注超话签到
   
   - 超话等级越高，签到积分越高
   - 连续签到7天之后会出现异常，需要验证，未找到解决办法
   - 默认降序排序，超话等级高先签到、签到过的超话将不再进行数据请求进行签到
2. 每日积分获取
   - 连续签到积分最高8分
3. 微博超话APP登录积分
   - 该接口验证ip设备，只有在已登录ip才可生效，以目前能力暂GitHub上无法成功
   - 在本地网页登录微博成功后，程序运行是可以成功的
4. 超话帖子评论转发点赞
   - 已优化评论转发积分获取，将获取关注超话列表等级最低的超话进行无痕刷分
   - 进入关注超话等级最低的超话，转发评论所带的content都为💦
   - 转发评论点赞完后都会进行删除微博、删除评论和取消点赞操作，因此是进行的无痕获取积分
5. 超话打榜
   - 通过设置的PICK在关注超话列表进行查找，如果设置的PICK未关注则不打榜
   - 有几率会出现账号异常的检测操作，暂无法解决，可自行通过微博app进行打榜
6. 任务中心查询积分

   - 仅作积分展示
7. 微信推送消息

   - 用来查看积分获取情况



### 🏍更新记录

**💥2020/09/10：增加微博超话APP登录积分获取接口，该接口GitHub Actions上暂无法成功**

**💗2020/09/08：增加微博评论解析、酷推等接口，更新README文档，代码重构**

**🎲2020/09/04：增加删除微博、删除评论、取消点赞接口，优化喻言超话评论**

**🏳2020/08/31：增加打榜382023账户异常的判断**

**🎉2020/08/29：增加喻言超话评论，增加任务中心积分显示**

**💤2020/08/28：增加打榜计划，优化微信推送格式**

**🌈2020/08/27：第一次提交**



### 🚁成果图



<img src="https://cdn.jsdelivr.net/gh/ReaJason/WeiBo_SuperTopics/Pictures/result.jpg" width = "500" div align=center />



### ♻致谢

感谢[wxy1343/weibo_points](https://github.com/wxy1343/weibo_points)的接口参考