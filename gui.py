import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

from watermark_generator import WatermarkGenerator
from lsb_watermark import LSBWatermark
from dwt_watermark import DWTWatermark
from watermark_detector import WatermarkDetector

class WatermarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("数字水印系统")
        
        # 初始化组件
        self.generator = WatermarkGenerator()
        self.lsb_watermark = LSBWatermark()
        self.dwt_watermark = DWTWatermark()
        self.detector = WatermarkDetector()
        
        # 存储路径和图像
        self.host_image_path = None
        self.watermark_path = None
        self.watermarked_image = None
        self.original_watermark = None
        self.host_image = None
        self.to_extract_image = None
        self.to_detect_image = None  # 新增：用于存储待检测的图像
        
        self.create_widgets()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建左右两个主要区域
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, padx=5, sticky=(tk.N, tk.S))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, padx=5, sticky=(tk.N, tk.S))
        
        # 在左侧区域创建功能框架（竖向排列）
        # 1. 水印生成框架
        generate_frame = ttk.LabelFrame(left_frame, text="水印生成", padding="5")
        generate_frame.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # 水印类型选择
        ttk.Label(generate_frame, text="水印类型:").grid(row=0, column=0, sticky=tk.W)
        self.watermark_type = tk.StringVar(value="text")
        ttk.Radiobutton(generate_frame, text="文本", variable=self.watermark_type, 
                       value="text").grid(row=0, column=1)
        ttk.Radiobutton(generate_frame, text="图像", variable=self.watermark_type, 
                       value="image").grid(row=0, column=2)
        
        # 文本水印输入
        ttk.Label(generate_frame, text="水印文本:").grid(row=1, column=0, sticky=tk.W)
        self.watermark_text = tk.StringVar()
        ttk.Entry(generate_frame, textvariable=self.watermark_text).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        # 水印大小设置
        ttk.Label(generate_frame, text="水印大小:").grid(row=2, column=0, sticky=tk.W)
        size_frame = ttk.Frame(generate_frame)
        size_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        self.width_var = tk.StringVar(value="100")
        self.height_var = tk.StringVar(value="30")
        ttk.Entry(size_frame, textvariable=self.width_var, width=5).pack(side=tk.LEFT)
        ttk.Label(size_frame, text="x").pack(side=tk.LEFT, padx=2)
        ttk.Entry(size_frame, textvariable=self.height_var, width=5).pack(side=tk.LEFT)
        
        ttk.Button(generate_frame, text="生成水印", 
                  command=self.generate_watermark).grid(row=3, column=0, columnspan=3, pady=5)
        
        # 2. 水印嵌入框架
        embed_frame = ttk.LabelFrame(left_frame, text="水印嵌入", padding="5")
        embed_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(embed_frame, text="选择算法:").grid(row=0, column=0, sticky=tk.W)
        self.algorithm_var = tk.StringVar(value="LSB")
        ttk.Radiobutton(embed_frame, text="LSB", variable=self.algorithm_var, 
                       value="LSB").grid(row=0, column=1)
        ttk.Radiobutton(embed_frame, text="DWT", variable=self.algorithm_var, 
                       value="DWT").grid(row=0, column=2)
        
        ttk.Button(embed_frame, text="选择载体图像", 
                  command=self.load_host_image).grid(row=1, column=0, columnspan=3, pady=5)
        ttk.Button(embed_frame, text="选择水印图像", 
                  command=self.load_watermark).grid(row=2, column=0, columnspan=3, pady=5)
        ttk.Button(embed_frame, text="嵌入水印", 
                  command=self.embed_watermark).grid(row=3, column=0, columnspan=3, pady=5)
        
        # 3. 水印提取框架
        extract_frame = ttk.LabelFrame(left_frame, text="水印提取", padding="5")
        extract_frame.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(extract_frame, text="选择待提取图像", 
                  command=self.load_extract_image).grid(row=0, column=0, pady=5)
        ttk.Button(extract_frame, text="提取水印", 
                  command=self.extract_watermark).grid(row=1, column=0, pady=5)
        
        # 4. 水印检测框架
        detect_frame = ttk.LabelFrame(left_frame, text="水印检测", padding="5")
        detect_frame.grid(row=3, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(detect_frame, text="选择待检测图片", 
                  command=self.load_detect_image).grid(row=0, column=0, pady=5)
        ttk.Button(detect_frame, text="选择目标水印", 
                  command=self.load_target_watermark).grid(row=1, column=0, pady=5)
        ttk.Button(detect_frame, text="水印检测", 
                  command=self.detect_watermark).grid(row=2, column=0, pady=5)
        
        # 在右侧区域创建图像预览框架
        preview_frame = ttk.LabelFrame(right_frame, text="图像预览", padding="5")
        preview_frame.grid(row=0, column=0, sticky=(tk.N, tk.S))
        
        # 图像显示（垂直排列）
        self.host_label = ttk.Label(preview_frame)
        self.host_label.grid(row=0, column=0, pady=5)
        
        self.watermark_label = ttk.Label(preview_frame)
        self.watermark_label.grid(row=1, column=0, pady=5)
        
        self.result_label = ttk.Label(preview_frame)
        self.result_label.grid(row=2, column=0, pady=5)
        
        # 文件名显示标签（垂直排列）
        self.host_filename_label = ttk.Label(preview_frame, text="载体图像: 未选择")
        self.host_filename_label.grid(row=3, column=0, pady=2)
        
        self.watermark_filename_label = ttk.Label(preview_frame, text="水印图像: 未选择")
        self.watermark_filename_label.grid(row=4, column=0, pady=2)
        
        self.result_filename_label = ttk.Label(preview_frame, text="结果图像: 未生成")
        self.result_filename_label.grid(row=5, column=0, pady=2)
        
    def load_host_image(self):
        self.host_image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.bmp *.gif *.tiff")])
        if self.host_image_path:
            self.host_image = Image.open(self.host_image_path).convert('L')
            display_image = self.host_image.copy()
            display_image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(display_image)
            self.host_label.configure(image=photo)
            self.host_label.image = photo
            # 显示文件名
            filename = os.path.basename(self.host_image_path)
            self.host_filename_label.configure(text=f"载体图像: {filename}")
            
    def load_watermark(self):
        self.watermark_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.bmp *.gif *.tiff")])
        if self.watermark_path:
            self.original_watermark = Image.open(self.watermark_path).convert('L')
            display_image = self.original_watermark.copy()
            display_image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(display_image)
            self.watermark_label.configure(image=photo)
            self.watermark_label.image = photo
            # 显示文件名
            filename = os.path.basename(self.watermark_path)
            self.watermark_filename_label.configure(text=f"水印图像: {filename}")
            
    def load_extract_image(self):
        extract_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.bmp *.gif *.tiff")])
        if extract_path:
            self.to_extract_image = Image.open(extract_path).convert('L')
            display_image = self.to_extract_image.copy()
            display_image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(display_image)
            self.host_label.configure(image=photo)
            self.host_label.image = photo
            
    def load_detect_image(self):
        """加载待检测的图像"""
        detect_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.bmp *.gif *.tiff")])
        if detect_path:
            self.to_detect_image = Image.open(detect_path).convert('L')
            display_image = self.to_detect_image.copy()
            display_image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(display_image)
            self.host_label.configure(image=photo)
            self.host_label.image = photo
    
    def load_target_watermark(self):
        """加载目标水印图像"""
        target_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.bmp *.gif *.tiff")])
        if target_path:
            self.target_watermark = Image.open(target_path).convert('L')
            display_image = self.target_watermark.copy()
            display_image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(display_image)
            self.watermark_label.configure(image=photo)
            self.watermark_label.image = photo
    
    def embed_watermark(self):
        if not self.host_image_path or not self.watermark_path:
            messagebox.showerror("错误", "请先选择载体图像和水印图像")
            return
            
        algorithm = self.algorithm_var.get()
        if algorithm == "LSB":
            self.watermarked_image = self.lsb_watermark.embed(self.host_image, self.original_watermark)
        else:
            self.watermarked_image = self.dwt_watermark.embed(self.host_image, self.original_watermark)
            
        display_image = self.watermarked_image.copy()
        display_image.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(display_image)
        self.result_label.configure(image=photo)
        self.result_label.image = photo
        
        # 生成带算法标识的文件名
        output_filename = f"watermarked_image_{algorithm}.png"
        self.watermarked_image.save(output_filename)
        self.result_filename_label.configure(text=f"结果图像: {output_filename}")
        messagebox.showinfo("成功", f"水印已嵌入并保存为{output_filename}")
        
    def extract_watermark(self):
        if not self.to_extract_image:
            messagebox.showerror("错误", "请先选择待提取的图像")
            return
            
        if not self.original_watermark:
            messagebox.showerror("错误", "请先选择原始水印图像以获取尺寸信息")
            return
            
        watermark_size = self.original_watermark.size
        algorithm = self.algorithm_var.get()
        
        if algorithm == "LSB":
            extracted = self.lsb_watermark.extract(self.to_extract_image, watermark_size)
        else:
            if not self.host_image:
                messagebox.showerror("错误", "DWT算法需要选择原始载体图像")
                return
            extracted = self.dwt_watermark.extract(self.to_extract_image, self.host_image, watermark_size)
            
        display_image = extracted.copy()
        display_image.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(display_image)
        self.result_label.configure(image=photo)
        self.result_label.image = photo
        
        # 生成带算法标识的文件名
        output_filename = f"extracted_watermark_{algorithm}.png"
        extracted.save(output_filename)
        self.result_filename_label.configure(text=f"结果图像: {output_filename}")
        messagebox.showinfo("成功", f"水印已提取并保存为{output_filename}")
        
    def detect_watermark(self):
        """检测图像中是否包含目标水印"""
        if not self.to_detect_image:
            messagebox.showerror("错误", "请先选择待检测的图像")
            return
            
        if not hasattr(self, 'target_watermark'):
            messagebox.showerror("错误", "请先选择目标水印")
            return
        
        # 从待检测图像中提取水印
        watermark_size = self.target_watermark.size
        
        if self.algorithm_var.get() == "LSB":
            extracted = self.lsb_watermark.extract(self.to_detect_image, watermark_size)
        else:
            # DWT算法需要原始图像，这里可能需要调整检测策略
            messagebox.showerror("错误", "当前版本DWT算法不支持直接检测")
            return
            
        # 检测提取的水印与目标水印的相似度
        is_detected, correlation = self.detector.detect(self.target_watermark, extracted)
        
        # 显示提取的水印
        display_image = extracted.copy()
        display_image.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(display_image)
        self.result_label.configure(image=photo)
        self.result_label.image = photo
        
        if is_detected:
            message = f"检测到目标水印！\n相关系数: {correlation:.3f}"
        else:
            message = f"未检测到目标水印\n相关系数: {correlation:.3f}"
            
        messagebox.showinfo("检测结果", message)
    
    def generate_watermark(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            watermark_type = self.watermark_type.get()
            if watermark_type == "text":
                if not self.watermark_text.get():
                    messagebox.showerror("错误", "请输入水印文本")
                    return
                    
                watermark = self.generator.generate_text_watermark(
                    self.watermark_text.get(), 
                    size=(width, height)
                )
                type_str = "text"
            else:
                image_path = filedialog.askopenfilename(
                    filetypes=[("Image files", "*.png *.jpg *.bmp *.gif *.tiff")])
                if not image_path:
                    return
                    
                watermark = self.generator.generate_image_watermark(
                    image_path, 
                    size=(width, height)
                )
                type_str = "image"
            
            self.original_watermark = Image.fromarray(watermark)
            
            # 显示生成的水印
            display_image = self.original_watermark.copy()
            display_image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(display_image)
            self.watermark_label.configure(image=photo)
            self.watermark_label.image = photo
            
            # 生成带类型标识的文件名
            output_filename = f"generated_watermark_{type_str}.png"
            self.original_watermark.save(output_filename)
            self.watermark_filename_label.configure(text=f"水印图像: {output_filename}")
            messagebox.showinfo("成功", f"水印已生成并保存为{output_filename}")
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的水印尺寸")

def main():
    root = tk.Tk()
    app = WatermarkGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 