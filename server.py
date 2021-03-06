import esockets
import os
import django
import time
import datetime
import schedule
import threading
import socket
ASK_FOR_ALL =  bytes.fromhex("03 03 00 00 00 5f 04 10")
ASK_FOR_WARNING = bytes.fromhex( '03 03 00 0a 00 0e e5 ee')
ASK_FOR_VERSION = bytes.fromhex( '03 03 00 90 00 01 85 c5')
ASK_FOR_CLOSE = bytes.fromhex( '03 05 00 00 01 88 cd de')
ASK_FOR_OPEN = bytes.fromhex( '03 05 00 00 02 99 0d 22')
ASK_FOR_LOCK = bytes.fromhex( '03 06 00 55 00 01 98 38')
ASK_FOR_UNLOCK = bytes.fromhex( '03 06 00 55 00 00 59 f8')
ASK_FOR_CHECK = bytes.fromhex( '03 06 00 56 00 01 a9 f8')
ASK_FOR_UNCHECK = bytes.fromhex( '03 06 00 56 00 00 68 38')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
django.setup()
from app import models

task_queue = []

def num_to_str(num):
    ge = num%16
    shi = num//16
    return str(shi)+str(ge)

def on_off_trans(on_off_string):
    if on_off_string == "0":
        return ""
    diff_len = 16 - len(on_off_string)
    on_off_string = diff_len * '0' + on_off_string
    if on_off_string[-1] == "1": #合闸
        code = on_off_string[0:4]
        if code == "0000":
            result = "手动合闸"
        elif code == "0001":
            result = "指令合闸"
        elif code == "0010":
            result = "自动合闸"
        elif code == "0011":
            result = "外部合闸"
        elif code == "0100":
            result = "远程自检合闸"
        elif code == "0101":
            result = "欠负载"
        elif code == "0110":
            result = "过负载"
        elif code == "0111":
            result = "缺相"
        elif code == "1000":
            result = "定时合闸"
        else:
            result = "合闸"
    elif on_off_string[-1] == "0": #分闸
        code = on_off_string[4:8]
        if code == "0000":
            result = "手动分闸"
        elif code == "0001":
            result = "指令分闸"
        elif code == "0010":
            result = "故障分闸"
        elif code == "0011":
            result = "外部分闸"
        elif code == "0100":
            result = "远程自检分闸"
        elif code == "0101":
            result = "自锁分闸"
        elif code == "0110":
            result = "非法开门分闸"
        elif code == "0111":
            result = "防雷失效分闸"
        elif code == "1000":
            result = "定时分闸"
        elif code == "1001":
            result = "欠费分闸"
        else:
            result = "分闸"
    else:
        result = ""
    return result

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
    # 转为时间数组 '2000-00-00-00-00-00'
    #print(string)
    timeArray = time.strptime(string, "%Y-%m-%d-%H-%M-%S")
    # 转为时间戳
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

def calc_crc(string):
    data = bytearray.fromhex(string)
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return "{:04X}".format(((crc & 0xff) << 8) + (crc >> 8))

def handle_incoming(client, address):
    """
    Return True: The client is accepted and the server starts polling for messages
    Return False: The server disconnects the client.
    """

    #client.sendall(b'SERVER: Connection accepted!\n')
    print(datetime.datetime.now(), "[func:handle_incoming]\t\t\t\tAccepted Client:", client)
    return True
#b'\x03\x03\x1e\x00\x00\x00\x00\x00\x00\x00\x00\tP\x00\x00\x00\x00\x00\x1a\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x93\xde'
def handle_readable(client):
    """
    Return True: The client is re-registered to the selector object.
    Return False: The server disconnects the client.
    """
    data = client.recv(1028)
    str_ip = (str(client).split(",")[-2].split("(")[1])
    str_port = str(client).split(",")[-1].split(")")[0]
    print(datetime.datetime.now(), "[func:handle_readable:Handle]\t\tReceived Client Struct:", client)
    print(datetime.datetime.now(), "[func:handle_readable:Handle]\t\tReceived Client:", str_ip, str_port)
    print(datetime.datetime.now(), "[func:handle_readable:Handle]\t\tClient Received:", data)
    if data == b'':
        print(datetime.datetime.now(), "[func:handle_readable:None]")
        return False
    if data[0:12] == b'parameterset':
        recv_client = client
        print(datetime.datetime.now(), "[func:handle_readable:Parameterset]Received Parameterset")
        data = data.decode("utf-8")
        imei = int(data.split('-')[0].split(':')[1])
        json_str = str(data.split('-')[1])
        print(datetime.datetime.now(), "[func:handle_readable:Parameterset](imei):", imei)
        print(datetime.datetime.now(), "[func:handle_readable:Parameterset](jsonstr):", json_str)
        set_json = eval(json_str)
        message = list()
        if set_json.get("inExMaiChongDianNeng") != None:
            temp = '03100052000201' + "{:04X}".format(set_json["inExMaiChongDianNeng"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inExMaiChongNum") != None:
            temp = '03060051' + "{:04X}".format(set_json["inExMaiChongNum"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inFuZaiNum") != None:
            temp = '03060099' + "{:04X}".format(set_json["inFuZaiNum"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inFuZaiValue") != None:
            temp = '0306009a' + "{:04X}".format(set_json["inFuZaiValue"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inGuoZaiShiJian") != None:
            temp = '0306002e' + "{:04X}".format(set_json["inGuoZaiShiJian"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inGuoYaDianYa") != None:
            temp = '0306002c' + "{:04X}".format(set_json["inGuoYaDianYa"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inGuoZaiDianLiu") != None:
            temp = '0306002a' + "{:04X}".format(set_json["inGuoZaiDianLiu"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inLaHuTime") != None:
            temp = '03060098' + "{:04X}".format(set_json["inLaHuTime"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inLaHuValue") != None:
            temp = '03060097' + "{:04X}".format(set_json["inLaHuValue"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inLouDianDianLiu") != None:
            temp = '0306002b' + "{:04X}".format(set_json["inLouDianDianLiu"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inQianYaDianYa") != None:
            temp = '0306002d' + "{:04X}".format(set_json["inQianYaDianYa"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inQueXiangTime") != None:
            temp = '0306009b' + "{:04X}".format(set_json["inQueXiangTime"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inShortDelayDuanLu") != None:
            temp = '03060029' + "{:04X}".format(set_json["inShortDelayDuanLu"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inShunShiDuanLu") != None:
            temp = '03060028' + "{:04X}".format(set_json["inShunShiDuanLu"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inWenDuValue") != None:
            temp = '0306002f' + "{:04X}".format(set_json["inWenDuValue"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inXinTiaoTime") != None:
            temp = '03060037' + "{:04X}".format(set_json["inXinTiaoTime"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inYuCunDianLiang") != None:
            temp = '03100035000201' + "{:04X}".format(set_json["inYuCunDianLiang"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inZhaBiSuoTime") != None:
            temp = '03060033' + "{:04X}".format(set_json["inZhaBiSuoTime"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        if set_json.get("inZhaYanShiTime") != None:
            temp = '03060032' + "{:04X}".format(set_json["inZhaYanShiTime"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        #0059 58 5a
        if set_json.get("msFenZhaTime") and set_json.get("msHeZhaTime"):
            b0_b7_0059 = set_json["msFenZhaTime"][0]
            b8_b11_0059 = set_json["msHeZhaTime"][2]
            b12_b15_0059 = set_json["msHeZhaTime"][0]
            temp = b12_b15_0059 * 4096 + b8_b11_0059 * 256 + b0_b7_0059
            temp = "{:04X}".format(temp)
            temp = '03060059' + temp
            temp = temp + calc_crc(temp)
            message.append(temp)
            temp = '03060058' + "{:04X}".format(set_json["msHeZhaTime"][1])
            temp = temp + calc_crc(temp)
            message.append(temp)
            temp = '0306005a' + "{:04X}".format(set_json["msFenZhaTime"][1] * 256 + set_json["msFenZhaTime"][2])
            temp = temp + calc_crc(temp)
            message.append(temp)
        #0057
        if set_json.get("ssDI1Fuc") and set_json.get("ssDI2Fuc"):
            temp = '03060057' + "{:04X}".format(set_json["ssDI2Fuc"] * 256 + set_json["ssDI1Fuc"])
            temp = temp + calc_crc(temp)
            message.append(temp)
        #007f
        if set_json.get("swDingShiFenZha") and set_json.get("swDingShiHeZha") and set_json.get("swFuZaiJianCeAct") and set_json.get("swGuoYaProAct") \
        and set_json.get("swGuoZaiProAct") and set_json.get("swLaHuProAct") and set_json.get("swLouDianProAct") and set_json.get("swQianYaProAct") \
        and set_json.get("swQueXiangProAct") and set_json.get("swShortDelayProAct") and set_json.get("swShunShiProAct") and set_json.get("swWenDuProAct")\
                and set_json.get("swYuFuFei"):
            temp = set_json["swShunShiProAct"] + 2*set_json["swShortDelayProAct"] + 4*set_json["swGuoZaiProAct"] + 8*set_json["swLouDianProAct"] + \
            16*set_json["swGuoYaProAct"] + 32*set_json["swQianYaProAct"] + 64*set_json["swWenDuProAct"] + 128*set_json["swLaHuProAct"] + \
            1024*set_json["swDingShiHeZha"] + 2048*set_json["swDingShiFenZha"] + 4096*set_json["swYuFuFei"] + 8192*set_json["swFuZaiJianCeAct"] + \
            16384*set_json["swQueXiangProAct"]
            temp = '0306007f' + "{:04X}".format(temp)
            temp = temp + calc_crc(temp)
            message.append(temp)

        print(datetime.datetime.now(), "[func:handle_readable:Parameterset](messages):", message)
        devices = models.Device.objects.filter(imei=imei)
        if devices.exists():
            ip = devices[0].ip
            temp = server.clients.copy()
            print(datetime.datetime.now(), "[func:handle_readable:Parameterset](database ip):", ip)
            send_flag = False
            for client, _ in temp.items():
                print(datetime.datetime.now(), "[func:handle_readable:Parameterset](client to send):", client)
                client_ip = str(client).split(",")[-2].split("(")[1]
                print(datetime.datetime.now(), "[func:handle_readable:Parameterset](client ip):", client_ip)
                try:
                    if client_ip == ip:
                        for m in message:
                            print(datetime.datetime.now(), "[func:handle_readable:Parameterset](message):", m)
                            client.sendall(bytes.fromhex(m))
                            send_flag = True
                except Exception as e:
                    server.clients.pop(client)
                    print(datetime.datetime.now(), "[func:handle_readable:Parameterset](result):", "---- remove error peer ----")
                    print(datetime.datetime.now(), "[func:handle_readable:Parameterset](exception):", Exception, e)
                else:
                    print(datetime.datetime.now(), "[func:handle_readable:Parameterset](result):", "---- success ----")
                    break
            if send_flag:
                recv_client.sendall(b'1')
            else:
                recv_client.sendall(b'0')

    if data[0:13] == b'remotecontrol':
        recv_client = client
        print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol]Received Remotecontrol")
        data = data.decode("utf-8")
        contrl_data = data.split(':')[1]
        imei = int(contrl_data.split('-')[0])
        index = int(contrl_data.split('-')[1])
        value = str(contrl_data.split('-')[2])
        print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol](imei):", imei)
        print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol](index, value):", index, value)
        if index == 0:
            if value == 'true':
                #03 05 00 00 01 88 CD DE
                message = ASK_FOR_CLOSE
            else:
                #03 05 00 00 02 99 0D 22
                message = ASK_FOR_OPEN
        elif index == 1:
            if value == 'true':
                message = ASK_FOR_LOCK
            else:
                message = ASK_FOR_UNLOCK
        else:
            if value == 'true':
                message = ASK_FOR_CHECK
            else:
                message = ASK_FOR_UNCHECK
        print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol](message):", message)
        devices = models.Device.objects.filter(imei=imei)
        if devices.exists():
            ip = devices[0].ip
            temp = server.clients.copy()
            print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol](database ip):", ip)
            send_flag = False
            for client, _ in temp.items():
                print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol](Client send to):", client)
                client_ip = str(client).split(",")[-2].split("(")[1]
                print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol](client ip):", client_ip)
                try:
                    if client_ip == ip:
                        print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol](send to):", message)
                        client.sendall(message)
                        send_flag = True
                except Exception as e:
                    server.clients.pop(client)
                    print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol](result):", "---- remove error peer ----")
                    print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol](exception):", Exception, e)
                else:
                    print(datetime.datetime.now(), "[func:handle_readable:Remotecontrol](result):", "---- success ----")
                    break
            if send_flag:
                recv_client.sendall(b'1')
            else:
                recv_client.sendall(b'0')

    elif len(data) == 7: #获取版本号
        print(datetime.datetime.now(), "[func:handle_readable:Version]Received Version")
        ip = models.Device.objects.filter(ip=str_ip)
        if ip.exists():
            soft_version = num_to_str(data[3])
            soft_version = "V"+soft_version[1]+"."+soft_version[0]
            ip[0].soft_version = soft_version
            ip[0].save()
    elif len(data) == 15 and data.decode().isdigit():
        print(datetime.datetime.now(), "[func:handle_readable:IMEI]Received IMEI")
        str_data = data.decode()
        print(datetime.datetime.now(), "[func:handle_readable:IMEI](strdata):", str_data)
        imei = models.Device.objects.filter(imei=str_data)
        if imei.exists():
            device = models.Device.objects.get(imei = str_data)
            device.ip = str_ip
            device.port = str_port
            device.save()
        else: #如果imei未注册
            get_version_code = ASK_FOR_VERSION
            client.sendall(get_version_code)
            #version_code = client.recv(1028)
            #str_version_code = version_code.decode()
            str_version_code = "V1.4"
            models.Device.objects.create(imei = str_data, ip = str_ip,port = str_port, device_version="V1.0.0", soft_version = str_version_code, time = time.time())
    #时间上报
    elif len(data) == 35 and data[0] == 3 and data[1] == 3:
        print(datetime.datetime.now(), "[func:handle_readable:Upload]Received Upload")
        devices = models.Device.objects.filter(ip=str_ip)
        if devices.exists():
            if num_to_str(data[28]) == "00" or num_to_str(data[29]) == "00":
                return
            else:
                upload_time = time_stamp_trans("20"+num_to_str(data[27])+"-"+num_to_str(data[28])+"-"+num_to_str(data[29])+"-"+num_to_str(data[30])+"-"+num_to_str(data[31])+"-"+num_to_str(data[32]))
            uploads = models.Upload.objects.filter(imei = devices[0])
            if uploads.exists():
                if upload_time <= uploads[len(uploads) - 1].time:
                    return
            upload = models.Upload()
            upload.imei = devices[0]
            upload.Ileakage = float((data[3]*16*16 + data[4])*0.01)
            upload.IA = float((data[5]*16*16 + data[6])*0.01)
            upload.IB = float((data[7]*16*16 + data[8])*0.01)
            upload.IC = float((data[9]*16*16 + data[10])*0.01)
            upload.UA = float((data[11]*16*16 + data[12])*0.1)
            upload.UB = float((data[13]*16*16 + data[14])*0.1)
            upload.UC = float((data[15]*16*16 + data[16])*0.1)
            upload.TA = float((data[17]*16*16 + data[18]))
            upload.TB = float((data[19]*16*16 + data[20]))
            upload.TC = float((data[21]*16*16 + data[22]))
            #合分闸标志位检测
            upload.on_off = int(data[23]*16*16 + data[24])
            #on_off = bin(data[23]*16*16 + data[24])
            #upload.on_off = on_off_trans(on_off[2:])
            #错误码标志位检测
            error_code = bin(data[25]*16*16 + data[26])
            if error_code[2:] != "0":
                get_warning_code = ASK_FOR_WARNING  #03 0B 00 26 00 01 85 E2
                client.sendall(get_warning_code)
            #upload.error_code = error_code_trans(error_code[2:])
            upload.error_code = int(data[25]*16*16 + data[26])
            upload.time = upload_time
            upload.save()
    #故障
    elif len(data) == 33 and data[0] == 3 and data[1] == 3:
        print(datetime.datetime.now(), "[func:handle_readable:Warning]Received Warning")
        ip = models.Device.objects.filter(ip=str_ip)
        if ip.exists():
            warning = models.Warning()
            warning.imei = ip[0]
            #on_off = bin(data[3] * 16 * 16 + data[4])
            #warning.on_off = on_off_trans(on_off[2:])
            #fault_type = bin(data[5] * 16 * 16 + data[6])
            #warning.fault_type = error_code_trans(fault_type[2:])
            warning.on_off = int(data[3] * 16 * 16 + data[4])
            warning.fault_type = int(data[5] * 16 * 16 + data[6])
            '''
            if data[8] == 0:
                fault_phase = "A"
            elif data[8] == 1:
                fault_phase = "B"
            elif data[8] == 2:
                fault_phase = "C"
            else:
                fault_phase = ""
            warning.fault_phase = fault_phase
            '''
            warning.time = time.time()
            warning.fault_phase = data[8]
            warning.delay_time = float((data[9] * 16 * 16 + data[10]) * 20)
            warning.IA = float((data[11] * 16 * 16 + data[12]) * 0.01)
            warning.IB = float((data[13] * 16 * 16 + data[14]) * 0.01)
            warning.IC = float((data[15] * 16 * 16 + data[16]) * 0.01)
            warning.Ileakage = float((data[17] * 16 * 16 + data[18]) * 0.01)
            warning.UA = float((data[19] * 16 * 16 + data[20]) * 0.1)
            warning.UB = float((data[21] * 16 * 16 + data[22]) * 0.1)
            warning.UC = float((data[23] * 16 * 16 + data[24]) * 0.1)
            warning.TA = float((data[25] * 16 * 16 + data[26]) * 1)
            warning.TB = float((data[27] * 16 * 16 + data[28]) * 1)
            warning.TC = float((data[29] * 16 * 16 + data[30]) * 1)
            warning.save()
    #2 + (n-1)*2 + 1
    elif len(data) == 195 and data[0] == 3 and data[1] == 3:
        print(datetime.datetime.now(), "[func:handle_readable:Data]Received Data")
        ip = models.Device.objects.filter(ip=str_ip)
        if ip.exists():
            data_object = models.Data()
            data_object.imei = ip[0]
            data_object.time = time.time()
            data_object.Ileakage = float((data[3] * 16 * 16 + data[4]) * 0.01) #1
            data_object.I1 = float((data[5] * 16 * 16 + data[6]) * 0.01)  #2
            data_object.I2 = float((data[7] * 16 * 16 + data[8]) * 0.01)
            data_object.I3 = float((data[9] * 16 * 16 + data[10]) * 0.01)
            data_object.U1 = float((data[11] * 16 * 16 + data[12]) * 0.1)
            data_object.U2 = float((data[13] * 16 * 16 + data[14]) * 0.1)
            data_object.U3 = float((data[15] * 16 * 16 + data[16]) * 0.1)
            data_object.TA = float((data[17] * 16 * 16 + data[18]) * 1)
            data_object.TB = float((data[19] * 16 * 16 + data[20]) * 1)
            data_object.TC = float((data[21] * 16 * 16 + data[22]) * 1)
            data_object.PA = float((data[115] * 16 * 16 + data[116]) * 1)  # 57
            data_object.PB = float((data[117] * 16 * 16 + data[118]) * 1)
            data_object.PC = float((data[119] * 16 * 16 + data[120]) * 1)
            data_object.PT = float((data[121] * 16 * 16 + data[122]) * 1)
            data_object.QA = float((data[123] * 16 * 16 + data[124]) * 1)
            data_object.QB = float((data[125] * 16 * 16 + data[126]) * 1)
            data_object.QC = float((data[127] * 16 * 16 + data[128]) * 1)
            data_object.QT = float((data[129] * 16 * 16 + data[130]) * 1)
            data_object.SA = float((data[131] * 16 * 16 + data[132]) * 1)
            data_object.SB = float((data[133] * 16 * 16 + data[134]) * 1)
            data_object.SC = float((data[135] * 16 * 16 + data[136]) * 1)
            data_object.ST = float((data[137] * 16 * 16 + data[138]) * 1)
            data_object.PFA = float((data[139] * 16 * 16 + data[140]) * 0.01)
            data_object.PFB = float((data[141] * 16 * 16 + data[142]) * 0.01)
            data_object.PFC = float((data[143] * 16 * 16 + data[144]) * 0.01)
            data_object.PF = float((data[145] * 16 * 16 + data[146]) * 0.01)
            data_object.FREQ = float((data[147] * 16 * 16 + data[148]) * 0.01)
            data_object.WPosAc = float((data[149] * 16 * 16 * 16 * 16 + data[150] * 16 * 16 * 16 + data[151] * 16 * 16 + data[152]) * 0.1)
            data_object.WPosRe = float((data[153] * 16 * 16 * 16 * 16 + data[154] * 16 * 16 * 16 + data[155] * 16 * 16 + data[156]) * 0.1)
            data_object.WRevAc = float((data[157] * 16 * 16 * 16 * 16 + data[158] * 16 * 16 * 16 + data[159] * 16 * 16 + data[160]) * 0.1)
            data_object.WRevRe = float((data[161] * 16 * 16 * 16 * 16 + data[162] * 16 * 16 * 16 + data[163] * 16 * 16 + data[164]) * 0.1)
            data_object.save()
    else:
        pass
    #client.sendall(b'SERVER: ' + data)
    return True

def get_data():
    print(datetime.datetime.now(), "[func:get_data]Ask for Data")
    temp = server.clients.copy()
    for client, _ in temp.items():
        try:
            print(datetime.datetime.now(), "[func:get_data](client):", client)
            client.sendall(ASK_FOR_ALL)
        except Exception as e:
            print(datetime.datetime.now(), "[func:get_data](result):", "----remove error peer----")
            print(datetime.datetime.now(), "[func:get_data](exception):", Exception, e)
            server.clients.pop(client)
        else:
            print(datetime.datetime.now(), "[func:get_data](result):", "----success----")
            pass


def run_threaded(job_func, server):
    job_thread = threading.Thread(target=job_func, args=(server,))
    job_thread.start()


server = esockets.SocketServer(port = 2333, host = "0.0.0.0", handle_incoming=handle_incoming,
                               handle_readable=handle_readable)
server.start()
print(datetime.datetime.now(),'[func:main:server](started on): {}:{}'.format(server.host, server.port))

schedule.every(15).minutes.do(get_data)
while True:
    schedule.run_pending()
