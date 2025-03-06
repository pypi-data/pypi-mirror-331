"""
测试sms_client
"""
from sms.sms_client import SmsClient

if __name__ == '__main__':
    client = SmsClient('https://***:8089', '100005', 'admin@110')
    print(client.send(['187****8433'], '【凌渡科技】验证码是0702,5分钟有效'))