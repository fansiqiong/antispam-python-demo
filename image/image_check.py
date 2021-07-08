#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
易盾反垃圾云服务图片在线检测接口python示例代码
接口文档: http://dun.163.com/api.html
python版本：python3.7
运行:
    1. 修改 SECRET_ID,SECRET_KEY,BUSINESS_ID 为对应申请到的值
    2. $ python image_check.py
"""
__author__ = 'yidun-dev'
__date__ = '2019/11/27'
__version__ = '0.2-dev'

import hashlib
import time
import random
import urllib.request as urlrequest
import urllib.parse as urlparse
import json
from gmssl import sm3, func

class ImageCheckAPIDemo(object):
    """图片在线检测接口示例代码"""

    API_URL = "http://as.dun.163.com/v4/image/check"
    VERSION = "v4"

    def __init__(self, secret_id, secret_key, business_id):
        """
        Args:
            secret_id (str) 产品密钥ID，产品标识
            secret_key (str) 产品私有密钥，服务端生成签名信息使用
            business_id (str) 业务ID，易盾根据产品业务特点分配
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.business_id = business_id

    def gen_signature(self, params=None):
        """生成签名信息
        Args:
            params (object) 请求参数
        Returns:
            参数签名md5值
        """
        buff = ""
        for k in sorted(params.keys()):
            buff += str(k) + str(params[k])
        buff += self.secret_key
        if "signatureMethod" in params.keys() and params["signatureMethod"] == "SM3":
            return sm3.sm3_hash(func.bytes_to_list(bytes(buff, encoding='utf8')))
        else:
            return hashlib.md5(buff.encode("utf8")).hexdigest()

    def check(self, params):
        """请求易盾接口
        Args:
            params (object) 请求参数
        Returns:
            请求结果，json格式
        """
        params["secretId"] = self.secret_id
        params["businessId"] = self.business_id
        params["version"] = self.VERSION
        params["timestamp"] = int(time.time() * 1000)
        params["nonce"] = int(random.random() * 100000000)
        # params["signatureMethod"] = "SM3"  # 签名方法，默认MD5，支持SM3
        params["signature"] = self.gen_signature(params)

        try:
            params = urlparse.urlencode(params).encode("utf8")
            request = urlrequest.Request(self.API_URL, params)
            content = urlrequest.urlopen(request, timeout=10).read()
            return json.loads(content)
        except Exception as ex:
            print("调用API接口失败:", str(ex))

def data_preprocess():
    infile = "INPUT_DATASET_PATH"
    dataList: list=[]
    with open(infile) as f:
        dataset = json.load(f)
        for item in dataset:
            # type = 1: url(单次上限 100 张)
            # type = 2: base64(单次上限 10M)
            data = dict({"name": item['url'], "type": 1, "data": item['url']})
            dataList.append(data)
    return dataList

if __name__ == "__main__":
    """示例代码入口"""
    SECRET_ID = "your_secret_id"  # 产品密钥ID，产品标识
    SECRET_KEY = "your_secret_key"  # 产品私有密钥，服务端生成签名信息使用，请严格保管，避免泄露
    BUSINESS_ID = "your_business_id"  # 业务ID，易盾根据产品业务特点分配
    api = ImageCheckAPIDemo(SECRET_ID, SECRET_KEY, BUSINESS_ID)

    # 私有请求参数
    images = data_preprocess()
    params = {
        "images": json.dumps(images)
        # "account": "python@163.com"
        # "ip": "123.115.77.137"
    }

    ret = api.check(params)

    code: int = ret["code"]
    msg: str = ret["msg"]
    if code == 200:
        # 图片反垃圾结果
        antispamArray: list = ret["antispam"]
        for antispamResult in antispamArray:
            name: str = antispamResult["name"]
            taskId: str = antispamResult["taskId"]
            status: int = antispamResult["status"]
            # 图片检测状态码，定义为：0：检测成功，610：图片下载失败，620：图片格式错误，630：其它
            if status == 0:
                # 图片维度结果
                action: int = antispamResult["action"]
                labelArray: list = antispamResult["labels"]
                print("taskId: %s, status: %s, name: %s, action: %s" % (taskId, status, name, action))
                # 产品需根据自身需求，自行解析处理，本示例只是简单判断分类级别
                for labelItem in labelArray:
                    label: int = labelItem["label"]
                    level: int = labelItem["level"]
                    rate: float = labelItem["rate"]
                    subLabels: list = labelItem["subLabels"]
                    print("label: %s, level: %s, rate: %s, subLabels: %s" % (label, level, rate, subLabels))
                if action == 0:
                    print("#图片机器检测结果: 最高等级为\"正常\"\n")
                elif action == 1:
                    print("#图片机器检测结果: 最高等级为\"嫌疑\"\n")
                elif action == 2:
                    print("#图片机器检测结果: 最高等级为\"确定\"\n")
            else:
                # status对应失败状态码：610：图片下载失败，620：图片格式错误，630：其它
                print("图片检测失败, taskId: %s, status: %s, name: %s" % (taskId, status, name))
        # 图片OCR结果
        ocrArray: list = ret["ocr"]
        for ocrResult in ocrArray:
            name: str = ocrResult["name"]
            taskId: str = ocrResult["taskId"]
            details: list = ocrResult["details"]
            print("taskId: %s, name: %s" % (taskId, name))
            # 产品需根据自身需求，自行解析处理，本示例只是简单输出ocr结果信息
            for detail in details:
                content: str = detail["content"]
                lineContents: list = detail["lineContents"]
                print("识别ocr文本内容: %s, ocr片段及坐标信息: %s" % (content, lineContents))
        # 图片人脸检测结果
        faceArray: list = ret["face"]
        for faceResult in faceArray:
            name: str = faceResult["name"]
            taskId: str = faceResult["taskId"]
            details: list = faceResult["details"]
            print("taskId: %s, name: %s" % (taskId, name))
            # 产品需根据自身需求，自行解析处理，本示例只是简单输出人脸结果信息
            for detail in details:
                faceNumber: int = detail["faceNumber"]
                faceContents: list = detail["faceContents"]
                print("识别人脸数量: %s, 人物信息及坐标信息: %s" % (faceNumber, faceContents))
        # 图片质量检测结果
        qualityArray: list = ret["quality"]
        for qualityResult in qualityArray:
            name: str = qualityResult["name"]
            taskId: str = qualityResult["taskId"]
            details: list = qualityResult["details"]
            print("taskId: %s, name: %s" % (taskId, name))
            # 产品需根据自身需求，自行解析处理，本示例只是简单输出质量结果信息
            for detail in details:
                aestheticsRate: float = detail["aestheticsRate"]
                metaInfo: dict = detail["metaInfo"]
                boarderInfo: dict = detail["boarderInfo"]
                print("图片美观度分数:%s, 图片基本信息:%s, 图片边框信息:%s" % (aestheticsRate, metaInfo, boarderInfo))

    else:
        print("ERROR: code=%s, msg=%s" % (ret["code"], ret["msg"]))
