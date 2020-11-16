## 🎐WeiBo_SuperTopics

> ✨欢迎 star，有问题可以提 issue 一起学习交流
>
> 💫每日积分获取 40+ 积分
>
> 💢取消 Actions 任务，异地 IP 请求很容易异常，我三个号测试号都异常了
>
> 🚀GitHub Actions 开启就玩玩，大家可以试腾讯云函数 + 固定 IP 看能不能长期有用
>
> ✅Clone 到本地使用更佳，或者使用 Tasker + Termux 来进行手机自动化任务
>
> ✨可以试试我写的本地程序：[微博超话工具](https://reajason.top/2020/10/19/WeiBoSuperTopicsTool/)



### 🌍功能简介

- 关注超话签到 +16 分+6 点以后签到随机积分
- 每日积分获取 +8 分
- 微博超话APP登录积分 +10 分
- 超话帖子评论转发点赞 +16 分
- 超话打榜 -66 分
- 任务中心查询积分
- 微信推送消息



### 🚀运作流程

##### 1、参数设置

```python
cookie  # 通过登录https://m.weibo.cn/获取cookie
s  # 通过抓包微博国际版APP签到请求获取
pick  # 设置自己打榜的超话名字,例如：喻言
sckey  # 通过https://sc.ftqq.com/3.version获取
```

##### 2、每日任务

```python
# 有能力可以自定义自己的每日任务
# 每日超话签到+每日积分获取+超话APP登录积分+超话打榜+超话评论转发+任务中心

def run():
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format="[%(levelname)s]; %(message)s")
    log = []
    cookie = input()
    s = input()
    pick = input()
    sckey = input()
    wb = WeiBo(cookie)
    user = wb.get_profile()
    log.append("#### 💫‍User：")
    if not user['status']:
        logging.warning(user['errmsg'])
        return
    logging.info("获取个人信息成功✔")
    topic_list = wb.get_topic_list()
    log.append("```")
    log.append(user["user"]["user_msg"])
    log.append("```")
    logging.info("开始超话签到")
    log.append("#### ✨CheckIn：")
    log.append("```")
    for topic in topic_list:
        check_dict = wb.check_in(s, topic)
        if check_dict["status"]:
            log.append(check_dict["msg"])
            logging.info(check_dict)
        else:
            log.append(check_dict["errmsg"])
            logging.warning(check_dict["errmsg"])
            break
    log.append("```")
    logging.info("获取每日积分")
    log.append("#### 🔰DailyScore：")
    log.append("```")
    daily_res = wb.get_daily_score()
    if daily_res['status']:
        log.append(daily_res['msg'])
        logging.info(daily_res['msg'])
    else:
        log.append(daily_res['msg'])
        logging.warning(daily_res['msg'])
    log.append("```")
    logging.info("超话评论转发（正在执行，需要一点时间......）")
    log.append("#### ✅Post：")
    log.append("```")
    repost = wb.repost_comment(topic_list[-1])
    logging.info(repost)
    log.append(repost)
    log.append("```")
    logging.info("指定超话打榜")
    log.append("#### 💓Pick：")
    log.append("```")
    picks = [topic for topic in topic_list if topic["topic_title"] == pick]
    if not picks:
        errmsg = f"未关注【{pick}】该超话，请检查超话名字是否正确"
        logging.warning(errmsg)
        log.append(errmsg)
        return
    pick_res = wb.pick_topic(picks[0], "select66")
    if pick_res['status']:
        log.append(pick_res['result']['msg'])
        logging.info(pick_res['result']['msg'])
    else:
        log.append(pick_res['errmsg'])
        logging.warning(pick_res['errmsg'])
    log.append("```")
    logging.info("查询任务中心")
    log.append("#### 🌈TaskCenter：")
    log.append("```")
    task_dict = wb.task_center()
    if task_dict['status']:
        log.append(task_dict['task_dict']['msg'])
        logging.info(task_dict['task_dict']['msg'])
    else:
        log.append(task_dict['task_res.text'])
        logging.info(task_dict['task_res.text'])
    log.append("```")
    wb.server_push(sckey, "\n".join(log))
```



### 🚧使用步骤

1. 获取cookie
   - Chrome登录[微博手机版](https://m.weibo.cn/)
   - F12抓取任意请求获取cookie字段
2. 获取s参数
   - 有Root手机下载Httpcanary抓取微博国际版app的签到请求包，就在请求url中
   - 使用mumu模拟器+Fiddle或mumu模拟器+Httpcanary抓取微博国际版app的签到请求包
3. 获取sckey
   - 进入[Server酱](https://sc.ftqq.com/3.version)
   - GIthub账号登陆并绑定微信获取sckey



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

**🌙2020/11/16：优化部分接口，增加登录接口、批量取关、批量删除微博等等**

**🎭2020/09/19：取消GitHub Actions，因为使用国外IP(或者说是异地请求)微博很容易异常**

**💥2020/09/10：增加微博超话APP登录积分获取接口，该接口GitHub Actions上暂无法成功**

**💗2020/09/08：增加微博评论解析、酷推等接口，更新README文档，代码重构**

**🎲2020/09/04：增加删除微博、删除评论、取消点赞接口，优化喻言超话评论**

**🏳2020/08/31：增加打榜382023账户异常的判断**

**🎉2020/08/29：增加喻言超话评论，增加任务中心积分显示**

**💤2020/08/28：增加打榜计划，优化微信推送格式**

**🌈2020/08/27：第一次提交**



### ⚡更新计划
1. 增加更多关于微博超话的接口，方便自己有时间维护升级我的 [微博超话工具](https://reajason.top/2020/10/19/WeiBoSuperTopicsTool/)
2. 写一个简易的接口文档，方便有兴趣自己编写工具的人参考（自己抓接口其实更好玩）
3. ......



### 🚁成果图



<img src="https://cdn.jsdelivr.net/gh/ReaJason/WeiBo_SuperTopics/Pictures/result.jpg" width = "500" div align=center />



### 🔥致谢

感谢[wxy1343/weibo_points](https://github.com/wxy1343/weibo_points)的接口参考