import hashlib
import time
import requests


class SmsClient:
    def __init__(self, url, user_id, password):
        # 如果url以/结尾，则自动去除
        if url.endswith('/'):
            self.url = url = url[:-1]
        else:
            self.url = url
        self.url = url + '/domsg/smsSendJson.do'
        self.user_id = user_id
        self.password = password

    def send(self, mobiles: list,
             content: str,
             ext: str = None,
             msg_id: str = None,
             encode_type: str = None):
        try:
            timestamp = str(int(time.time() * 1000))
            md5_str = self.password + self.user_id + timestamp
            md5 = hashlib.md5(md5_str.encode('utf-8')).hexdigest().upper()
            data = {
                'userid': self.user_id,
                'pwd': md5,
                'timestamp': timestamp,
                'mobile': ",".join(mobiles),
                'content': content,
                'ext': ext if ext else '',
                'msgid': msg_id if msg_id else '',
                'encodetype': encode_type if encode_type else ''
            }
            headers = {'Content-Type': 'application/json'}
            # 发送POST请求
            response = requests.post(self.url, json=data, headers=headers)
            if response.status_code != 200:
                return {"msg": "请求失败:", "code": str(response.status_code)}
            return response.json()
        except Exception as e:
            return {"msg": "客户端请求失败: " + str(e), "code": "-400"}
