# CraftMon

就是我之前那个[服务器展示面板 Minecraft-Server-Status](https://github.com/GamerNoTitle/Minecraft-Server-Status)的重置版啦，其实我本身不怎么会用 PHP 的，那个版本大部分的东西都是拿了别人现成的轮子做的，到头来维护真的很很很狠很麻烦，所以就用我熟悉的 Python 做了一个 flask 版的

## 配置程序

首先你得装好 Python（请使用 Python3.10 及以上），然后用 pip 安装一下轮子

```shell
pip install -r requirements.txt
```

然后修改`config.yml`里面的内容，里面应该长这样（有我的示例）

```yaml
web:
  host: 0.0.0.0
  port: 8080

server:
  # 如果你想显示你的服务器连接信息的话，就把下面这个show-info改为true，否则保持不动
  show-info: false
  # 服务器名字
  name: EMUnion
  # 服务器地址
  host: mc.bili33.top
  # 这个port只是拿来展示的，如果上面关掉了的话可以不动它
  port: 25565
  # 查询信息实际用的是query这个端口，在server.properties里面有，需要自行设置端口并且把这个功能打开
  query: 10125
  logo: https://cdn.bilicdn.tk/gh/Vikutorika/newassets@master/img/Miscellaneous/EMUnion.jpg
  preview: # 服务器预览部分
    title: 嘿！这里是EMUnion
    # 预览界面的描述，可以用html书写
    descr: |
      EMUnion是一个生电服务器，里面有形形色色的玩家们，我们有超级运维<a href="https://bili33.top" target="_blank"><u>GamerNoTitle</u></a>
      和<a href="https://noionion.top" target="_blank"><u>2x_ercha</u></a>，还有我们的物理腐竹ttss，此外，我们还有各位生电服的大佬（划掉）再次坐镇，欢迎大家的加入！
    images: # 服务器的预览图片，你需要把文件丢在images文件夹里面，然后复制文件名在这里
      - 2023-01-21_13.58.07.png
      - 2023-06-18_17.58.00.png
      - 2023-06-18_17.58.11.png
      - 2023-06-18_17.58.33.png
      - 2023-06-18_17.59.35.png
      - 2023-06-18_18.00.16.png
      - 2023-06-18_18.00.23.png
      - 2023-06-18_18.00.40.png
      - 2023-06-18_18.01.21.png
      - 2023-06-18_18.04.46.png
      - 2023-06-18_18.05.45.png
      - 2023-06-18_18.06.08.png
      - 2023-06-18_18.06.24.png
      - 2023-06-18_18.08.58.png
      - 2023-06-18_18.09.12.png
      - 2023-06-18_18.12.54.png
      - 2023-06-18_18.13.38.png
      - 2023-06-18_18.14.08.png
      - 2023-06-18_18.14.13.png
      - 2023-06-18_18.15.52.png
  contact:
    content: | # 这里是加入我们页面的内容，请使用html书写（要不然会很丑）
      <a href="http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=zQHSKERVton9xMCctGiSLWAj8S48-BFL&authKey=mbWJxC1uydGIUNeRoiTJamDF1eQbNxT18TvKQbark1Vd2qEcPH5kt%2FW6ZsHFdXaZ&noverify=0&group_code=519383932" target="_blank"><button>加入审核群</button></a>
```

只需要按照里面的提示修改就行了，修改完了用以下命令启动

```shell
python app.py
```

然后你就可以访问`http://127.0.0.1:8080`来查看网站了！

## 预览图

![](http://cdn.bili33.top/gh/Vikutorika/newassets@master/img/Github/CraftMon/msedge-20230618-184807.png)

![](http://cdn.bili33.top/gh/Vikutorika/newassets@master/img/Github/CraftMon/msedge-20230618-184855.png)

![](http://cdn.bili33.top/gh/Vikutorika/newassets@master/img/Github/CraftMon/msedge-20230618-184918.png)
