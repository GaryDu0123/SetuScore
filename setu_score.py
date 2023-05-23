import json
import os
import re
import requests
from sqlitedict import SqliteDict

from hoshino import aiorequests
from hoshino import R, Service
from hoshino.typing import CQEvent, MessageSegment
from typing import Dict
from hoshino.config.setu_score import API_KEY, SECRET_KEY

sv = Service('色图打分', enable_on_default=False, bundle='色图打分', help_='''色图打分''')

# ======================================== #
host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}'
response = requests.get(host)
access_token = response.json()["access_token"]
request_url = "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined"
request_url = request_url + "?access_token=" + access_token
headers = {'content-type': 'application/x-www-form-urlencoded'}
FILE_PATH = os.path.dirname(__file__)


async def porn_pic_index(url):
    params = {"imgUrl": url}
    data: Dict = {}
    resp = await aiorequests.post(request_url, data=params, headers=headers)
    if resp.ok:
        data = await resp.json()
    try:
        if not data:
            return {'code': -1, 'msg': 'API Error'}
        if "error_code" in data:
            return {'code': data['error_code'], 'msg': data['error_msg']}
        try:
            data = data['data']
        except Exception:
            return {'code': -1, 'msg': '请检查策略组中疑似区间是否拉满'}
        porn_0 = 0
        porn_1 = 0
        porn_2 = 0
        for c in data:
            # 由于百度的图片审核经常给出极低分,所以不合规项置信度*500后为分数
            if c['type'] == 1 and c['subType'] == 0:
                porn_0 = int(c['probability'] * 500)
            elif c['type'] == 1 and c['subType'] == 1:
                porn_1 = int(c['probability'] * 500)
            elif c['type'] == 1 and c['subType'] == 10:
                porn_2 = int(c['probability'] * 500)
        return {'code': 0, 'msg': 'Success', 'value': max(porn_0, porn_1, porn_2)}
    except FileNotFoundError:
        return {'code': -1, 'msg': 'File not found'}


async def get_database() -> SqliteDict:
    # 创建目录
    img_path = os.path.join(FILE_PATH, 'img/')
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    db_path = os.path.join(FILE_PATH, 'data.sqlite')
    # 替换默认的pickle为josn的形式读写数据库
    db = SqliteDict(db_path, encode=json.dumps, decode=json.loads, autocommit=True)
    return db


class PicListener:
    def __init__(self):
        self.on = {}

    def allow_search(self, gid):
        return self.on.get(gid, True)

    def turn_on(self, gid):
        self.on[gid] = False

    def turn_off(self, gid):
        self.on[gid] = True


pls = PicListener()


@sv.on_message('group')
async def picmessage(bot, ev: CQEvent):
    msg_id = ev.message_id
    if not pls.allow_search(ev.group_id):
        return

    ret = re.search(r"\[CQ:image,file=(.*?),((?!subType=1).)*?,url=(.*?)]", str(ev.message))
    if not ret:
        return
    pls.turn_on(ev.group_id)
    file = ret.group(1)
    url = ret.group(3)  # 这里的组索引变为3，因为我们添加了一个新的组来排除subType=1
    db = await get_database()
    if file in db:
        score = db[file]
    else:
        # ↓如果你想下载图片到本地的话去掉注释↓
        # 下载路径是你的go-cqhttp/data/cache
        # await get_bot().get_image(file=file)
        porn = await porn_pic_index(url)
        if porn['code'] == 0:
            score = porn['value']
            db[file] = score
        else:
            code = porn['code']
            err = porn['msg']
            await bot.send(ev, f'错误:{code}\n{err}')
            return

    # Store score in the database
    if score > 450:
        await bot.send(ev, f'{score} 好涩~不许给盐看!!!')
    elif score > 400:
        await bot.send(ev, f'{score} 不要太过分了!!')
    elif score > 350:
        await bot.send(ev, f'{score} 啊啊啊(闭眼)')
    elif score > 300:
        await bot.send(ev, f'{score} wwwww!')
    elif score > 250:
        await bot.send(ev, f'{score} wwwww?!')
    elif score > 200:
        await bot.send(ev, f'{score} 这是, 色图?!')
    pls.turn_off(ev.group_id)
