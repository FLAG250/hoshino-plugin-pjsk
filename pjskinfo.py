import json, base64, time
import requests as req
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import re
from io import BytesIO
import codecs

from hoshino.typing import CQEvent, MessageSegment
from hoshino import Service, priv, config

import asyncio

sv = Service(
    name = 'pjsk信息查询',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.SUPERUSER, #管理权限
    visible = False, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    )
    

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
url_getmD = 'https://musics.pjsekai.moe/musicDifficulties.json'
url_getmc = 'https://musics.pjsekai.moe/musics.json'
url_e_data = 'https://database.pjsekai.moe/events.json'
color={"ap":"#d89aef","fc":"#ef8cee","clr":"#f0d873","all":"#6be1d9"}
load_path = os.path.dirname(__file__)     #更改为自动获取

def data_req(url):  #现场请求相关数据，耗时较长，但是数据永远是最新的
    temp_res = req.get(url, headers = headers)
    re = json.loads(temp_res.text)
    return re

def a_check(uid,account): #bot, ev: CQEvent
    n_a = len(account)
    for a in range(n_a):
        if uid != account[a]["qqid"]:
            continue
        else:
            return False
    else:
        return True

@sv.on_prefix("/pjsk绑定")
async def reg(bot, ev: CQEvent):
    ppid = ev.message.extract_plain_text().strip()
    try:
        pid = int(ppid)
        uid = ev.user_id
        print(pid)
        if isinstance(pid,int) and pid > 1000000000000000:       #待优化
            with open(load_path+f"\\account.json","r") as f:
                account = json.load(f)
            n_a = len(account)

            if a_check(uid,account):
                indexdata = []
                for a in range(n_a):
                    uuid = account[a]["qqid"]
                    ppid = account[a]["pjskid"]
                    account_dict = {'qqid' : uuid,
                                    'pjskid' : ppid}
                    indexdata.append(account_dict)
                account_dict = {'qqid' : uid,
                                'pjskid' : int(pid)}
                indexdata.append(account_dict)

                with open (load_path+'\\account.json', 'w', encoding='utf8') as f:
                    json.dump(indexdata, f,indent =2, ensure_ascii=False)
                
                await bot.send(ev,f"绑定完成！",at_sender = True)
            else:
                await bot.send(ev,f"你已经绑定过！",at_sender = True)
        else:
            await bot.send(ev,f"UID格式错误",at_sender = True)
    except:
        await bot.send(ev,f"绑定发生错误",at_sender = True)






async def lg(user_id):  
    uid = user_id

    with open(load_path+f'\\account.json', 'r') as fff:
        udata = json.load(fff)
        if not a_check(uid,udata):
            for a in udata:
                if  uid == a['qqid']:
                    return a['pjskid']
                else:
                    continue
        else:
            return  0




async def getLeaderIcon(data1):
    leaderId = data1['userDecks'][0]["leader"]
    for  level in data1["userCards"]:
        if leaderId == level["cardId"]:
            card_type = level["defaultImage"]
            break
    getCd = req.get('https://database.pjsekai.moe/cards.json')
    cards_infomation = json.loads(getCd.text)
    for sc in cards_infomation:
        if leaderId == sc["id"]:
            if card_type == 'original':
                url = f'https://asset.pjsekai.moe/startapp/thumbnail/chara/{sc["assetbundleName"]}_normal.png'
            elif card_type == "special_training":
                url = f'https://asset.pjsekai.moe/startapp/thumbnail/chara/{sc["assetbundleName"]}_after_training.png'
            l_icon = req.get(url)
            return l_icon

    

async def countFlg(_list,TAG,difficulty,data1):
    a_count = 0
    for result in data1['userMusicResults']:
            if result['musicDifficulty'] == difficulty:
                if result[TAG] == True and result['musicId'] not in _list:
                    a_count = a_count + 1
                    _list.append(result['musicId'])
    return _list,a_count


async def countClear(_list,difficulty,data1):
    a_count = 0
    for result in data1['userMusicResults']:
            if result['musicDifficulty'] == difficulty:
                if result['fullComboFlg'] == True and result['musicId'] not in _list:
                    a_count = a_count + 1
                    _list.append(result['musicId'])
                if result['playResult'] == 'clear' and result['musicId'] not in _list:
                    a_count = a_count + 1
                    _list.append(result['musicId'])
    for a in _list:
        if _list.count(a) >= 2:
            a_count = account - _list.count(a) + 1
    return _list,a_count

@sv.on_prefix("/pjskpf")
async def pj_profileGet(bot,ev:CQEvent):
    #逮捕
    uid = ev.user_id
    userID = await lg(uid)

    selection = 0
    
    for i in ev.message:
        if i.type == 'at':
            uid = int(i.data['qq'])
            userID = await lg(uid)
            break   

    _uID = ev.message.extract_plain_text().strip()
    if _uID != "":
        _userID = int(_uID)
        if isinstance(_userID,int) and _userID > 1000000000000000:
            userID = _userID
            selection = 1
        else:
            return await bot.send(ev,f'UID格式错误')

     
    
    if userID == 0:
        await bot.send(ev,f"没有绑定捏\n输入“/pjsk绑定+pjskID”来绑定吧~")
    else:
        try:
            url = f'https://api.pjsekai.moe/api/user/{userID}/profile'
            getdata = req.get(url)
            data1 = json.loads(getdata.text)


            dict_backup=[]
            difficulty = ['easy','normal','hard','expert','master']
            for tag in difficulty:
                count = 0
                fc_count = 0
                ap_count = 0
                clr_list = []
                fc_list = []
                ap_list = []
                fc_list,fc_count = await countFlg(fc_list,'fullComboFlg',tag,data1)
                ap_list,ap_count = await countFlg(ap_list,'fullPerfectFlg',tag,data1)
                clr_list,count = await countClear(clr_list,tag,data1)

                dict_backup.append({tag:{'fc':fc_count,'ap':ap_count,'clear':count}})
            #print(dict_backup)


            
            profile_image= Image.open(load_path+'\\test1.png')
            new_pimage = load_path+'\\pjprofile.png'

            if selection == 0:
                picon = Image.open(BytesIO((await get_usericon(f'{uid}')).content)) #####
            else:
                picon = Image.open(BytesIO((await getLeaderIcon(data1)).content))
            
            num_font = ImageFont.truetype(load_path+'\\CAT.TTF',size=40)
            name_font = ImageFont.truetype(load_path+'\\zzaw.ttf',size=80)
            rank_font = ImageFont.truetype(load_path+'\\CAT.TTF',size=36)
            word_font = ImageFont.truetype(load_path+'\\zzaw.ttf',size=32)
            draw = ImageDraw.Draw(profile_image)
            draw_icon = ImageDraw.Draw(picon)
            
            #防止部分玩家ID过大导致其以期望外的方式生成
            u = data1['user']['userGamedata']['name'].encode("utf-8")
            if len(u) < 18:
                draw.text((281,130),data1['user']['userGamedata']['name'],'#FFFFFF',font=name_font)
            else:
                name_font = ImageFont.truetype(load_path+'\\zzaw.ttf',size=48)
                draw.text((281,162),data1['user']['userGamedata']['name'],'#FFFFFF',font=name_font)

            draw.text((404,231),str(data1['user']['userGamedata']['rank']),'#FFFFFF',font=rank_font)



            
            async def measure(msg, font_size, img_width):
                i = 0
                l = len(msg)
                length = 0
                positions = []
                while i < l :
                    if re.search(r'[0-9a-zA-Z]', msg[i]):
                        length += font_size // 2
                    else:
                        length += font_size
                    if length >= img_width:
                        positions.append(i)
                        length = 0
                        i -= 1
                    i += 1
                return positions

            #个人简介
            
            word_text = Image.new('RGB', (654, 157), "#5b5b5b")
            
            draw1 = ImageDraw.Draw(word_text)
            

            msg = data1['userProfile']['word']
            positions = await measure(msg,32,700)
            str_list = list(msg)
            for pos in positions:
                str_list.insert(pos,'\n')
            msg = "".join(str_list)  

            draw1.text((0,0), msg, "#FFFFFF", font=word_font)
            profile_image.paste(word_text, (103,307))
            

            def draw_musicsCompleted():
                x = 0
                for tag in difficulty:
                    for pdata in dict_backup[x]:
                        y = 0
                        for ptag in ['clear','fc','ap']:
                            draw.text((140 + x * 128,580 + y * 128),str(dict_backup[x][pdata][ptag]),'#FFFFFF',font=num_font)
                            y = y + 1
                    x = x + 1
            
            def characterdataGet():
                for i in data1['userCharacters']:
                    if i["characterId"] % 4 == 0:
                        x = 960 + (165 * 3)
                        y = 350 + (107 * (((i["characterId"])// 4)-1))
                        if i["characterId"] > 20:
                            y = 130 + (107 * ((((i["characterId"])-20)// 4)-1))
                    else:
                        x = 960 + (165 * ((((i["characterId"])) % 4)-1))
                        y = 350 + (107 * (((i["characterId"])//4)))
                        if i["characterId"] > 20:
                            y = 130 + (107 * ((((i["characterId"])-20)// 4)))
                    draw.text((x, y),str(i['characterRank']),"#000000",font=num_font)

            

            draw_musicsCompleted()
            characterdataGet()
            picon = picon.resize((177,177),Image.Resampling.LANCZOS)
            profile_image.paste(picon, (95,106))
            buf = BytesIO()
            profile_image.save(buf, format='PNG')
            base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}' #通过BytesIO发送图片，无需生成本地文件
            await bot.send(ev,f'[CQ:image,file={base64_str}]',at_sender = True)
        except:
            await bot.send(ev,f"api或服务器可能寄了 或者你这个小可爱填错别人ID 不然一般是不会出现意料之外的问题的！ \n请及时联系管理员看看发生什么事了")

def load_event_info(_data):
    i = -2
    close_time = int(_data[i]["closedAt"]/1000) 
    if time.time() > close_time: #说明倒数第二个活动已关闭，按最新的算
        i = -1
    return _data[i]['id'], _data[i]['name'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(_data[i]["aggregateAt"]/1000))),  _data[i]['eventType']
            
@sv.on_prefix("/sk")
async def event_rank(bot,ev:CQEvent):    
    uid = ev.user_id
    userid = await lg(uid)
    if userid == 0:
        await bot.send(ev,f"没有绑定捏\n输入“/pjsk绑定+pjskID”来绑定吧~")
    else:
        try:
            _data = data_req(url_e_data)
            event_id, event_name, event_end_time, e_type = load_event_info(_data)
            url1 = f'https://api.pjsekai.moe/api/user/%7Buser_id%7D/event/{event_id}/ranking?targetUserId={userid}'

            user_event_data = req.get(url1, headers=headers)
            _event_data = json.loads(user_event_data.text)
            try:
                user_event_rank = _event_data['rankings'][0]['rank']  #你的try嵌套错地方了，如果没打活动这里就取不到值了
                user_event_score = _event_data['rankings'][0]['score']  #所以生成消息那边嵌套的try实际没有用
            except:
                await bot.send(ev, '小可爱你还没打活动查什么呢', at_sender = True) 
                return  #利用return结束
            nearest_line = []
            event_line = [100, 200, 500,
                        1000, 2000, 5000,
                        10000, 20000, 50000,
                        100000, 200000, 500000,
                        1000000, 2000000, 5000000]

            for a in range(len(event_line)):
                if int(event_line[a]) >= user_event_rank:
                    if a != 0:
                        nearest_line.append(event_line[a-1])
                    nearest_line.append(event_line[a])
                    break
            else:
                nearest_line.append(event_line[-1])
                                
            msg = f"当前活动:{event_name}\n活动类型:{e_type}\n活动截止时间:{event_end_time}\n你的分数:{str(user_event_score)} rank#{str(user_event_rank)}\n最近的分数线:"
            for i in nearest_line:
                try:
                    url2 = f'https://api.pjsekai.moe/api/user/%7Buser_id%7D/event/{event_id}/ranking?targetRank={i}'
                    event_line_data = req.get(url2, headers=headers)
                    _event_line_data = json.loads(event_line_data.text)
                    msg += f"\nrank#{i} {str(_event_line_data['rankings'][0]['score'])}"
                except:
                    msg += f"\nrank#{i} 最近的分数线:暂无数据"

        except Exception as e:
            msg = f"发生错误，错误类型：{type(e)}\n请联系管理员"
            print(e)
        await bot.send(ev, msg, at_sender = True)    
    
def load_req_line(string:str):
    return string.replace('k', '000').replace('K', '000').replace('w', '0000').replace('W', '0000')
    
@sv.on_prefix('/pjsk档线')
async def event_line_score(bot, ev):
    try:
        req_line = load_req_line(ev.message.extract_plain_text().strip())
    except:
        req_line = 0
    try:
        _data = data_req(url_e_data)
        event_id, event_name, event_end_time, e_type = load_event_info(_data)
        
        #line_score = []
        if req_line ==0:
            event_line = [100, 200, 500,
                    1000, 2000, 5000,
                    10000, 20000, 50000,
                    100000, 200000, 500000, 1000000]
            event_line_msg = ['100', '200', '500',
                    '1k', '2k', '5k',
                    '1w', '2w', '5w',
                    '10w', '20w', '50w', '100w']
            index = 0
            msg = f'活动标题：{event_name}\n活动类型:{e_type}'
            for line in event_line:
                url2 = f'https://api.pjsekai.moe/api/user/%7Buser_id%7D/event/{event_id}/ranking?targetRank={line}'
                event_line_data = data_req(url2)
                try:
                    #line_score.append(str(event_line_data['rankings'][0]['score']))  #预留后期图像化
                    line_score = event_line_data['rankings'][0]['score']
                    msg += f'\n{event_line_msg[index]}线:{line_score}'
                except:
                    #line_score.append('暂无数据')
                    msg += f'\n{event_line_msg[index]}线:暂无数据'
                index += 1
        else:
            msg = f'活动标题：{event_name}\n活动类型:{e_type}'
            url2 = f'https://api.pjsekai.moe/api/user/%7Buser_id%7D/event/{event_id}/ranking?targetRank={req_line}'
            event_line_data = data_req(url2)
            try:
                line_score = event_line_data['rankings'][0]['score']
                msg += f'\n{req_line}线:{line_score}'
            except:
                msg += f'\n{req_line}线:暂无数据'
    except Exception as e:
        print(e)
        msg = f"发生错误，错误类型：{type(e)}\n请联系管理员"
        
    await bot.send(ev, msg, at_sender = True)  

async def pj_musicCompletedDataGet(uid,data1):
    difficulty = 'master'
    count = 0
    c_count = 0
    p_count = 0
    list1 = []
    list2 = []
    list3 = []
    list4 = []

    list1,c_count = await countFlg(list1,'fullComboFlg',difficulty,data1)
    list2,p_count = await countFlg(list2,'fullPerfectFlg',difficulty,data1)
    list4,count = await countClear(list4,difficulty,data1)

    _lv = data_req(url_getmD)
    allMusic = data_req(url_getmc)
    #按难度分类  
    for _ in allMusic:
            list3.append(_['id'])
    
    async def selectPlus(_list):
        lv_s = {26:0,27:0,28:0,29:0,30:0,31:0,32:0,33:0,34:0,35:0,36:0}
        for __lv in _lv:
            if __lv['musicDifficulty'] == difficulty and __lv['musicId'] in _list:
                lv_s[__lv['playLevel']] += 1
        return lv_s
    
    lv1 = await selectPlus(list1)
    lv2 = await selectPlus(list2)
    lv3 = await selectPlus(list3)
    lv4 = await selectPlus(list4)
    
    
    async def change(lv):
        re_lv1 = []
        in_dex ={}
        for i in range(26,37):
            a = lv[i]
            b = str(i)
            in_dex[f"{b}"] = a
            n_dex =in_dex
        re_lv1.append(n_dex)     
        return re_lv1   
    
    re_lv1 = await change(lv1) #fc
    re_lv2 = await change(lv2) #ap
    _all = await change(lv3) #all
    _clear = await change(lv4) #clear
    

    return _clear,_all,re_lv1,re_lv2

    
async def get_usericon(user):
        p_icon = req.get(f'https://q1.qlogo.cn/g?b=qq&nk={user}&s=640')
        return p_icon

@sv.on_prefix("/pjsk进度")
async def gen_pjsk_jindu_image(bot,ev:CQEvent):
    #逮捕
    uid = ev.user_id
    userID = await lg(uid)

    selection = 0
    
    for i in ev.message:
        if i.type == 'at':
            uid = int(i.data['qq'])
            userID = await lg(uid)
            break

    _uID = ev.message.extract_plain_text().strip()
    if _uID != "":
        _userID = int(_uID)
        if isinstance(_userID,int) and _userID > 1000000000000000:
            userID = _userID
            selection = 1
        else:
            return await bot.send(ev,f'UID格式错误')



    if userID == 0:
        await bot.send(ev,f"没有绑定捏\n输入“/pjsk绑定+pjskID”来绑定吧~")

    else:
        try:
            url = f'https://api.pjsekai.moe/api/user/{str(userID)}/profile'
            getdata = req.get(url)
            data1 = json.loads(getdata.text)

            _clr,_all,_fc,_ap = await pj_musicCompletedDataGet(uid,data1)
            image1 = Image.open(load_path+f'\\test.png')
            new_image =load_path+f'\\pjskjindu.png'


            if selection == 0:
                icon = Image.open(BytesIO((await get_usericon(f'{uid}')).content)) #####
            else:
                icon = Image.open(BytesIO((await getLeaderIcon(data1)).content))

            font = ImageFont.truetype(load_path+f'\\CAT.TTF',size=40)
            font1 = ImageFont.truetype(load_path+f'\\zzaw.ttf',size=50)
            font2 = ImageFont.truetype(load_path+f'\\CAT.TTF',size=36)
            draw = ImageDraw.Draw(image1)

            u = data1['user']['userGamedata']['name'].encode("utf-8")
            if len(u) < 18:
                draw.text((214,75),data1['user']['userGamedata']['name'],'#000000',font=font1)
            else:
                font1 = ImageFont.truetype(load_path+f'\\zzaw.ttf',size=30)
                draw.text((214,95),data1['user']['userGamedata']['name'],'#000000',font=font1)

            draw.text((315,135),str(data1['user']['userGamedata']['rank']), "#FFFFFF",font=font2)
            icon = icon.resize((117,117),Image.Resampling.LANCZOS)
            image1.paste(icon, (67,57))

            for i in _ap[0]:
                if i <= '31':
                    draw.text((167,284+(97*(int(i)-26))),str(_ap[0][i]), color["ap"],font=font)
                else:
                    draw.text((667,284+(97*(int(i)-32))),str(_ap[0][i]), color["ap"],font=font)
            for i in _fc[0]:
                if i <= '31':
                    draw.text((242,284+(97*(int(i)-26))),str(_fc[0][i]), color["fc"],font=font)
                else:
                    draw.text((742,284+(97*(int(i)-32))),str(_fc[0][i]), color["fc"],font=font)
            
            for i in _clr[0]:
                if i <= '31':
                    draw.text((317,284+(97*(int(i)-26))),str(_clr[0][i]), color["clr"],font=font)
                else:
                    draw.text((817,284+(97*(int(i)-32))),str(_clr[0][i]), color["clr"],font=font)
            for i in _all[0]:
                if i <= '31':
                    draw.text((392,284+(97*(int(i)-26))),str(_all[0][i]), color["all"],font=font)
                else:
                    draw.text((892,284+(97*(int(i)-32))),str(_all[0][i]), color["all"],font=font)
            
            buf = BytesIO()
            image1.save(buf, format='PNG')
            base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
            await bot.send(ev,f'[CQ:image,file={base64_str}]',at_sender = True)
        except:
            await bot.send(ev,f"api或服务器可能寄了 或者你这个小可爱填错别人ID 不然一般是不会出现意料之外的问题的！ \n请及时联系管理员看看发生什么事了")


'''
userID = await lg(uid)
url = f'https://api.pjsekai.moe/api/user/{userID}/profile'
getdata = req.get(url)
data1 = json.loads(getdata.text)
#print(data1)
'''
''' 备份 给新功能测试
loop = asyncio.get_event_loop() 
loop.run_until_complete(pj_profileGet())
loop.close()
'''
