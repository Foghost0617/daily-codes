import os
import numpy as np
import rasterio
from PIL import Image

# 输入输出路径
folder_path = 'maridaTif'        # 原始 Sentinel-2 tif 文件夹路径
output_folder = 'maridaRGB256'      # 输出 RGB 图像的路径

# 创建输出文件夹（如果不存在）
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 分位数归一化函数
def normalize_percentile(band, lower_percentile=2, upper_percentile=98):
    low = np.percentile(band, lower_percentile)
    high = np.percentile(band, upper_percentile)
    band = np.clip(band, low, high)
    return ((band - low) / (high - low) * 255).astype(np.uint8)

# 遍历 tif 文件
for file_name in os.listdir(folder_path):
    if file_name.lower().endswith(".tif"):
        file_path = os.path.join(folder_path, file_name)

        try:
            with rasterio.open(file_path) as src:
                # Sentinel-2: Band 4 = Red, Band 3 = Green, Band 2 = Blue
                red_band   = src.read(4)
                green_band = src.read(3)
                blue_band  = src.read(2)

                print(f"{file_name} | R[{red_band.min()}, {red_band.max()}] "
                      f"G[{green_band.min()}, {green_band.max()}] "
                      f"B[{blue_band.min()}, {blue_band.max()}]")

                # 使用分位数归一化
                red   = normalize_percentile(red_band)
                green = normalize_percentile(green_band)
                blue  = normalize_percentile(blue_band)

                # 合并为 RGB 图像
                rgb_image = np.stack((red, green, blue), axis=-1)

                # 转换为 PIL 图像并缩放
                pil_image = Image.fromarray(rgb_image)
                pil_image = pil_image.resize((256, 256), Image.Resampling.LANCZOS)

                # 构造输出路径
                output_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}_RGB.jpg")
                pil_image.save(output_path)

                print(f" Saved to {output_path}\n")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")