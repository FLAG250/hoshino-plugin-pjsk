# hoshino-pjsk-plugin
因为频道里的pjsk查询没有开源 翻了翻pjsk信息网站发现有api于是决定自己做<br> 
指令 `/pjsk绑定+pjskID`可以绑定发送者的qq与pjsk，<br>
指令`/pjsk进度`可以查询master难度的完成情况
指令`/pjskpf`可以查询pjsk个人档案（目前只有各难度的clear、FC、AP完成情况，以及各个角色等级）
指令`/sk`可以查询个人当前活动分数和上一级的分数线<br>

本人python初学者 也是第一次写hoshino的插件 所以你将可以在py文件中看到：屎山、多段重复代码、莫名其妙的变量名称……


## 部署方法<br>
1.git本项目 将文件夹放在\hoshino\modulus\下<br>
2.在\config\_bot_.py中加入“hoshino-pjsk-plugin”，
3.在pjskinfo.py中修改load_path的路径（指向你放本插件的目录）
例load_path = "C:\\Users\\Administrater\\Desktop\\haru-bot-setup\\hoshino\\modules\\hoshino-pjsk-plugin"<br>
4.重启并运行hoshino

