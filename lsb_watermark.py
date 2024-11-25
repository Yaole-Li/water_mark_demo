import numpy as np
from PIL import Image

class LSBWatermark:
    def __init__(self):
        pass
    
    def embed(self, host_image, watermark):
        # 确保输入是numpy数组
        host_array = np.array(host_image)
        
        # 将水印调整为与载体图像相同的大小
        watermark = watermark.resize((host_array.shape[1], host_array.shape[0]), Image.Resampling.LANCZOS)
        watermark_array = np.array(watermark)
        
        # 将水印二值化 - 修改阈值处理逻辑
        watermark_binary = (watermark_array > 128).astype(np.uint8)  # 修改这里，从 < 改为 >
        
        # 获取原始图像的最低位平面
        host_lsb = host_array & 0xFE
        
        # 嵌入水印
        watermarked = host_lsb | watermark_binary
        
        return Image.fromarray(watermarked)
    
    def extract(self, watermarked_image, watermark_size):
        # 提取最低位平面
        watermarked_array = np.array(watermarked_image)
        extracted = (watermarked_array & 0x01) * 255
        
        # 调整大小以匹配原始水印尺寸
        extracted_image = Image.fromarray(extracted.astype(np.uint8))
        extracted_image = extracted_image.resize(watermark_size, Image.Resampling.LANCZOS)
        
        return extracted_image 