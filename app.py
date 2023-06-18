import os
import yaml
import re
import requests
from flask import Flask, render_template, send_from_directory
from utils.mcclient import QueryClient

app = Flask(__name__)
app.template_folder = 'templates'

with open('config.yml', encoding='utf8') as f:
    conf = yaml.load(f.read(), Loader=yaml.FullLoader)

mc_show_info = conf['server']['show-info']
mc_host = conf['server']['host']
mc_port = conf['server']['port']
mc_query = conf['server']['query']
mc_name = conf['server']['name']
mc_logo = conf['server']['logo']
mc_preview_title = conf['server']['preview']['title']
mc_preview_descr = conf['server']['preview']['descr']
mc_preview_images = conf['server']['preview']['images']
join_content = conf['server']['contact']['content']

host = conf['web']['host']
port = conf['web']['port']
# for Minecraft Java servers (needs to be enabled on the server)
query_client = QueryClient(mc_host, port=mc_query)

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
        res = query_client.get_status()
    except TimeoutError:
        offline = True
    if not offline:
        cleaned_motd = re.sub(r'§[a-f0-9klmnor]', '', res.motd)
        cleaned_motd = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_motd)
        player_list = []
        for player in res.players.list:
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
                            current = len(res.players.list),
                            maxp = res.players.max,
                            logo = mc_logo,
                            preview_title = mc_preview_title,
                            preview_descr = mc_preview_descr,
                            preview_images = mc_preview_images,
                            join_content = join_content,
                            player_list = player_list,
                            offline = offline)
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