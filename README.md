# hoshino-pjsk-plugin<br>
因为频道里的pjsk查询没有开源 翻了翻pjsk信息网站发现有api于是决定自己做<br> 
指令 `/pjsk绑定+pjskID`可以绑定发送者的qq与pjsk，<br>
指令`/pjsk进度`可以查询master难度的完成情况<br>
指令`/pjskpf`可以查询pjsk个人档案（目前只有各难度的clear、FC、AP完成情况，以及各个角色等级）<br>
指令`/sk`可以查询个人当前活动分数和上一级的分数线<br>

python初学者 第一次写hoshino的插件<br>
所以你将可以在py文件中看到：屎山、多段重复代码、莫名其妙的变量名称……<br>


## 部署方法<br>
1.git本项目 将文件夹放在\hoshino\modulus\下<br>
2.在\config\_bot_.py中加入“hoshino-pjsk-plugin”，<br>
3.在pjskinfo.py中修改load_path的路径（指向你放本插件的目录）<br>
例load_path = "C:\\Users\\Administrater\\Desktop\\haru-bot-setup\\hoshino\\modules\\hoshino-pjsk-plugin"<br>
4.重启并运行hoshino<br>

## 未来功能<br>
谱面查询<br>
歌曲查询<br>
猜歌（谱面猜歌，曲绘猜歌，歌曲切片猜歌）<br>
按歌曲别称检索<br>
（向频道的unibot靠拢）<br>

## 已知问题<br>
文件中字体均不支持中日文字混用因此可能会出现下面这种情况<br>
> 
> ![](image/哈哈.png)
（如果有佬……）
