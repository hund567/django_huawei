# -*- coding: utf-8 -*-


from django.contrib import admin

# Register your models here.
from models import Array,Lun,Server

#创建后台维护页面的新类

class Serveradmin(admin.ModelAdmin):
    #列表页属性
    list_display = ['pk','server_ID','server_name','server_IP','server_wwn','array_id_id']

    list_filter = ['server_ID','array_id_id']
    search_fields = ['server_ID','server_name','server_IP','server_wwn','array_id_id']
    list_per_page = 10
    #
    # #添加修改页属性
    # fields = []
    # fieldset = []


class Lunadmin(admin.ModelAdmin):
    def LUNID(self):
        return self.lun_ID
    LUNID.short_description = "LUN 唯一标识"




    #列表页属性
    list_display = ['pk',LUNID,'lun_NAME','lun_CAPACITY','lun_WWN','server_ID']
    list_filter = ['lun_ID','lun_WWN','server_ID']
    search_fields = ['lun_ID','lun_WWN','server_ID']
    list_per_page = 10
    #
    # #添加修改页属性
    #fields = ['lun_NAME','lun_CAPACITY','lun_WWN','server_ID','lun_ID']
    fieldsets = [("base",{"fields":['lun_ID']}),("info",{"fields":['lun_NAME','lun_CAPACITY','lun_WWN','server_ID']})]
    #修改页面字段描述

#采用装饰器
#装饰的是一个类
@admin.register(Array)
class Arrayadmin(admin.ModelAdmin):
    #列表页属性
    list_display = ['pk','array_id','array_name','location','array_ip','PRODUCTVERSION','patchVersion','TOTALCAPACITY','FREEDISKSCAPACITY','STORAGEPOOLCAPACITY','STORAGEPOOLFREECAPACITY']
    list_filter = ['array_name','array_ip']
    search_fields = ['array_name','array_ip']
    list_per_page = 10
    #
    # #添加修改页属性
    # fields = ['','']
    # fieldset = []

    actions_on_bottom = True
    actions_on_top = False

#注册的时候将类加入到属性里面去
# admin.site.register(Array,Arrayadmin)
admin.site.register(Lun,Lunadmin)
admin.site.register(Server,Serveradmin)