# -*- coding: utf-8 -*-


from django.contrib import admin

# Register your models here.
from models import Array,Lun,Server

#创建后台维护页面的新类

class Serveradmin(admin.ModelAdmin):
    #列表页属性
    list_display = ['pk','server_ID','server_name','server_IP','server_wwn','array_id_id']

    # lsit_filter = []
    # search_fields = []
    # list_per_page = 10
    #
    # #添加修改页属性
    # fields = []
    # fieldset = []


class Lunadmin(admin.ModelAdmin):
    #列表页属性
    list_display = ['pk','lun_ID','lun_NAME','lun_CAPACITY','lun_WWN','server_ID']

    # lsit_filter = []
    # search_fields = []
    # list_per_page = 10
    #
    # #添加修改页属性
    # fields = []
    # fieldset = []


class Arrayadmin(admin.ModelAdmin):
    #列表页属性
    list_display = ['pk','array_id','array_name','location','array_ip','PRODUCTVERSION','patchVersion','TOTALCAPACITY','FREEDISKSCAPACITY','STORAGEPOOLCAPACITY','STORAGEPOOLFREECAPACITY']

    # lsit_filter = []
    # search_fields = []
    # list_per_page = 10
    #
    # #添加修改页属性
    # fields = []
    # fieldset = []



#注册的时候将类加入到属性里面去
admin.site.register(Array,Arrayadmin)
admin.site.register(Lun,Lunadmin)
admin.site.register(Server,Serveradmin)