# -*- coding: utf-8 -*-
import os
import pymysql
import time
import datetime
infile = 'D:/date.txt'
#首先从nbu中取出数据
def get_info_and_insert(infile):
   f = open(infile,'r')
   sourceInline = f.readlines()
   dataset=[]
   for line in sourceInline:
       list1=line.strip('\n')
       list2=list1.split(',')
       dataset.append(list2)
#处理并插入数据库
   conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
   cursor = conn.cursor()
   for i in range(1,len(dataset)):
       job_id = dataset[i][0]
       start_time = int(dataset[i][8])
       end_time = int(dataset[i][10])
       elapsed = int(dataset[i][9])/60
       policy = dataset[i][4]
       schedule = str(dataset[i][5])
       client = str(dataset[i][6])
       if dataset[i][11] == '':
           storage_unit = ''
       else:
           storage_unit = dataset[i][11][-1]
       #这里一定要注意,start_time一定先转换为int,然后再转为datetime
       time_local = time.localtime(start_time)
       start_time_ts = time.strftime("%Y/%m/%d %H:%M:%S",time_local)
       time_local2 = time.localtime(end_time)
       end_time_ts = time.strftime("%Y/%m/%d %H:%M:%S", time_local2)
       time_local3 = time.localtime(elapsed)
       elapsed_ts = time.strftime("%H:%M:%S", time_local3)
       # end_time_ts = time.strftime(end_time, "%Y/%m/%d %H:%M:%S")
       # end_time_ts = time.mktime(end_time)
       #str='insert into myapp_nbu_jobinfo(job_id,start_time,end_time,elapsed,policy,schedule,client) values(%s,%s,%s,%s,%s,%s.%s)",(job_id,start_time,end_time,elapsed,policy,schedule,client)'
       cursor.execute("select count(*) from myapp_nbu_jobinfo where job_id=%s",(job_id))
       a = cursor.fetchall()
       if a[0][0] == 0:
           cursor.execute(
           "insert into myapp_nbu_jobinfo(job_id,start_time,end_time,elapsed,policy,schedule,client,storage_unit) values(%s,%s,%s,%s,%s,%s,%s,%s)",(job_id,start_time_ts,end_time_ts,elapsed,policy,schedule,client,storage_unit))
       else:
           cursor.execute(
               "update  myapp_nbu_jobinfo set start_time =%s ,end_time=%s,elapsed=%s,policy=%s,schedule=%s,client=%s,storage_unit=%s  where job_id =%s",
               (start_time_ts, end_time_ts, elapsed, policy, schedule, client, storage_unit,job_id))

       conn.commit()
   conn.close()







#下一步是创建新的表以统计次数信息
def create_statics_table():
   time_begin = datetime.date.today()
   time_stamp = time.mktime(time_begin.timetuple())

   #清空daily表
   conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
   cursor = conn.cursor()
   # cursor.execute("delete from myapp_nbu_daily")
   # conn.commit()
   # conn.close()

   #插入daily以及time表
   conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
   cursor = conn.cursor()
   cursor.execute("select distinct storage_unit from myapp_nbu_jobinfo" )
   tuple_of_storage_unit = cursor.fetchall()
   for each in tuple_of_storage_unit:


       for i in range(1,289):
           time_to_insert =  time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time_stamp - 300*i))
           cursor.execute("select * from myapp_nbu_time where time =%s and storage_unit = %s",(time_to_insert,each[0]))
           num2=cursor.rowcount
           if num2 == 0:
               cursor.execute(
                   "insert into myapp_nbu_time(time,count,storage_unit) values(%s,%s,%s)",
                   (time_to_insert,0,each[0]))

           cursor.execute("select * from myapp_nbu_daily where time =%s and storage_unit = %s", (time_to_insert,each[0]))
           num3 = cursor.rowcount
           if num3 == 0:
               cursor.execute(
                   "insert into myapp_nbu_daily(time,count,storage_unit) values(%s,%s,%s)",
                   (time_to_insert,0,each[0]))
   conn.commit()
   conn.close()




#遍历每天统计 并插入两张表
def count_one_day():
   conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
   cursor = conn.cursor()
   cursor.execute("select distinct storage_unit from myapp_nbu_jobinfo")
   tuple_of_storage_unit = cursor.fetchall()
   for each in tuple_of_storage_unit:

       cursor.execute(
           "select time from  myapp_nbu_daily where storage_unit= %s",(each[0]))
       time_group = cursor.fetchall()
       cursor.execute(
           "select start_time,end_time,storage_unit,policy from myapp_nbu_jobinfo where storage_unit= %s",(each[0]))
       nbu_info_group = cursor.fetchall()

       for eachtime in time_group:
           count = 0
           policy_list = []
           policy_str=''
           for each_nbu_info in nbu_info_group:

               if eachtime[0] > each_nbu_info[0] and eachtime[0] < each_nbu_info[1]:

                   count = count +1
                   policy_list.append(each_nbu_info[3])
           policy_str = '\n'.join(policy_list)
           cursor.execute("update myapp_nbu_time set  count=%s ,policy=%s where time=%s and storage_unit=%s",(count,policy_str,eachtime[0],each[0]))
           cursor.execute("update myapp_nbu_daily set count=%s ,policy=%s where time=%s and storage_unit=%s ",(count,policy_str, eachtime[0],each[0]))
   conn.commit()

#将数据进行统计并插入周表
def count_one_week():
   time_begin = datetime.date.today()
   time_stamp = time.mktime(time_begin.timetuple())-86400

   conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
   cursor = conn.cursor()

   # 首先清除静态表
   cursor.execute("delete from myapp_nbu_weekly")
   conn.commit()
   cursor.execute("select distinct storage_unit from myapp_nbu_jobinfo")
   tuple_of_storage_unit = cursor.fetchall()
   for each in tuple_of_storage_unit:
       cursor.execute(
           "select sum(COUNT) from  myapp_nbu_daily  where storage_unit=%s group by HOUR(time)",(each[0]))
       a = cursor.fetchall()

       #创建weekly表中字段
       for i in range(0, 23):
           time_to_insert = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time_stamp + 3600 * i))
           cursor.execute("select * from myapp_nbu_weekly where time =%s and storage_unit=%s", (time_to_insert,each[0]))
           num2 = cursor.rowcount
           if num2 == 0:
               cursor.execute(
                   "insert into myapp_nbu_weekly(time,count,storage_unit) values(%s,%s,%s)",
                   (time_to_insert, 0,each[0]))
           b = a[i][0]/12
           cursor.execute("update myapp_nbu_weekly set count=%s where time =%s and  storage_unit=%s", (b,time_to_insert,each[0]))

           cursor.execute("select * from myapp_nbu_week_all where time =%s and storage_unit=%s",
                          (time_to_insert, each[0]))
           num3 = cursor.rowcount
           if num3 == 0:
               cursor.execute(
                   "insert into myapp_nbu_week_all(time,count,storage_unit) values(%s,%s,%s)",
                   (time_to_insert, 0,each[0]))
           b = a[i][0] / 12
           cursor.execute("update myapp_nbu_week_all set count=%s where time =%s and  storage_unit=%s", (b, time_to_insert,each[0]))


   conn.commit()
   conn.close()


def count_one_month():
   time_begin = datetime.date.today()
   time_stamp = time.mktime(time_begin.timetuple()) - 86400

   conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
   cursor = conn.cursor()
   cursor.execute("select distinct storage_unit from myapp_nbu_jobinfo")
   tuple_of_storage_unit = cursor.fetchall()
   #这里就无需清除任何表了
   for each in tuple_of_storage_unit:
       cursor.execute(
           "select sum(COUNT) from  myapp_nbu_weekly WHERE storage_unit = %s group by DAY (time)",(each[0]))
       a = cursor.fetchall()

       #创建month表中字段
       time_to_insert = time.strftime("%Y/%m/%d", time.localtime(time_stamp))
       cursor.execute("select * from myapp_nbu_monthly where time =%s and storage_unit = %s", (time_to_insert,each[0]))
       num3 = cursor.rowcount

       if num3 == 0:
           cursor.execute(
               "insert into myapp_nbu_monthly(time,count,storage_unit) values(%s,%s,%s)",
               (time_to_insert, 0,each[0]))
       b = a[0][0] / 24
       cursor.execute("update myapp_nbu_monthly set count=%s where time =%s and  storage_unit = %s", (b, time_to_insert,each[0]))
   conn.commit()
   conn.close()

if __name__ == '__main__':
   #get_info_and_insert(infile)
   #create_statics_table()
   count_one_day()
   #count_one_week()
   #count_one_month()