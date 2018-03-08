# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
#创建模型类 模型类里的属性就是标、表的字段
class Array(models.Model):
    array_id = models.CharField(max_length=50)
    array_name = models.CharField(max_length=20)
    location = models.CharField(max_length=20)
    array_ip = models.CharField(max_length=20)
    PRODUCTVERSION =  models.CharField(max_length=50)
    patchVersion=  models.CharField(max_length=20)
    TOTALCAPACITY = models.IntegerField()
    FREEDISKSCAPACITY = models.IntegerField()
    STORAGEPOOLCAPACITY= models.IntegerField()
    STORAGEPOOLFREECAPACITY = models.IntegerField()
    def _str_(self):
        return "%s"%(self.array_name)
class Server(models.Model):
    server_ID = models.IntegerField()
    server_name =models.CharField(max_length=50)
    server_IP = models.CharField(max_length=20)
    server_wwn = models.CharField(max_length=100)
    #引入外键
    array_id = models.ForeignKey("Array")

class Lun(models.Model):
    lun_ID = models.CharField(max_length=50)
    lun_NAME = models.CharField(max_length=30)
    lun_CAPACITY = models.IntegerField()
    lun_WWN = models.CharField(max_length=20)
    server_ID = models.ForeignKey("Server")
