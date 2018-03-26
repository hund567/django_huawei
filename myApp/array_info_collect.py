# -*- coding:utf-8 -*-
import requests
import urllib, urllib2, json
import cookielib
import ssl
import xlwt
import xlrd

# #全局变量
#Arrays_list=[['93.1.243.31','2102350BVB10H8000046','admin','Admin@storage']]
# Arrays_list=[['93.1.243.31','2102350BVB10H8000046','admin','Admin@storage'],['93.1.243.25','2102350HYS10H8000042','admin','Admin@storage'],['93.1.243.63','2102350DJX10G8000002','admin','Admin@storage'],['93.1.243.63','2102350DJX10G8000002','admin','Admin@storage'],['93.1.243.61','2102350BVB10F6000042','admin','Admin@storage'],['93.225.115.54','2102350BVB10F6000041','admin','admin@Storage']]
Arrays_group_dict={}
all_info = []



# 初始化xls格式
def set_style(name,height, bold=False):
    style = xlwt.XFStyle()  # 初始化样式

    font = xlwt.Font()  # 为样式创建字体
    font.name = name  # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height


    #borders= xlwt.Borders()
    # borders.left= 6
    # borders.right= 6
    # borders.top= 6
    # borders.bottom= 6

    style.font = font
    # style.borders = borders

    ########这部分设置居中格式#######
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平居中
    alignment.vert = xlwt.Alignment.VERT_CENTER  # 垂直居中
    alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
    style.alignment = alignment

    return style


# 创建excel表
def init_excel(Arrays_group_dict):
    # 创建xls与sheet  并写好sheet字段
    wk = xlwt.Workbook()
    st_summary = wk.add_sheet(u'存储信息汇总', cell_overwrite_ok=True)
    row1 = [u'存储名称', u'存储IP', u'存储ID', u'微码版本', u'补丁版本', u'总容量(单位：Ｇ)', u'剩余裸盘容量(单位：Ｇ)', u'存储池容量(单位：Ｇ)', u'存储池剩余容量(单位：Ｇ)']

    #标准化列宽
    st_summary.col(0).width = 256 * 15
    st_summary.col(1).width = 256 * 15
    st_summary.col(2).width = 256 * 30
    st_summary.col(3).width = 256 * 15



    for i in range(0, len(row1)):
        st_summary.write(0, i, row1[i], set_style('Times New Roman', 220, True))
    # 向总表写入存储信息
    count_array = 1
    for each_array_id in Arrays_group_dict:
        sheetname = Arrays_group_dict[each_array_id][0] + ' ' + Arrays_group_dict[each_array_id][1]
        #print sheetname
        st = wk.add_sheet(sheetname, cell_overwrite_ok=True)
        row0 = [u'主机名', u'主机IP', u'主机wwn', u'lun名称', u'lun_ID', u'lun 大小(单位：Ｇ)', u'lun_wwn', u'盘机名称', u'盘机ID', u'盘机IP']
        for i in range(0, len(row0)):
            st.write(0, i, row0[i], set_style('Times New Roman',220, True))
        count=1

        #设置列宽
        st.col(0).width = 256 * 15
        st.col(1).width = 256 * 13
        st.col(2).width = 256 * 20
        st.col(3).width = 256 * 30
        st.col(6).width = 256 * 35
        st.col(8).width = 256 * 30
        st.col(9).width = 256 * 13
        st_summary.write(count_array,0,sheetname ,set_style('Times New Roman', 220, False))
        st_summary.write(count_array, 1, Arrays_group_dict[each_array_id][2], set_style('Times New Roman', 220, False))
        st_summary.write(count_array, 2, each_array_id, set_style('Times New Roman', 220, False))
        st_summary.write(count_array, 3, Arrays_group_dict[each_array_id][3], set_style('Times New Roman', 220, False))
        st_summary.write(count_array, 4, Arrays_group_dict[each_array_id][4], set_style('Times New Roman', 220, False))
        st_summary.write(count_array, 5, Arrays_group_dict[each_array_id][5], set_style('Times New Roman', 220, False))
        st_summary.write(count_array, 6, Arrays_group_dict[each_array_id][6], set_style('Times New Roman', 220, False))
        st_summary.write(count_array, 7, Arrays_group_dict[each_array_id][7], set_style('Times New Roman', 220, False))
        st_summary.write(count_array, 8, Arrays_group_dict[each_array_id][8], set_style('Times New Roman', 220, False))
        count_array = count_array + 1



    #开始写入数据
    # 遍历server_group，写入excel
    #print all_info

        all_info = Arrays_group_dict[each_array_id][9]
        for each_server in all_info:

            name = each_server[0]
            ip = each_server[1]
            wwns = each_server[2]
            wwn_string = '\n'.join(wwns)
            luns = []
            luns = each_server[3]
        #print luns
            lun_name_list = []

            for each1 in luns:

                lun_name_list.append(each1[0])
            lun_id_string = '\n'.join(lun_name_list)

            lun_name_list = []
            for each2 in luns:
                lun_name_list.append(each2[1])
            lun_name_string = '\n'.join(lun_name_list)

            lun_size_list = []
            for each3 in luns:
                lun_size_list.append(str(int(each3[2])/2097152))
            lun_size_string = '\n'.join(lun_size_list)

            lun_wwn_list = []
            for each4 in luns:
                lun_wwn_list.append(each4[3])
            lun_wwn_string = '\n'.join(lun_wwn_list)

            st.write(count, 0, each_server[0], set_style('Times New Roman', 220, False))
            st.write(count, 1, each_server[1], set_style('Times New Roman', 220, False))
            st.write(count, 2, wwn_string, set_style('Times New Roman', 220, False))
            st.write(count, 3, lun_name_string, set_style('Times New Roman', 220, False))
            st.write(count, 4, lun_id_string, set_style('Times New Roman', 220, False))
            st.write(count, 5, lun_size_string, set_style('Times New Roman', 220, False))
            st.write(count, 6, lun_wwn_string, set_style('Times New Roman', 220, False))
            st.write(count, 7, sheetname, set_style('Times New Roman', 220, False))
            st.write(count, 8, each_array_id, set_style('Times New Roman', 220, False))
            st.write(count, 9, Arrays_group_dict[each_array_id][2], set_style('Times New Roman', 220, False))


            count=count +1
        #组织总表



    #结束后设置xls列宽行高

    location = 'C:/Users/sdfh-guanc/Desktop/' + u'storage_info'.encode('utf-8') + '.xls'
    wk.save(location)

# 先创建函数以方便url拼接
def build_uri(urlinput, endpoint):
    return '='.join([urlinput, endpoint])


def func(array_ip,array_id,array_user,array_passwd):

    url_head = 'https://' + array_ip + ':8088/deviceManager/rest/'
    login_url = url_head + 'xxxxx/login'
    system_url = url_head + array_id + '/system/'
    fc_port_url = url_head + array_id + '/fc_initiator?PARENTID'
    lun_url = url_head + array_id + '/lun/associate?TYPE=11&ASSOCIATEOBJTYPE=21&ASSOCIATEOBJID'
    server_url = url_head + array_id + '/host?range=[0-100]'
    data = {'scope': 0, 'username': array_user, 'password': array_passwd}
    user_agent = r'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'
    context = ssl
    head = {'User-Agent': user_agent, 'Content-Type': 'application/json;charset=UTF-8', 'Cache-Control': 'max-age=0', 'If-Modified-Since': bytes(0), 'Accept': '*/*', 'X-Requested-With': 'XMLHttpRequest'}
    #data = {'scope': 0, 'username': 'admin', 'password': 'Admin@storage'}
    cookie = cookielib.CookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cookie_support)
    urllib2.install_opener(opener)
    server_list = ['', '', '', []]



    # 登陆并获取cookie中session信息，以备后用
    #循环开始前先置空cookie
    iBaseToken = ''
    session_info=''

    req = requests.post(url=login_url, headers=head,
                        json={"scope": 0, "username": array_user, "password": array_passwd}, verify=False)
    print req.status_code
    session_info = requests.utils.dict_from_cookiejar(req.cookies)['session']
    iBaseToken = json.loads(req.text)['data']['iBaseToken']
    head2 = {'User-Agent': user_agent, 'Content-Type': 'application/json;charset=UTF-8', 'Cache-Control': 'max-age=0', 'If-Modified-Since': bytes(0), 'Accept': '*/*', 'X-Requested-With': 'XMLHttpRequest', 'iBaseToken':iBaseToken}
    cookies = dict(CSRF_IBASE_TOKEN=iBaseToken, DEVICE_ID=array_id, initLogin='true', session=session_info)
    # 获取盘机信息
    req_main = requests.get(url=system_url, headers=head2, verify=False, cookies=cookies)
    main_info = json.loads(req_main.text)['data']


    # init_excel(main_info['ID'])
    # 获取主机信息 ID IP NAME 生成字符串


    req_server = requests.get(url=server_url, headers=head2, verify=False, cookies=cookies)
    server_info = json.loads(req_server.text)['data']
    server_group = []
    array_list = []

    for item in server_info:
        server_list=['','',[],[]]
        server_ID = item['ID']
        server_name = item['NAME']
        server_IP = item['IP']
        server_list[0] = server_name
        server_list[1] = server_IP
        # 将提取主机ID并获取相应wwn
        req_fc_port = None
        req_fc_port = requests.get(url=build_uri(fc_port_url, server_ID), headers=head2, verify=False,cookies=cookies)
        lun_list = []
        lun_info = []
        wwn_info = []
        wwn_list = []
        if 'data' in json.loads(req_fc_port.text):

            wwn_info = json.loads(req_fc_port.text)['data']
            wwn_list = []
            for eachwwn in wwn_info:
                wwn = eachwwn['ID']
                wwn_list.append(wwn)

            server_list[2] = wwn_list
        #print server_list

        # 根据主机ID获取lun信息

        req_lun = None
        req_lun = requests.get(url=build_uri(lun_url, server_ID), headers=head2, verify=False, cookies=cookies)

        if 'data' in json.loads(req_lun.text):

            lun_info = json.loads(req_lun.text)['data']
            single_lun_list = []


        for each in lun_info:
            single_lun_list=[]
            single_lun_list.append(each['ID'])
            single_lun_list.append(each['NAME'])
            single_lun_list.append(each['CAPACITY'])
            single_lun_list.append(each['WWN'])
            lun_list.append(single_lun_list)




        server_list[3] = lun_list


        server_group.append(server_list)
        #print server_group
    #将盘机ID与上面的server_group做成一个字典
    array_list.append(main_info['NAME'])
    array_list.append(main_info['LOCATION'])
    array_list.append(array_ip)
    array_list.append(main_info['PRODUCTVERSION'])
    array_list.append(main_info['patchVersion'])
    array_list.append(int(main_info['TOTALCAPACITY'])/2097152)
    array_list.append(int(main_info['FREEDISKSCAPACITY'])/2097152)
    array_list.append(int(main_info['STORAGEPOOLCAPACITY'])/2097152)
    array_list.append(int(main_info['STORAGEPOOLFREECAPACITY'])/2097152)
    array_list.append(server_group)
    Arrays_group_dict[array_id] = array_list


    return Arrays_group_dict


#test


if __name__ == '__main__':
    for each_array in Arrays_list:
        func(each_array[0],each_array[1],each_array[2],each_array[3])
    init_excel(Arrays_group_dict)


