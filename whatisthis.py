import requests
import re
from urllib.parse import quote
from html.parser import unescape
from bs4 import BeautifulSoup
import time

def text_filter(element, link_with=''):
    text = ''
    for el in element.descendants:
        if 'NavigableString' in str(type(el)):
            text += str(el).replace('\n', '').replace('\r', '').strip() + link_with
    if link_with != '':
        return text[:-len(link_with)]
    else:
        return text

proxies = {
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809',
}


def t683531(appid):
    if not str(appid).isdigit():
        print('请输入有效的appid')
        return None
    params = {'appids': appid, 'cc': 'cn', 'l': 'schinese'}
    data = requests.get('https://store.steampowered.com/api/appdetails',
                        params=params,
                        proxies=proxies).json()[str(appid)]
    if data['success'] != 1:
        params['cc'] = 'us'
        data = requests.get('https://store.steampowered.com/api/appdetails',
                            params=params,
                            proxies=proxies).json()[str(appid)]
        while data['success'] != 1:
            params['cc'] = input('此游戏在当前区域锁区（默认为cn及us），请输入有效cc区域代号后按回车，以继续获取：')
            data = requests.get(
                'https://store.steampowered.com/api/appdetails',
                params=params,
                proxies=proxies).json()[str(appid)]
    data = data['data']
    genres = ''.join([el['description'] for el in data['genres']])
    name = data['name']
    is_free = data['is_free']
    date = unescape(data['release_date']['date'])
    today = time.strftime("%Y年%m月%d日", time.localtime(int(time.time())))
    if data['release_date']['coming_soon']:
        release_date = f"将于{date}在steam上线[/k0]"
        summary = f"{genres}游戏《{name}》于{today}在Steam商店上架，计划于{date}上线"
    else:
        if not is_free:
            release_date = f"已于{date}发售"
            final_formatted = data['price_overview']['final_formatted'].replace(' ', '')
            discount_percent = data['price_overview']['discount_percent']
            release_date += f" -{discount_percent}%/{final_formatted}"
            summary = f"{genres}游戏《{name}》于{today}在Steam商店上架，已于{date}发售。"
        else:
            release_date = f"已于{date}免费上线"
            summary = f"免费{genres}游戏《{name}》已于{date}在Steam商店上架"
    
    title = f"[k0]{genres}游戏《{name}》{release_date}\n\n{summary}"
    print(title)

    header_image = data['header_image']
    print(
        f"[img]{header_image}[/img]\n[url=https://store.steampowered.com/app/{appid}]{name}[/url]\n[sframe]{appid}[/sframe]\n\n"
    )

    about_the_game = BeautifulSoup(data['about_the_game'], 'html.parser').get_text()
    p = re.compile('\[size=167\](.*?\[\/size\])')
    about_the_game = p.sub(r'\n[size=4]\1\n', about_the_game)
    print(
        f"[k1]关于此游戏[/k1]\n[quote]{about_the_game}[/quote]"
    )

    screenshots, movies = '', ''
    if 'screenshots' in data.keys():
        screenshots = '\n'.join(
            [f"[img]{el['path_full']}[/img]" for el in data['screenshots']])
    if 'movies' in data.keys():
        movies = '\n'.join(
            [f"[media]{el['mp4']['max']}[/media]" for el in data['movies']])
    print(
        f"[collapse=商店宣传]\n{movies}\n{screenshots}\n[/collapse]"
    )

    header = {
        'Connection':
        'keep-alive',
        'Cookie':
        'wants_mature_content=1; timezoneOffset=28800,0; Steam_Language=schinese; steamCountry=US; mature_content=1; birthtime=-40073356799;',
        'Host':
        'store.steampowered.com',
        'Upgrade-Insecure-Requests':
        '1',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    r1 = requests.get(f"https://store.steampowered.com/app/{appid}",
                      params=params,
                      proxies=proxies,
                      headers=header)
    soup = BeautifulSoup(r1.text, 'html.parser')
    params['l'] = 'english'
    data_eng = requests.get('https://store.steampowered.com/api/appdetails',
                            params=params,
                            proxies=proxies).json()[str(appid)]['data']

    # category
    c_table = '[collapse=商店信息][table=200,#101822]\n'
    for tr in soup.select('div#category_block > div'):
        if tr.get('class') and tr.get('class')[0] == 'game_area_details_specs':
            icon = f"[img=26,16]{tr.select_one('img').get('src')}[/img]"
            cata = tr.select_one('a.name').string
            if tr.select_one('img').get('src').split('/')[-1] in [
                    'ico_learning_about_game.png', 'ico_info.png'
            ]:
                cata = f"[color=#acb2b8]{text_filter(tr.select_one('a.name'))}[/color]"
            else:
                cata_link = tr.select_one('a').get('href')
                cata = f"[url={cata_link}]{cata}[/url]"
        else:
            icon = ''
            cata = f"[color=#acb2b8]{text_filter(tr)}[/color]"
        temp_line = f"[tr][td][align=center]{icon}[/align][/td][td]{cata}[/td][/tr]\n"
        c_table += temp_line
    c_table += '[/table]'
    print(c_table)

    language = []
    l_table = '[table=280,#121b25]\n'
    for tr in soup.select_one('table.game_language_options').select('tr'):
        temp_line = []
        if language == []:
            for th in tr.select('th'):
                temp_line.append(text_filter(th))
        else:
            for td in tr.select('td'):
                temp_line.append(text_filter(td))
        language.append(temp_line)
    for idx, line in enumerate(language):
        temp_line = '[tr]'
        if len(line) == 2:
            temp_line += f"[td][color=#61686d]{line[0].strip()}[/color][/td][td=3,1][color=#61686d][align=center]{line[1].strip()}[/align][/color][/td]"
        else:
            for i, cell in enumerate(line):
                if i == 0:
                    color = '#8f98a0'
                    temp_line += f"[td][color={color}]{cell.strip()}[/color][/td]"
                else:
                    color = '#67c1f5'
                    temp_line += f"[td][color={color}][align=center]{cell.strip()}[/align][/color][/td]"
        temp_line += '[/tr]\n'
        l_table += temp_line
    l_table += '[/table]'
    print(l_table)

    # achievements
    if 'achievements' in data.keys():
        achievements = data['achievements']
        total = achievements['total']
        show = 4
        if len(achievements['highlighted']) < 4:
            show = len(achievements['highlighted'])
        a_table = f"[table=10,#101720][tr][td={show},1][url=https://steamcommunity.com/stats/{appid}/achievements][color=#8f98a0]包括 {total} 项 Steam 成就[/color][/url][/td][/tr]\n"
        a_table += f"[tr]"
        for i, el in enumerate(achievements['highlighted']):
            if i <= 3: a_table += f"[td][img=64,64]{el['path']}[/img][/td]"
        a_table += '[/tr]\n[/table]'
        print(a_table)

    # requirements
    keys = {
        'pc_requirements': ['Windows', len(data['pc_requirements'])],
        'linux_requirements':
        ['SteamOS + Linux', len(data['linux_requirements'])],
        'mac_requirements': ['Mac OS X',
                             len(data['mac_requirements'])]
    }
    width = max([el[1] for el in keys.values()])
    r_table = f"[table=450,#1b2838]\n[tr][td={width},1][color=#ffffff]系统需求[/color][/td][/tr]\n"
    if width != 0:
        for k, v in keys.items():
            if v[1] != 0:
                r_table += f"[tr][td={v[1]},1][color=#67c1f5]{v[0]}[/color][/td][/tr]\n[tr]".replace(
                    '=1,1', '')
                for el in data[k].values():
                    r_table += f"[td][color=#acb2b8]{el}[/color][/td]"
                r_table += '[/tr]\n'
        r_table += '[/table]'
        print(r_table)

    # underlined_links
    game_genres = [[el['id'], el['description']] for el in data['genres']]
    game_genres_eng = [[el['id'], el['description']]
                       for el in data_eng['genres']]
    genres = ', '.join([
        f"[url=https://store.steampowered.com/genre/{game_genres_eng[idx][1]}]{el[1]}[/url]"
        for idx, el in enumerate(game_genres)
    ])
    developers = ', '.join([
        f"[url=https://store.steampowered.com/search/?developer={quote(el, safe='/', encoding=None, errors=None)}]{el}[/url]"
        for el in data['developers']
    ])
    publishers = ', '.join([
        f"[url=https://store.steampowered.com/search/?publisher={quote(el, safe='/', encoding=None, errors=None)}]{el}[/url]"
        for el in data['publishers']
    ])
    u_table = f"[table=250,#101821]\n[tr][td][color=#556772]名称：[/color][color=#8f98a0]{name}[/color]\n" \
              f"[color=#556772]类型：[/color]{genres}\n" \
              f"[color=#556772]开发商：[/color]{developers}\n" \
              f"[color=#556772]发行商：[/color]{publishers}\n" \
              f"[color=#556772]发行日期：[/color][color=#8f98a0]{date}[/color][/td][/tr]"
    u_data = soup.select_one('div.underlined_links').select(
        'div.details_block')[1].children
    for el in list(u_data):
        try:
            href = el.get('href')
            text = text_filter(el)
            if href != None:
                temp_line = f"[tr][td][url={href}]{text}[/url][/td][/tr]\n"
                u_table += temp_line
        except:
            pass
    u_table += '[/table][/collapse]'
    print(u_table)
