import numpy as np
from PIL import Image
from scipy.stats import pearsonr

class WatermarkDetector:
    def __init__(self):
        self.threshold = 0.7  # 相关系数阈值
        
    def detect(self, original_watermark, extracted_watermark):
        # 转换为numpy数组
        original_array = np.array(original_watermark).flatten()
        extracted_array = np.array(extracted_watermark).flatten()
        
        # 计算相关系数
        correlation, _ = pearsonr(original_array, extracted_array)
        
        # 判断是否检测到水印
        is_detected = correlation > self.threshold
        
        return is_detected, correlation 