import streamlit as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title='揽星辰', page_icon=None, layout="wide",
                   initial_sidebar_state="auto", menu_items=None)


password = st.sidebar.text_input('请输入密码', type='password')
if password != 'lxc' and password != '':
    st.error('密码错误')
    st.stop()
elif password == '':
    st.warning('请输入密码')
    st.stop()
else:
    pass




st.header('揽星辰同盟考勤管理')

col1, col2 = st.columns(2)
with col1:
    fileup1 = st.file_uploader('上传同盟文件')
    if fileup1 is not None:

        df1 = pd.read_csv(fileup1)
        df1.columns = df1.columns.str.strip(' ')
    else:
        st.warning('请上传文件')

with col2:
    fileup2 = st.file_uploader('上传同盟文件2')
    if fileup2 is not None:
        df2 = pd.read_csv(fileup2)
        df2.columns = df2.columns.str.strip(' ')
    else:
        st.stop()

name1 = pd.to_datetime(fileup1.name[4:].strip('.csv').replace('年','/').replace('(1)','/').
                       replace('月','/').replace('日',' ').replace('时',':').replace('分',':').replace('秒',''))
name2 = pd.to_datetime(fileup2.name[4:].strip('.csv').replace('年','/').
                       replace('月','/').replace('日',' ').replace('时',':').replace('分',':').replace('秒',''))

if name1 > name2:
    df1, df2 = df2, df1
    name1, name2 = name2, name1
else:
    pass

st.write('对比时间： ', name1 , ' vs ', name2)
st.write('时间相差：',name2 - name1  )

df1 = df1[['成员','分组','战功本周','战功总量','势力值']]

df2 = df2[['成员',
           '分组',
           '战功本周',
           '战功总量',
           '势力值']]


df2 = df2.rename(columns={'分组': '分组-后',
                          '战功本周': '战功本周-后',
                          '战功总量': '战功总量-后',
                          '势力值': '势力值-后'})

res = pd.merge(df1, df2, how='outer', on=['成员'])

st.header('成员退出及加入情况')
col1, col2 = st.columns(2)

join = res[res['战功本周'].isnull()].dropna(axis=1)
exit = res[res['战功本周-后'].isnull()].dropna(axis=1)
with col1:
    st.write('退出共计'+ str(len(exit)) +'人')

    st.dataframe(exit, use_container_width=True)
with col2:
    st.caption('加入共计'+ str(len(join)) +'人')

    st.dataframe(join, use_container_width=True)

res['分组'] = res['分组'].str.strip(' ')
st.header('数据变化')
res = res.dropna()
st.caption('战功变化共计'+ str(len(res)) +'人')
team_list = ['破晓','点杀','烟雨','穿雲','风华','背嵬','未分组']
col1, col2 = st.columns([1,2])
with col1:
    team_select = st.multiselect('选择分组', team_list, team_list)

res = res[res['分组'].isin(team_select)]
for i in team_select:
    st.subheader(i)
    temp = res[res['分组']==i]
    if temp.empty:
        st.write('无分组'+str(i)+ '数据')
    else:
        col1, col2 = st.columns([1,1])
        with col1:
            st.caption('战功变化')

            temp['战功变化'] = temp['战功总量-后'] - temp['战功总量']
            war = temp[['成员','分组','战功总量','战功总量-后','战功变化']]
            war = war.sort_values('战功变化', ascending=False)
            st.dataframe(war, use_container_width=True)
        with col2:
            st.caption('势力值变化')
            temp['势力值变化'] = temp['势力值-后'] - temp['势力值']
            land = temp[['成员','分组','势力值','势力值-后','势力值变化']]
            land = land.sort_values('势力值变化', ascending=False)
            st.dataframe(land, use_container_width=True)










