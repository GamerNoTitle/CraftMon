import os
import yaml
import re
import requests
from flask import Flask, render_template, send_from_directory
from mcstatus.server import JavaServer

app = Flask(__name__)
app.template_folder = 'templates'

with open('config.yml', encoding='utf8') as f:
    conf = yaml.load(f.read(), Loader=yaml.FullLoader)

mc_show_info = conf['server']['show-info']
mc_host = conf['server']['host']
mc_port = conf['server']['port']
mc_name = conf['server']['name']
mc_logo = conf['server']['logo']
mc_preview_title = conf['server']['preview']['title']
mc_preview_descr = conf['server']['preview']['descr']
mc_preview_images = conf['server']['preview']['images']
join_content = conf['server']['contact']['content']

host = conf['web']['host']
port = conf['web']['port']

def parse_motd(motd):
    # Minecraft MOTD 颜色代码与 HTML 样式的映射
    color_codes = {
        '0': 'color: #000000;',  # 黑色
        '1': 'color: #0000AA;',  # 深蓝
        '2': 'color: #00AA00;',  # 深绿
        '3': 'color: #00AAAA;',  # 青色
        '4': 'color: #AA0000;',  # 深红
        '5': 'color: #AA00AA;',  # 紫色
        '6': 'color: #FFAA00;',  # 金色
        '7': 'color: #AAAAAA;',  # 灰色
        '8': 'color: #555555;',  # 深灰
        '9': 'color: #5555FF;',  # 蓝色
        'a': 'color: #55FF55;',  # 绿色
        'b': 'color: #55FFFF;',  # 浅蓝
        'c': 'color: #FF5555;',  # 红色
        'd': 'color: #FF55FF;',  # 粉色
        'e': 'color: #FFFF55;',  # 黄色
        'f': 'color: #FFFFFF;',  # 白色
    }

    # 样式代码
    style_codes = {
        'l': 'font-weight: bold;',  # 粗体
        'o': 'font-style: italic;',  # 斜体
        'n': 'text-decoration: underline;',  # 下划线
        'm': 'text-decoration: line-through;',  # 删除线
        'r': '',  # 重置样式
    }

    # 将 MOTD 转换为 HTML
    html_output = ""
    current_styles = []
    i = 0

    while i < len(motd):
        if motd[i] == '§' and i + 1 < len(motd):
            code = motd[i + 1]
            i += 2

            if code in color_codes:
                current_styles = [color_codes[code]]
            elif code in style_codes:
                if code == 'r':
                    current_styles = []  # 重置所有样式
                else:
                    current_styles.append(style_codes[code])
            continue

        # 添加 HTML span 包裹文字
        if current_styles:
            html_output += f"<span style=\"{' '.join(current_styles)}\">{motd[i]}</span>"
        else:
            html_output += motd[i]

        i += 1

    return html_output


@ app.route('/assets/<path:filename>')
def serve_static(filename):
    return send_from_directory('assets', filename)

@ app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('images', filename)

@ app.route('/')
def home():
    offline = False
    try:
        server = JavaServer.lookup(f"{mc_host}:{mc_port}")
        status = server.status()
        players = server.query().players.names
        # return {
        #     "version": status.version.name,
        #     "protocol_version": status.version.protocol,
        #     "players": players,
        #     "players_online": status.players.online,
        #     "players_max": status.players.max,
        #     "motd": status.description,
        #     "latency": round(status.latency, 2),
        #     "online": True,
        #     "error": False,
        #     "msg": "success"
        # }
    except (TimeoutError, ConnectionRefusedError):
        offline = True
    if not offline:
        cleaned_motd = parse_motd(status.description)
        title = status.motd.to_plain().replace("\n", " ")
        # cleaned_motd = re.sub(r'§[a-f0-9klmnor]', '', str(status.description))
        # cleaned_motd = re.sub(r'[^a-zA-Z0-9\s]', '', str(cleaned_motd))
        player_list = []
        for player in players:
            try:
                data = requests.get(f'https://playerdb.co/api/player/minecraft/{player}', timeout=5).json()
                if data['success']:
                    uuid = data['data']['player']['id']
                    img = f'https://crafatar.com/renders/head/{uuid}'
                else:
                    img = 'https://crafatar.com/renders/head/aaaaaaaa-cf6b-4485-bef9-3957e7b7f509'
            except requests.exceptions.ReadTimeout:
                img = 'https://crafatar.com/renders/head/aaaaaaaa-cf6b-4485-bef9-3957e7b7f509'
            player_list.append({'name': player, 'img': img})
        return render_template('index.html',
                            name = mc_name,
                            host = mc_host,
                            port = mc_port,
                            show_info = mc_show_info,
                            motd = cleaned_motd,
                            current = len(players),
                            maxp = status.players.max,
                            logo = mc_logo,
                            preview_title = mc_preview_title,
                            preview_descr = mc_preview_descr,
                            preview_images = mc_preview_images,
                            join_content = join_content,
                            player_list = player_list,
                            offline = offline,
                            title = title)
    else:
        return render_template('index.html',
                            name = mc_name,
                            host = mc_host,
                            port = mc_port,
                            show_info = mc_show_info,
                            logo = mc_logo,
                            preview_title = mc_preview_title,
                            preview_descr = mc_preview_descr,
                            preview_images = mc_preview_images,
                            join_content = join_content,
                            offline = offline)
        

if __name__ == '__main__':
    app.run(host, port)