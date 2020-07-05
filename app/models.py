from django.db import models
import django.utils.timezone as timezone
# Create your models here.
class User (models.Model):
    #openid用户唯一标识
    userPhone = models.CharField(max_length=64, primary_key=True)
    #用户名
    userNickName = models.CharField(max_length=64)
    userEmail = models.CharField(max_length=64)
    userKey = models.CharField(max_length=64)

class Device (models.Model):
    #多对多关系：多个用户<->多个设备
    user = models.ManyToManyField(User)
    #设备的ip地址
    ip = models.CharField(max_length=15,null=True)
    #设备的端口号
    port = models.CharField(max_length=8,null=True)
    #时间
    time = models.BigIntegerField(null=True)
    #device type
    deviceType = models.CharField(max_length= 5, null = True)
    #imei设备唯一标识
    imei = models.CharField(max_length=32)
    #设备地理位置
    location = models.CharField(max_length=32,null=True)
    #设备软件版本
    soft_version = models.CharField(max_length=32,null=True)
    #设备版本
    device_version = models.CharField(max_length=32,null=True)
    #设备名称
    deviceName = models.CharField(max_length=20, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    price = models.CharField(max_length=50, null = True)

class Data (models.Model):
    #外键 ： 设备imei
    imei = models.ForeignKey(Device, on_delete=models.CASCADE)
    #2018-02-01-22
    time = models.BigIntegerField()
    PA = models.FloatField()     # 57
    PB = models.FloatField()    # 58
    PC = models.FloatField()    # 59
    PT = models.FloatField()    # 60
    QA = models.FloatField()    # 61
    QB = models.FloatField()    # 62
    QC = models.FloatField()    # 63
    QT = models.FloatField()    # 64
    SA = models.FloatField()   # 65
    SB = models.FloatField()    # 66
    SC = models.FloatField()    # 67
    ST = models.FloatField()    # 68
    PFA = models.FloatField()    # 69
    PFB = models.FloatField()    # 70
    PFC = models.FloatField()    # 71
    PF = models.FloatField()    # 72
    FREQ = models.FloatField()    # 73
    WPosAc = models.FloatField()    # 74 正向有功
    WPosRe = models.FloatField()   # 75
    WRevAc = models.FloatField()    # 76 反向有功
    WRevRe = models.FloatField()    # 77
    '''
    Ia = models.CharField(max_length=10)    # 
    Ib = models.CharField(max_length=10)    # 
    Ic = models.CharField(max_length=10)    # 
    Va = models.CharField(max_length=10)    # 
    Vb = models.CharField(max_length=10)    # 
    Vc = models.CharField(max_length=10)    # 
    '''
    TA = models.FloatField()    # 8
    TB = models.FloatField()    # 9
    TC = models.FloatField()    # 10
    Ileakage = models.FloatField()  #1
    I1 = models.FloatField()    # 2
    I2 = models.FloatField()    # 3
    I3 = models.FloatField()    # 4
    U1 = models.FloatField()    # 5
    U2 = models.FloatField()    # 6
    U3 = models.FloatField()    # 7



class Warning (models.Model):
    # 外键 ： 设备imei
    imei = models.ForeignKey(Device, on_delete=models.CASCADE)
    # 告警时间
    time = models.BigIntegerField()
    #工作状态
    on_off = models.IntegerField()
    # 故障类型 故障一_故障二_故障三  。。。。
    fault_type = models.IntegerField()
    # 故障所在相位 (A or B or C)
    fault_phase = models.IntegerField()
    delay_time = models.FloatField()
    UA = models.FloatField()
    UB = models.FloatField()
    UC = models.FloatField()
    IA = models.FloatField()
    IB = models.FloatField()
    IC = models.FloatField()
    Ileakage = models.FloatField()
    TA = models.FloatField()
    TB = models.FloatField()
    TC = models.FloatField()


class Option (models.Model):
    # 外键 ： 设备imei
    imei = models.ForeignKey(Device, on_delete=models.CASCADE)
    # 操作时间
    time = models.BigIntegerField()
    # 操作类型 (合/开 True False)
    on_off_opt = models.BooleanField()
    instant_shortcircuit = models.IntegerField()
    short_delay_short_circuit = models.IntegerField()
    fault_overload_I = models.IntegerField()
    fault_leakage_I = models.IntegerField()
    fault_overload_U = models.IntegerField()
    fault_leakage_U = models.IntegerField()
    overload_time = models.IntegerField()
    fault_temp = models.IntegerField()
    heart_time = models.IntegerField()

class Timedtask (models.Model):
    # 外键 ： 设备imei
    imei = models.ForeignKey(Device, on_delete=models.CASCADE)
    #定时任务时间 ：示例： "0022" (00:22)
    time = models.BigIntegerField()
    #合/分闸 (True = 合闸  False = 分闸)
    on_off = models.IntegerField()

class Upload(models.Model):
    # 外键 ： 设备imei
    imei = models.ForeignKey(Device, on_delete=models.CASCADE)
    Ileakage = models.FloatField()
    IA = models.FloatField()
    IB = models.FloatField()
    IC = models.FloatField()
    UA = models.FloatField()
    UB = models.FloatField()
    UC = models.FloatField()
    TA = models.FloatField()
    TB = models.FloatField()
    TC = models.FloatField()
    on_off = models.IntegerField()
    error_code = models.IntegerField()
    time = models.BigIntegerField()
