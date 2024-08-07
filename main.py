from whatisthis import t683531

if __name__ == '__main__':
    apps = [
        int(input("请输入AppID："))
    ]
    for el in apps:
        print(f"\n======================={el}==============================\n")
        t683531(el)
