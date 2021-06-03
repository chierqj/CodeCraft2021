import requests
import pandas as pd


c = '_frid=d7a37655be6246ce9b9b41b62fe501b7; vk=230b9cba-a45a-4b75-b117-226bd7eee76d; deviceid=VCE68GI5; _ga=GA1.2.1999562979.1616115433; _gid=GA1.2.485905941.1616115433; ua=725bcd9db2f641cfb1bbfebe8d85f7b4; HWWAFSESID=ea09273b9468897597; HWWAFSESTIME=1616635513358; ad_tm=; ad_cmp=; ad_ctt=; ad_mdm=; ad_sc=; SessionID=7fd0ece7-02b2-454d-a8c6-13d484f1cd51; ad_adp=; cf=Direct; locale=zh-cn; __ozlvd1791=1616635514; user_tag=f70a40bdafae4b2a97052fa629f1fb54; masked_domain=c**er; masked_user=c**er; masked_phone=159****6162; usite=cn; popup_max_time=60; x-framework-ob=""; domain_tag=chier; devclouddevui420J_SESSION_ID="{ec4faee94ac4151f9b42bfa766f3972a9e35ccab18846255}"; devclouddevui420cftk=H0L9-W8AW-4ZW7-K0HF-U2KK-IBW8-XL98-65NS; a3ps_1d41_saltkey=HGDmAFh2; a3ps_1d41_lastvisit=1616632847; a3ps_1d41_groupviewed=1326; HWS_ID=uJ9aGms94Ad49vM-Q6stnw.._-_1616640049_-_6lUjMrY22yYoOn-yCiaTCwkz6hI.; a3ps_1d41_auth=0A8F85AAFDB06CCB55FA4B769EA8FABCDCD1A2FDD9C89F2A31D11C1D4C60EA9F43E3395DE604C81C26C353AE82C5D155D33651A7739246A895807486DB68AC4842F1EFAE0F8565563B91C0C6413D61E7E09E191C6289A5BE80F816FD4585510EA2337DBB57439063212D6F19D4D5D1D8BF9D89609B0155F816C22961240918CF049335EAAE907396BADD04A3A9BDEF7FB8348662275EA6A9B811837285037122%2666c0f30cf97fe5f5; a3ps_1d41_csrftoken=17bb338983283f19ecb3; FORUM_ID=uJ9aGms94Ad49vM-Q6stnw..; a3ps_1d41_viewthread_ordertype=2; a3ps_1d41_st_p=79598%7C1616636466%7Cbbd60f77841eb9699a2916e7eaf406d22f37f62c1897e09a3dc1a33b187b2269; a3ps_1d41_sid=iPjoz0; a3ps_1d41_lip=124.115.222.148%2C1616636466; a3ps_1d41_lastact=1616636467%09forum.php%09ajax'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Cookie': c
}


nav_list = [9, 13, 10, 14, 11, 15, 12, 16]
urls = [
    'https://competition.huaweicloud.com/v1/competions/1000041380/team_ranking?stage_id=141693&page_no=1&page_size=100&area_id={}&_=1615551916026'.format(it) for it in nav_list]
divisions = ["京津东北赛区", "上合赛区", "杭厦赛区", "江山赛区",
             "成渝赛区", "西北赛区", "武长赛区", "粤港澳赛区"]


result = []
for div, url in zip(divisions, urls):
    res = requests.get(url, headers=headers)
    data = res.json()
    print(div, data["result"]["total"])
    rank_list = data["result"]["teamRankingList"]
    for it in rank_list:
        it["area"] = div
    result.extend(rank_list)
df = pd.DataFrame(result)
order = ["area", "team_name", "cost",
         "migration", "time_score", "created_time"]
df = df[order]
df.to_csv("rank.csv", index=False, encoding="utf_8_sig")
# df.to_csv("rank.csv", encoding="utf_8_sig")
