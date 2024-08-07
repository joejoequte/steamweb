import os
from whatisthis import t683531

# 从环境变量读取 AppID
app_id = int(os.getenv('APP_ID', '0'))

if app_id == 0:
    raise ValueError("APP_ID 环境变量未设置或无效")

if __name__ == '__main__':
    apps = [app_id]
    for el in apps:
        print(f"\n======================={el}==============================\n")
        t683531(el)
