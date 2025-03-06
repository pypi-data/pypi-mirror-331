# xi_font_spider_ocr

## 下载

```bash
pip install font_ocr
```

## 如何使用

```python
from font_ocr import FontSpiderOCR

if __name__ == '__main__':
    font_spider_oce = FontSpiderOCR(r"font.woff")  # 文件路径
    print(font_spider_oce.get_mapping("cmap_name"))  # 字码点为键
    print(font_spider_oce.get_mapping("glyf_name"))  # 字形为键, 值都是OCR识别后的数据
```