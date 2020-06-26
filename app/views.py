from django.shortcuts import render
from django.http import HttpResponse
import json
#from .models import User, Device, Data, Warning, Option, Timedtask, Upload
from .models import User, Device, Data, Warning, Option, Timedtask, Upload
# Create your views here.
from django.db.models import Max
import time
import socket

def priceCalculate(imei, startTimeStamp, endTimeStamp):
    if startTimeStamp < 86400:
        startTimeStamp = 86400
    devices = Device.objects.filter(imei = imei)
    if devices.exists():
        device = devices[0]
        prices  = eval(device.price)
        prices.pop(0)
        timeStamp = list()
        priceStamp = list()
        for i in range(len(prices)):
            hm = prices[i]["cuttime"].replace(':', '-') + "-00"
            timeStamp.append(hm)
            priceStamp.append(prices[i]["price"])
        endTimeStamp = endTimeStamp
        startTimeStamp = startTimeStamp - 86400
        p = startTimeStamp + 86400
        Price = 0
        while p <= endTimeStamp:
            before = p - 86400
            after = p
            ymd = time.strftime('%Y-%m-%d', time.localtime(before))
            for i in range(len(timeStamp)):
                if i == 0:
                    start = before
                    end = time_stamp_trans(ymd + "-" + timeStamp[i])
                    price = float(priceStamp[i])
                elif i == len(timeStamp) - 1:
                    start = time_stamp_trans(ymd + "-" + timeStamp[-2])
                    end = after
                    price = float(priceStamp[i])
                else:
                    start = time_stamp_trans(ymd + "-" + timeStamp[i-1])
                    end = time_stamp_trans(ymd + "-" + timeStamp[i])
                    price = float(priceStamp[i])
                datas = Data.objects.filter(time__gte=start, time__lte=end, imei=devices[0])
                if len(datas) >= 2:
                    Price = Price + price * (datas[len(datas)-1].WPosAc - datas[0].WPosAc)
                elif len(datas) == 0:
                    pass
                else: #TODO : 目前先按0计算，后续可细化
                    pass
            p = p + 86400
        return Price
    else:
        return 0


def error_code_trans(error_code_string):
    diff_len = 16 - len(error_code_string)
    error_code_string = diff_len * '0' + error_code_string
    result = ""
    if error_code_string[0] == "1":
        result += "温度报警 "
    if error_code_string[1] == "1":
        result += "欠电压报警 "
    if error_code_string[2] == "1":
        result += "过电压报警 "
    if error_code_string[3] == "1":
        result += "过载报警 "
    if error_code_string[4] == "1":
        result += "电流短路短延时报警 "
    if error_code_string[5] == "1":
        result += "拉弧报警 "
    if error_code_string[6] == "1":
        result += "漏电报警 "
    if error_code_string[7] == "1":
        result += "电流短路瞬时报警 "
    if error_code_string[8] == "1":
        result += "温度故障 "
    if error_code_string[9] == "1":
        result += "欠电压故障 "
    if error_code_string[10] == "1":
        result += "过电压故障 "
    if error_code_string[11] == "1":
        result += "过载故障 "
    if error_code_string[12] == "1":
        result += "短路短延时故障 "
    if error_code_string[13] == "1":
        result += "拉弧故障跳闸 "
    if error_code_string[14] == "1":
        result += "漏电故障 "
    if error_code_string[15] == "1":
        result += "电流短路瞬时故障 "
    return result

def time_stamp_trans(string):
    #tss1 = '2013-10-10 23:40:00'
    # 转为时间数组
    timeArray = time.strptime(string, "%Y-%m-%d-%H-%M-%S")
    # 转为时间戳
    timeStamp = int(time.mktime(timeArray))
    #print("timestamp:", timeStamp)
    return timeStamp

def home(request):
    try:
        if request.method == 'POST':
            postData = request.POST
            openid = postData.get("openid")  #openid
            imei = postData.get("imei")  #imei

            jsonData = {}
            return HttpResponse(json.dumps(jsonData))
        else:
            return HttpResponse("fail")
    except Exception as e:
        return HttpResponse(repr(e))


'''
  userNickName: NaN,
    userPhone: NaN,
    userEmail: NaN,
    userKey: NaN
'''
def login(request):
    try:
        if request.method == 'POST':
            postData = request.POST
            userPhone = postData.get('userPhone')
            userKey = postData.get('userKey')
            user = User.objects.filter(userPhone=userPhone)
            if user.exists():
                if userKey == user[0].userKey:
                    jsonData = {
                        "result": "success",
                        "message": "success",
                        "userNickName": user[0].userNickName,
                        "userUserId": user[0].userPhone,
                        "userEmail": user[0].userEmail
                    }
                else:
                    jsonData = {
                        "result": "fail",
                        "message": "phone number or the key is not right",
                    }
            else:
                jsonData = {
                    "result": "fail",
                    "message": "haven't register",
                }
            return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "please use POST",
            }
            return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        return HttpResponse(repr(e))
'''
0:没有使用POST方法
1：注册成功
2：手机号已被注册
3：手机号未注册
4：账号或密码错误
5：登陆成功
'''

def register(request):
    try:
        if request.method == 'POST':
            postData = request.POST
            userNickName = postData.get('userNickName')
            userPhone = postData.get('userPhone')
            userEmail = postData.get('userEmail')
            userKey = postData.get('userKey')
            print(userKey,userEmail,userNickName,userPhone)
            user = User.objects.filter(userPhone = userPhone)
            if user.exists():
                jsonData = {
                    "result": "fail",
                    "message": "phone had been registered",
                }
            else:
                newUser = User()
                newUser.userPhone = userPhone
                newUser.userEmail = userEmail
                newUser.userKey = userKey
                newUser.userNickName = userNickName
                newUser.save()
                jsonData = {
                    "result": "success",
                    "message": "register success",
                }
            return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "please use POST",
            }
            return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        return HttpResponse(repr(e))

def deviceslist(request):
    try:
        if request.method == 'POST':
            postData = request.POST
            option = postData.get('option')
            if option == 'deviceslist':
                userUserId = postData.get('userUserId')
                user = User.objects.filter(userPhone=userUserId)
                if user.exists():
                    devices = user[0].device_set.all()
                    if len(devices) == 0:
                        jsonData = {
                            "result": "fail"
                        }
                    else:
                        deviceList = []
                        for device in devices:
                            deviceList.append(
                                {
                                    "devName": device.deviceName,
                                    "devImei": device.imei,
                                    "devBindTime": device.time
                                }
                            )
                        jsonData = {
                            "result": "success",
                            "deviceList": deviceList
                        }
                else:
                    jsonData = {
                        "result": "fail",
                        "message": "phone haven't been registered",
                    }
                return HttpResponse(json.dumps(jsonData))
            elif option == 'delete':
                userUserId = postData.get("userUserId")
                imei = postData.get("imei")
                user = User.objects.get(userPhone=userUserId)
                device = Device.objects.get(imei=imei)
                device.user.remove(user)
                jsonData = {
                    "result": "success",
                }
                return HttpResponse(json.dumps(jsonData))
            else:
                jsonData = {
                    "result": "fail",
                    "message": "option don't exist",
                }
                return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "didn't use POST",
            }
            return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        return HttpResponse(repr(e))

def adddevice(request):
    try:
        if request.method == 'POST':
            postData = request.POST
            option = postData.get('option')
            if option == 'adddevice':
                location = postData.get('location')
                latitude = postData.get('latitude')
                longitude = postData.get('longitude')
                imei = postData.get('imei')
                deviceName = postData.get('deviceName')
                devices = Device.objects.filter(imei=imei)
                if devices.exists():
                    device = Device.objects.get(imei=imei)
                    device.location = location
                    device.latitude = latitude
                    device.longitude = longitude
                    device.deviceName = deviceName
                    device.save()
                else:  # 如果imei未注册
                    Device.objects.create(imei=imei, deviceName=deviceName, location=location, latitude=latitude,
                                          longitude=longitude, device_version="V1.0.0", soft_version="V1.4", time=time.time())
                device = Device.objects.get(imei=imei)
                user = User.objects.get(userPhone=postData.get("userUserId"))
                try:
                    device.user.add(user)
                except Exception as e:
                    jsonData = {
                        "result": "fail",
                        "message": str(Exception)+str(e)
                    }
                else:
                    jsonData = {
                        "result": "success"
                    }
                return HttpResponse(json.dumps(jsonData))
            elif option == "edit":
                imei = postData.get('imei')
                devices = Device.objects.filter(imei=imei)
                if devices.exists():
                    device = Device.objects.get(imei=imei)
                    devName = device.deviceName
                    devAddress = {
                        "latitude": device.latitude,
                        "longitude": device.longitude,
                        "addrStr": device.location
                    }

                    devBindTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(device.time))
                    devSwVision = device.soft_version
                    jsonData = {
                        "result": "success",
                        "devName": devName,
                        "devAddress": devAddress,
                        "devBindTime": devBindTime,
                        "devSwVision": devSwVision
                    }
                else:
                    jsonData = {
                        "result": "fail"
                    }
                return HttpResponse(json.dumps(jsonData))
            else:
                jsonData = {
                    "result": "fail",
                    "message": "option don't exist",
                }
                return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "didn't use POST",
            }
        return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        return HttpResponse(repr(e))

def devaccountrule(request):
    try:
        if request.method == "POST":
            postData = request.POST
            option = postData.get('option')
            if option == "get":
                imei = postData.get('imei')
                device = Device.objects.get(imei=imei)
                timeAccount = eval(device.price)
                #print(timeAccount)
                jsonData = {
                    "result": "success",
                    "timeAccount": timeAccount
                }
            elif option == "set":
                timeAccount = postData.get('timeAccount')
                imei = postData.get('imei')
                device = Device.objects.get(imei=imei)
                device.price = timeAccount
                device.save()
                jsonData = {
                    "result": "success",
                }
            else:
                jsonData = {
                    "result": "fail",
                    "message": "option don't exist",
                }
            return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "didn't use POST",
            }
            return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        return HttpResponse(repr(e))

def dynamicdata(request):
    try:
        if request.method == 'POST':
            postData = request.POST
            imei = postData.get('imei')
            date = postData.get('date')
            devices = Device.objects.filter(imei=imei)
            if devices.exists():
                startTimeStamp = time_stamp_trans(str(date) + "-00-00-00")
                endTimeStamp = time_stamp_trans(str(date) + "-23-59-59")
                datas = Data.objects.filter(time__gte=startTimeStamp, time__lte=endTimeStamp, imei=devices[0])
                header = ['Time', 'Uab', 'Ubc', 'Uca', 'Iab', 'Ibc', "Ta", "Pa", "Pb", "Pc", "Pt", "Qa", "Qb", "Qc", "Qt", "Sa", "Sb", "Sc", "St", "PFa", "PFb", "PFc", "PFt", "FREQ"]
                result = list()
                result.append(header)
                if datas.exists():
                    for data in datas:
                        result.append([data.time, data.U1, data.U2, data.U3, data.I1, data.I2, data.TA, data.PA, data.PB, data.PC, data.PT, data.QA, data.QB, \
                                        data.QC, data.QT, data.SA, data.SB, data.SC, data.ST, data.PFA, data.PFB, data.PFC, data.PF, data.FREQ])
                    print("dynamic", result)
                    jsonData = {
                        "result": "success",
                        "data": result,
                    }
                else:
                    jsonData = {
                        "result": "fail",
                        "message": "no data"
                    }
            else:
                jsonData = {
                    "result": "fail"
                }
            return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "didn't use POST",
            }
            return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        return HttpResponse(repr(e))

'''
// 从title里面找对应的子集
  time:1522306819000, //最近一次查询时间 TODO
  title: ['Uab', 'Ubc', 'Uca', 'Iab', 'Ibc', "Ta", "Pa", "Pb", "Pc", "Pt", "Qa", "Qb", "Qc", "Qt", "Sa", "Sb", "Sc", "St", "PFa", "PFb", "PFc", "PFt","FREQ"],
  value: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], //不知道会不会变精度 变的话还得加个精度项 tofixnum 没必要
'''
def realtimemonitor(request):
    try:
        if request.method == 'POST':
            postData = request.POST
            imei = postData.get('imei')
            devices = Device.objects.filter(imei=imei)
            if devices.exists():
                datas = Data.objects.filter(imei=devices[0])
                if datas.exists():
                    data = datas[len(datas) - 1]
                    #print(data)
                    curtime = data.time
                    print(data.ST)
                    title = ['Uab', 'Ubc', 'Uca', 'Iab' ,'Ibc','Ica' ,"Ta", "Tb", "Tc", "Pa", "Pb", "Pc", "Pt", "Qa", "Qb", "Qc", "Qt", "Sa",
                             "Sb", "Sc", "St", "PFa", "PFb", "PFc", "PFt", "FREQ", "PAE", "PRE", "NAE", "NRE"]
                    print(data.ST)
                    value = [data.U1, data.U2, data.U3, data.I1, data.I2, data.I3, data.TA, data.TB, data.TC, data.PA, data.PB, data.PC, data.PT,
                             data.QA, data.QB, data.QC, data.QT, data.SA, data.SB,
                             data.SC, data.ST, data.PFA, data.PFB, data.PFB, data.PFC, data.PF, data.FREQ, data.WPosAc, data.WPosRe, data.WRevAc, data.WRevRe]
                    print(data.ST)
                    result = {
                        "time": curtime,
                        "title": title,
                        "value": value
                    }
                    print(data.ST)
                    #print("realmonitor", result)
                    jsonData = {
                        "result": "success",
                        "data": result,
                    }
                else:
                    jsonData = {
                        "result": "fail",
                    }
            else:
                jsonData = {
                    "result": "fail",
                }
            return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": 0,
            }
            return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        return HttpResponse(repr(e))
#["now or old","deviceIMEI","faultTime","faultType(直接给我二进制)","faultPos","actType开关工作状态标志位",faultId]

def warningmessage (request) :
    try:
        if request.method == "POST":
            postData = request.POST
            imei = postData.get("imei")
            devices = Device.objects.filter(imei=imei)
            if devices.exists():
                warnings = Warning.objects.filter(imei=devices[0])
                if warnings.exists():
                    result = list()
                    for i in range(len(warnings)):
                        result.append([0, devices[0].imei, devices[0].deviceName,
                                       warnings[len(warnings) - i - 1].time,
                                       warnings[len(warnings) - i - 1].fault_type,
                                       warnings[len(warnings) - i - 1].fault_phase,
                                       warnings[len(warnings) - i - 1].on_off, len(warnings) - i - 1])
                    result[0][0] = 1
                    print(result)
                    jsonData = {
                        "result": "success",
                        "data": result,
                    }
                else:
                    jsonData = {
                        "result": "fail"
                    }
            else:
                jsonData = {
                    "result": "fail"
                }
            return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "didn't use POST",
            }
            return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        print(Exception, e)
        return HttpResponse(repr(e))

def energystatistics(request):
    try:
        if request.method == "POST":
            postData = request.POST
            imei = postData.get("imei")
            startTime = postData.get("startTime")
            endTIme = postData.get("endTime")
            startTimeStamp = time_stamp_trans(startTime+"-00-00-00")
            startTimeStamp = startTimeStamp - 86400
            endTimeStamp = time_stamp_trans(endTIme+"-23-59-59")
            endTimeStamp = endTimeStamp + 1
            p =startTimeStamp + 86400
            result = list()
            devices = Device.objects.filter(imei = imei)
            if devices.exists():
                print(devices[0].price)
                while p <= endTimeStamp:
                    print(p - 86400, p)
                    onDayDatas = Data.objects.filter(time__gte=p - 86400, time__lte=p, imei=devices[0])
                    p = p + 86400
                    if len(onDayDatas) == 0:
                        continue
                    onDayData = onDayDatas[len(onDayDatas) - 1]
                    result.append([onDayData.time, onDayData.WPosAc, priceCalculate(imei, p - 86400, p)])
                """
                for i in range(1, len(result)):
                    result[i][1] = result[i][1] - result[i - 1][1]
                if len(result) >= 1:
                    result.pop(0)
                """
                print(result)
                jsonData = {
                    "result": "success",
                    "data": result,
                }
            else:
                jsonData = {
                    "result": "fail",
                }
            return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "didn't use POST",
            }
            return HttpResponse(json.dumps(jsonData))

    except Exception as e:
        return HttpResponse(repr(e))

def dashboard(request):
    try:
        if request.method == "POST":
            postData = request.POST
            imei = postData.get("imei")
            devices = Device.objects.filter(imei=imei)
            if devices.exists():
                warnings = Warning.objects.filter(imei=devices[0])
                if warnings.exists():
                    warn = warnings[0]
                    fault_type = bin(warn.fault_type)
                    fault_type = error_code_trans(fault_type[2:])
                    fault_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(warn.time))
                    warning = "告警：" + str(fault_type) + " 时间：" + str(fault_time)
                else:
                    warning = "告警："
                energy = list()
                aQ = None
                aF = None
                result = {
                    "warning": warning,
                    "energy": energy,
                    "aQ": aQ,
                    "aF": aF,
                }
                datas = Data.objects.filter(imei = devices[0])
                if datas.exists():
                    data = datas[len(datas) - 1]
                    result["aQ"] = abs(data.WPosAc)
                    result["aF"] = 0
                    ctime = time.localtime(time.time())
                    cTime = time.strftime('%Y-%m-%d', ctime)
                    cTime = cTime + "-00-00-00"
                    cTime = time_stamp_trans(cTime)
                    endTimeStamp = cTime + 86400
                    startTimeStamp = endTimeStamp - 30 * 86400
                    p = startTimeStamp + 86400
                    while p <= endTimeStamp:
                        onDayDatas = Data.objects.filter(time__gte=p - 86400, time__lte=p, imei=devices[0])
                        p = p + 86400
                        if len(onDayDatas) == 0:
                            continue
                        onDayData = onDayDatas[len(onDayDatas) - 1]
                        energy.append([onDayData.time, onDayData.WPosAc])
                    """
                    for i in range(1, len(energy)):
                        energy[i][1] = energy[i][1] - energy[i-1][1]
                    if len(energy) >= 1:
                        energy.pop(0)
                    """
                result["energy"] = energy
                result["aF"] = priceCalculate(imei, datas[0].time, cTime)
                print(result["aF"])
                #result = str(result)
                #print(energy)
                jsonData = {
                    "result": "success",
                    "data": result,
                }
            else:
                jsonData = {
                    "result": "fail"
                }
            return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "didn't use POST",
            }
            return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        return HttpResponse(repr(e))

def remotecontrol(request):
    try:
        if request.method == "POST":
            postData = request.POST
            imei = postData.get("imei")
            index = postData.get("index")
            value = postData.get("value")
            devices = Device.objects.filter(imei=imei)
            if devices.exists():
                ip = '127.0.0.1'
                port = 2333
                fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #fd.sendto(b'\x03\x03\x00\x00\x00\x5f\x04\x10', (ip, port))
                fd.connect((ip, port))
                message = "remotecontrol:"+str(imei)+"-"+str(index)+"-"+str(value)
                fd.send(message.encode('utf-8'))
                fd.close()
                jsonData = {
                    "result": "success",
                }
            else:
                jsonData = {
                    "result": "fail"
                }
            return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "didn't use POST",
            }
            return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        return HttpResponse(repr(e))

def parameterset(request):
    try:
        if request.method == "POST":
            postData = request.POST
            imei = postData.get("imei")
            method = postData.get("method")
            data = postData.get("data")
            #data = eval(data)
            print(data)
            devices = Device.objects.filter(imei=imei)
            if devices.exists():
                ip = '127.0.0.1'
                port = 2333
                fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #fd.sendto(b'\x03\x03\x00\x00\x00\x5f\x04\x10', (ip, port))
                fd.connect((ip, port))
                message = "parameterset:"+str(imei)+"-"+str(data)
                fd.send(message.encode('utf-8'))
                fd.close()
                jsonData = {
                    "result": "success",
                }
            else:
                jsonData = {
                    "result": "fail"
                }
            return HttpResponse(json.dumps(jsonData))
        else:
            jsonData = {
                "result": "fail",
                "message": "didn't use POST",
            }
            return HttpResponse(json.dumps(jsonData))
    except Exception as e:
        return HttpResponse(repr(e))