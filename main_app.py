import streamlit as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from pyecharts.charts import Pie, Bar
from streamlit_echarts import st_pyecharts
from pyecharts import options as opts
import plotly.express as px

st.set_page_config(page_title='揽星辰', page_icon=None, layout="wide",
                   initial_sidebar_state="auto", menu_items=None)


password = st.sidebar.text_input('请输入密码', type='password')
if password == 'lxc':
    name = '揽星辰'
elif password == 'gch':
    name = '观沧海'
elif password == 'ljt':
    name = '落九天'
elif password == '':
    st.warning('请输入密码')
    st.stop()
else:
    st.error('密码错误')
    st.stop()

main_function = st.sidebar.radio('功能选择', ['活动前后对比分析','周战功考核'])

if main_function == '活动前后对比分析':
    st.header(str(name) +'同盟考勤管理')

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

    name1 = pd.to_datetime(fileup1.name[4:].strip('.csv').replace('年','/').replace('(1)','').replace('(2)','').
                           replace('(3)','').replace('(4)','').replace('(5)','').replace('(6)','').
                           replace('月','/').replace('日',' ').replace('时',':').replace('分',':').replace('秒',''))
    name2 = pd.to_datetime(fileup2.name[4:].strip('.csv').replace('年','/').replace('(1)','').replace('(2)','').
                           replace('(3)','').replace('(4)','').replace('(5)','').replace('(6)','').
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

    res['分组-后'] = res['分组-后'].str.strip(' ')
    st.header('数据变化')
    res = res.dropna()
    st.caption('战功变化共计'+ str(len(res)) +'人')
    team_list = res['分组-后'].drop_duplicates().values.tolist()
    col1, col2 = st.columns([1,2])
    with col1:
        team_select = st.multiselect('选择分组', team_list, team_list)



    res = res[res['分组-后'].isin(team_select)]
    for i in team_select:
        st.subheader(i)
        temp = res[res['分组-后']==i]
        if temp.empty:
            st.write('无分组'+str(i)+ '数据')
        else:
            col1, col2 = st.columns([1,1])
            with col1:
                st.caption('战功变化')

                temp['战功变化'] = temp['战功总量-后'] - temp['战功总量']
                war = temp[['成员','分组','战功总量','战功总量-后','战功变化']]
                war = war.sort_values('战功变化', ascending=False)
                st.dataframe(war.set_index('成员'), use_container_width=True)
            with col2:
                st.caption('势力值变化')
                temp['势力值变化'] = temp['势力值-后'] - temp['势力值']
                land = temp[['成员','分组','势力值','势力值-后','势力值变化']]
                land = land.sort_values('势力值变化', ascending=False)
                st.dataframe(land.set_index('成员'), use_container_width=True)


else:
    st.title('周战功考核')
    fileup = st.file_uploader('上传同盟文件')
    if fileup is not None:

        df = pd.read_csv(fileup)
        df.columns = df.columns.str.strip(' ')
    else:
        st.warning('请上传文件')
        st.stop()
    st.subheader('当前战功及势力情况(不含小号及未分组)')
    test = df[['分组','成员','战功总量','战功本周','势力值']]
    test['分组'] = test['分组'].str.strip(' ')
    test = test[test['分组'].isin(['小号','未分组']) == False]
    test['全盟'] = '全盟'
    group = test.groupby(['分组'])['战功本周','战功总量','势力值'].mean().reset_index().round(0)
    group1 = test.groupby(['全盟'])['战功本周','战功总量','势力值'].mean().reset_index().round(0).rename(columns={'全盟':'分组'})
    group = pd.concat([group,group1])


    g = (
        Bar()
        .add_xaxis(group['分组'].values.tolist())

        .add_yaxis("战功本周", group['战功本周'].values.tolist())
        .add_yaxis("战功总量", group['战功总量'].values.tolist())
        .add_yaxis("势力值", group['势力值'].values.tolist())

        .set_global_opts(

            title_opts=opts.TitleOpts(title="战功势力对比(平均)"),
            legend_opts=opts.LegendOpts(selected_map={"战功总量": False}),
        )
    )
    col1, col2 = st.columns([1,1])
    with col1:
        st_pyecharts(g, height = 600)

    with col2:
        func = st.selectbox('功能选择', ['战功总量','势力值','战功本周'])
        hg = px.histogram(test, x=func, nbins=20,height=500, title='总战功分布',
                          color="分组")
        st.plotly_chart(hg,use_container_width=True)







    with st.expander('周战功考核',expanded=True):
        use_multi = st.checkbox('是否使用战功 = 势力 * 倍数', value=False)
        if use_multi:

            col1, col2 = st.columns([1,1])
            with col1:
                multi_factor = st.slider('选择倍数',min_value=1,max_value=10,value=3,step=1)

                team_list = df['分组'].drop_duplicates().values.tolist()
                team_list.insert(0,'全盟')

                team_select = st.radio('选择分组', team_list, horizontal=True)

        else:
            level = st.radio('档位设置', [2,3,4], horizontal=True)


            start_list = []
            war_num_list = []
            for l in range(int(level)):
                col1, col2= st.columns([1,1])


                with col1:
                    if l == int(level-1):
                        start = st.slider('势力值起始',
                                          min_value=0,
                                          max_value=40000,
                                          value=(l*15000,40000),
                                          step=1000,
                                          key=str(l))
                    else:
                        start = st.slider('势力值起始',
                                          min_value=0,
                                          max_value=40000,
                                          value=(l*15000,(l+1)*15000),
                                          step=1000,
                                          key=str(l))
                    start_list.append(start)
                with col2:
                    war_num = st.slider('战功+',
                                        min_value=0,
                                        max_value=100000,
                                        value=(l+1)*10000,
                                        step=1000,
                                        key=str((l+1)*10000))
                    war_num_list.append(war_num)


    if use_multi:
        temp = df[['成员','分组','战功本周','势力值']]
        temp2 = temp[temp['战功本周'] >= temp['势力值']*multi_factor]. \
            set_index('成员').sort_values('势力值', ascending=False)
        temp1 = temp[temp['战功本周'] < temp['势力值']*multi_factor]. \
            set_index('成员').sort_values('势力值', ascending=False)

        if team_select == '全盟':
            pass
        else:
            temp1 = temp1[temp1['分组']==team_select]
            temp2 = temp2[temp2['分组']==team_select]
        col0, col1, col2 = st.columns(3)
        with col0:

            c = (
                    Pie()
                    .add(
                        "",
                        [list(z) for z in zip(['合格','不合格'], [len(temp1), len(temp2)])],
                        radius=["20%", "55%"],
                        center=["50%", "50%"],
                        label_opts=opts.LabelOpts(
                            position="outside",
                            formatter="{b|{b}: }{c}  {per|{d}%}  ",
                            background_color="#eee",
                            border_color="#aaa",
                            border_width=1,
                            border_radius=4,
                            rich={
                                "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                                "abg": {
                                    "backgroundColor": "#e3e3e3",
                                    "width": "100%",
                                    "align": "right",
                                    "height": 22,
                                    "borderRadius": [4, 4, 0, 0],
                                },
                                "hr": {
                                    "borderColor": "#aaa",
                                    "width": "100%",
                                    "borderWidth": 0.5,
                                    "height": 0,
                                },
                                "b": {"fontSize": 16, "lineHeight": 33},
                                "per": {
                                    "color": "#eee",
                                    "backgroundColor": "#334455",
                                    "padding": [2, 4],
                                    "borderRadius": 2,
                                },
                            },
                        ),
                    ).set_colors(["steelblue","lightpink"])
                    .set_global_opts(title_opts=opts.TitleOpts(title=str(team_select)))
            )
            st_pyecharts(c,
                         height=500)

        with col1:


            st.subheader(str(team_select) + '共计不合格 ' + str(len(temp1)) + '人')
            st.dataframe(temp1, use_container_width=True)
        with col2:


            st.subheader(str(team_select) + '共计合格 ' + str(len(temp2)) + '人')
            st.dataframe(temp2, use_container_width=True)

    else:
        df = df[['成员','分组','战功本周','势力值']]

        team_list = df['分组'].drop_duplicates().values.tolist()
        team_list.insert(0,'全盟')
        col1, col2 = st.columns(2)
        st.write('-'*60)
        with col1:
            team_select = st.radio('选择分组', team_list, horizontal=True)
        st.subheader(str(team_select))
        for l,col in zip(range(int(level)), st.columns(int(level))):
            with col:



                temp = df[(df['势力值'] >= start_list[l][0]) &
                       (df['势力值'] < start_list[l][1]) &
                       (df['战功本周'] < war_num_list[l])].set_index('成员').sort_values('战功本周', ascending=True)

                temp_hg = df[(df['势力值'] >= start_list[l][0]) &
                          (df['势力值'] < start_list[l][1]) &
                          (df['战功本周'] >= war_num_list[l])].set_index('成员').sort_values('战功本周', ascending=True)

                if team_select == '全盟':
                    temp1 = temp
                    temp2 = temp_hg
                    count = len(df[(df['势力值'] >= start_list[l][0]) & (df['势力值'] < start_list[l][1])])
                else:
                    temp1 = temp[temp['分组']==team_select]
                    temp2 = temp_hg[temp_hg['分组']==team_select]




                    count = len(df[(df['分组']==team_select) &
                                   (df['势力值'] >= start_list[l][0]) &
                                   (df['势力值'] < start_list[l][1])])
                st.subheader(
                             '势力值 '+ str(start_list[l][0]) + ' 到 ' + str(start_list[l][1])
                             + '总计' + str(count) + '人')
                st.subheader('不合格 ' + str(len(temp1)) + '人 - 战功低于 ' + str(war_num_list[l]) )
                if temp1.empty:
                    st.caption('无不合格人员')
                else:
                    st.dataframe(temp1, use_container_width=True)

                st.subheader('合格 ' + str(len(temp2)) + '人')
                if temp2.empty:
                    pass
                else:
                    st.dataframe(temp2, use_container_width=True)









