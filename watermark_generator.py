import numpy as np
from PIL import Image, ImageDraw, ImageFont

class WatermarkGenerator:
    def __init__(self):
        pass
    
    def generate_text_watermark(self, text, size=(100, 30)):
        # 创建一个新的白色背景图像
        watermark = Image.new('L', size, 255)
        draw = ImageDraw.Draw(watermark)
        
        # 使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
            
        # 获取文本大小
        text_width = draw.textlength(text, font=font)
        text_height = 20
        
        # 计算文本位置使其居中
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # 绘制黑色文本
        draw.text((x, y), text, fill=0, font=font)
        
        return np.array(watermark)
    
    def generate_image_watermark(self, image_path, size=(100, 100)):
        # 从文件加载水印图像
        watermark = Image.open(image_path).convert('L')
        watermark = watermark.resize(size)
        
        return np.array(watermark) 