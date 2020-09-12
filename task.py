from api import WeiBo


def run():
    cookie = input()
    s = input()
    pick = input()
    sckey = input()
    wei = WeiBo(cookie)
    wei.daily_task(s, pick, sckey)


if __name__ == '__main__':
    run()
