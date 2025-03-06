# =================================
# @Time    : 2025年03月06日
# @Author  : 明廷盛
# @File    : font_ocr.py
# @Software: PyCharm
# @ProjectBackground: $END$
# =================================
import time

import tempfile

import os
from fontTools.ttLib import TTFont
from lxml import etree
from loguru import logger
import ddddocr
import matplotlib.pyplot as plt


class FontSpiderOCR:
    def __init__(self, woff_file_path):
        self.woff_file_path = woff_file_path
        # 提取纯文件名（不带路径和扩展名）
        base_name = os.path.basename(woff_file_path)  # 处理绝对路径
        self.woff_file_name = os.path.splitext(base_name)[0]

        # 创建临时目录对象并保留引用  删除时: temp_dir_obj.cleanup() 可以不删除缓存文件 ignore_cleanup_errors=True python3.0+
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.cache_path = self.temp_dir_obj.name
        logger.info(f"缓存路径为 {self.cache_path}")

        # 使用os.path.join确保跨平台兼容性
        self.xml_file_path = os.path.join(self.cache_path, f"{self.woff_file_name}.xml")
        TTFont(self.woff_file_path).saveXML(self.xml_file_path)


    def DDDDOCR_OCR(self, image):
        ocr = ddddocr.DdddOcr(show_ad=False)
        res = 0 if ocr.classification(image) == "D" else ocr.classification(image)
        return res

    def pic_ocr(self, TTGlyph_name):
        # 读取图片
        pic_path = os.path.join(self.cache_path, f"{TTGlyph_name[0]}.png")
        with open(pic_path, 'rb') as f:
            image = f.read()
        # OCR识别
        return self.DDDDOCR_OCR(image)  # 1.DDDDOCR_OCR进行识别

    def paint(self, xy_list, TTGlyph_name):
        plt.figure(figsize=(10, 10))
        # 遍历每个图案
        for shape in xy_list:
            # 提取 x 和 y 坐标
            x, y = zip(*[(int(point[0]), int(point[1])) for point in shape])

            # 绘制多边形
            plt.plot(x, y, marker='o')  # 连接点的多边形
            plt.fill(x, y, alpha=0.3)  # 填充多边形
        plt.xticks([])  # 隐藏x轴刻度标签
        plt.yticks([])
        # 设置绘图属性
        plt.axis('equal')  # 坐标轴比例一致
        plt.grid(True)
        pic_path = os.path.join(self.cache_path, f"{TTGlyph_name[0]}.png")
        plt.savefig(pic_path)

    def parse_font(self, tt):
        if tt.xpath('./contour[1]'):
            xy_list = []
            TTGlyph_name = tt.xpath('./@name')
            contour_list = tt.xpath('./contour')
            for contour in contour_list:
                TTGlyph_xy = [(x, y) for x, y in zip(contour.xpath('./pt/@x'), contour.xpath('./pt/@y'))]
                TTGlyph_xy.append(TTGlyph_xy[0])
                xy_list.append(TTGlyph_xy)

            self.paint(xy_list, TTGlyph_name)
            res = self.pic_ocr(TTGlyph_name)
            return (TTGlyph_name[0], res)

    def get_mapping(self, type):
        """
        :param type:"字码点"(cmap_name)作为键, "字形"(glyf_name)作为键
        :return: 返回的值都是识别后的数据
        """
        ziti = {}
        # STEP1:xpath解析xml文件
        with open(self.xml_file_path, "r") as f:
            # print(f.read())
            xml_content = etree.fromstring(f.read().encode("utf-8"))
            cmap_mapping = {g.get('name'): g.get('code') for g in xml_content.xpath("//map")}
            # print(cmap_mapping)
            # OCR映射字体
            TTGlyph_list = xml_content.xpath('//glyf/TTGlyph')
            for tt in TTGlyph_list[1:-1]:
                key, value = self.parse_font(tt)
                ziti[key] = value
            if type == "glyf_name":
                return ziti
            elif type == "cmap_name":
                cmap_ziti = {cmap_mapping[glyf_k]: v for glyf_k, v in ziti.items()}
                return cmap_ziti


