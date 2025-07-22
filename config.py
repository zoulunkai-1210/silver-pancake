# 配置文件
import os
import sys

# 判断是否为PyInstaller打包后的环境
if getattr(sys, 'frozen', False):
    # 打包后，BASE_DIR为exe所在目录
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 源码运行，BASE_DIR为当前文件所在目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
SRC_DIR = os.path.join(BASE_DIR, 'src')

# 数据文件配置
INPUT_FILE = 'top_surface_disp.txt'
INPUT_PATH = os.path.join(DATA_DIR, INPUT_FILE)

# 插值配置
GRID_RESOLUTION = 200  # 网格分辨率
INTERPOLATION_METHOD = 'cubic'  # 插值方法：'linear', 'cubic', 'nearest'

# 绘图配置
FIGURE_SIZE = (12, 8)
DPI = 300
COLORMAP = 'jet'  # 颜色映射：'jet', 'viridis', 'plasma', 'coolwarm'
CONTOUR_LEVELS = 50

# 单位转换配置
DISPLACEMENT_TO_MM = 1000  # 位移单位转换为mm（假设原单位为m）
DISTANCE_TO_M = 1.0  # 距离单位（假设原单位为m）

# 输出配置
SAVE_FORMATS = ['png', 'pdf']  # 保存格式