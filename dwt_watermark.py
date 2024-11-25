import numpy as np
import pywt
from PIL import Image
from PIL import ImageFilter

class DWTWatermark:
    def __init__(self):
        self.alpha = 0.01  # 进一步降低水印强度因子
        
    def embed(self, host_image, watermark):
        # 转换为numpy数组
        host_array = np.array(host_image).astype(np.float32)
        
        # 对主图像进行3级小波变换，增加隐藏深度
        coeffs2 = pywt.wavedec2(host_array, 'haar', level=3)
        
        # 获取第三级的所有子带
        LL3 = coeffs2[0]
        (LH3, HL3, HH3) = coeffs2[1]
        
        # 将水印调整为LL3子带的大小
        watermark = watermark.resize((LL3.shape[1], LL3.shape[0]), Image.Resampling.LANCZOS)
        watermark_array = np.array(watermark).astype(np.float32)
        
        # 将水印归一化到[-1,1]范围
        watermark_array = (watermark_array / 255.0 * 2) - 1
        
        # 在多个子带中分散嵌入水印，使用不同的强度
        LL3_watermarked = LL3 * (1 + self.alpha * watermark_array)
        LH3_watermarked = LH3 * (1 + self.alpha * 0.5 * watermark_array)
        HL3_watermarked = HL3 * (1 + self.alpha * 0.5 * watermark_array)
        
        # 更新系数
        coeffs2[0] = LL3_watermarked
        coeffs2[1] = (LH3_watermarked, HL3_watermarked, HH3)
        
        # 逆变换
        watermarked = pywt.waverec2(coeffs2, 'haar')
        
        # 确保像素值在有效范围内，使用更平滑的裁剪
        watermarked = np.clip(watermarked, 0, 255)
        
        # 平滑处理，减少可能的锯齿
        watermarked_image = Image.fromarray(watermarked.astype(np.uint8))
        watermarked_image = watermarked_image.filter(ImageFilter.SMOOTH)
        
        return watermarked_image
    
    def extract(self, watermarked_image, original_image, watermark_size):
        # 转换为numpy数组
        watermarked_array = np.array(watermarked_image).astype(np.float32)
        original_array = np.array(original_image).astype(np.float32)
        
        # 对两个图像进行3级小波变换
        w_coeffs2 = pywt.wavedec2(watermarked_array, 'haar', level=3)
        o_coeffs2 = pywt.wavedec2(original_array, 'haar', level=3)
        
        # 获取第三级子带
        w_LL3 = w_coeffs2[0]
        o_LL3 = o_coeffs2[0]
        w_LH3, w_HL3, _ = w_coeffs2[1]
        o_LH3, o_HL3, _ = o_coeffs2[1]
        
        # 从多个子带提取水印并组合
        extracted_LL = (w_LL3 / (o_LL3 + 1e-8) - 1) / self.alpha
        extracted_LH = (w_LH3 / (o_LH3 + 1e-8) - 1) / (self.alpha * 0.5)
        extracted_HL = (w_HL3 / (o_HL3 + 1e-8) - 1) / (self.alpha * 0.5)
        
        # 组合提取结果
        extracted = (extracted_LL + extracted_LH + extracted_HL) / 3
        
        # 调整像素范围到[0,255]
        extracted = ((extracted + 1) / 2) * 255
        extracted = np.clip(extracted, 0, 255)
        
        # 对提取结果进行去噪和增强
        # 使用更复杂的自适应阈值
        mean_val = np.mean(extracted)
        std_val = np.std(extracted)
        threshold = mean_val + 0.2 * std_val  # 降低阈值敏感度
        
        extracted = np.where(extracted > threshold, 255, 0)
        
        # 转换为图像并调整大小
        extracted_image = Image.fromarray(extracted.astype(np.uint8))
        extracted_image = extracted_image.resize(watermark_size, Image.Resampling.LANCZOS)
        
        # 对提取的水印进行后处理
        extracted_image = extracted_image.filter(ImageFilter.SMOOTH)
        
        return extracted_image 