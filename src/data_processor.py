import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import config

class DataProcessor:
    def __init__(self):
        self.data = None
        self.x = None
        self.y = None
        self.dx = None
        self.dy = None
        self.dz = None
        
    def load_data(self, file_path=None):
        """加载FLAC3D位移数据"""
        if file_path is None:
            file_path = config.INPUT_PATH
            
        try:
            # 使用pandas读取数据，更灵活地处理格式问题
            df = pd.read_csv(file_path, sep=None, engine='python', skiprows=1)
            
            # 检查列数
            if len(df.columns) < 7:
                print(f"警告：数据只有 {len(df.columns)} 列，期望7列")
                print("列名：", df.columns.tolist())
                return False
            
            # 转换为numpy数组
            self.data = df.values
            
            print(f"成功加载数据，共 {len(self.data)} 个节点")
            
            # 提取坐标和位移数据
            self.x = self.data[:, 1]  # X坐标（单位m）
            self.y = self.data[:, 2]  # Y坐标（单位m）
            self.dx = self.data[:, 4] * config.DISPLACEMENT_TO_MM  # X方向位移（mm）
            self.dy = self.data[:, 5] * config.DISPLACEMENT_TO_MM  # Y方向位移（mm）
            self.dz = self.data[:, 6] * config.DISPLACEMENT_TO_MM  # Z方向位移（mm）
            
            print(f"数据范围：X[{self.x.min():.2f}, {self.x.max():.2f}], "
                  f"Y[{self.y.min():.2f}, {self.y.max():.2f}]")
            
        except Exception as e:
            print(f"加载数据失败：{e}")
            print("尝试使用备用方法...")
            
            try:
                # 备用方法：手动读取和清理数据
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 跳过表头
                lines = lines[1:]
                
                # 清理数据
                cleaned_data = []
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line and len(line.split()) >= 7:  # 确保有足够的列
                        try:
                            row = [float(x) for x in line.split()]
                            if len(row) >= 7:
                                cleaned_data.append(row[:7])  # 只取前7列
                        except ValueError:
                            print(f"跳过第 {i+2} 行（无法转换为数字）")
                            continue
                
                if not cleaned_data:
                    print("没有找到有效数据")
                    return False
                
                self.data = np.array(cleaned_data)
                print(f"成功加载数据，共 {len(self.data)} 个节点（清理后）")
                
                # 提取坐标和位移数据
                self.x = self.data[:, 1]  # X坐标
                self.y = self.data[:, 2]  # Y坐标
                self.dx = self.data[:, 4] * config.DISPLACEMENT_TO_MM  # X方向位移（mm）
                self.dy = self.data[:, 5] * config.DISPLACEMENT_TO_MM  # Y方向位移（mm）
                self.dz = self.data[:, 6] * config.DISPLACEMENT_TO_MM  # Z方向位移（mm）
                
                print(f"数据范围：X[{self.x.min():.2f}, {self.x.max():.2f}], "
                      f"Y[{self.y.min():.2f}, {self.y.max():.2f}]")
                
            except Exception as e2:
                print(f"备用方法也失败：{e2}")
                return False
            
        return True
    
    def create_interpolation_grid(self):
        """创建插值网格，保持XY比例一致"""
        x_range = self.x.max() - self.x.min()
        y_range = self.y.max() - self.y.min()
        if x_range > y_range:
            nx = config.GRID_RESOLUTION
            ny = int(config.GRID_RESOLUTION * y_range / x_range)
        else:
            ny = config.GRID_RESOLUTION
            nx = int(config.GRID_RESOLUTION * x_range / y_range)
        xi = np.linspace(self.x.min(), self.x.max(), nx)
        yi = np.linspace(self.y.min(), self.y.max(), ny)
        xi_grid, yi_grid = np.meshgrid(xi, yi)
        return xi_grid, yi_grid, nx, ny
    
    def interpolate_displacement(self, xi_grid, yi_grid, displacement_data):
        zi = griddata((self.x, self.y), displacement_data, (xi_grid, yi_grid), method=config.INTERPOLATION_METHOD)
        return zi
    
    def calculate_tilt(self, zi, xi_grid, yi_grid):
        # 计算梯度，第二个参数为物理坐标
        dz_dy, dz_dx = np.gradient(zi, yi_grid[:,0], xi_grid[0,:])
        tilt_x = dz_dx  # 单位：mm/m
        tilt_y = dz_dy  # 单位：mm/m
        return tilt_x, tilt_y
    
    def calculate_curvature(self, zi, xi_grid, yi_grid):
        # 计算二阶导数，第二个参数为物理坐标
        d2z_dx2 = np.gradient(np.gradient(zi, xi_grid[0,:], axis=1), xi_grid[0,:], axis=1)
        d2z_dy2 = np.gradient(np.gradient(zi, yi_grid[:,0], axis=0), yi_grid[:,0], axis=0)
        curvature_x = d2z_dx2  # 单位：1/m，等价于10^-3/m
        curvature_y = d2z_dy2  # 单位：1/m，等价于10^-3/m
        return curvature_x, curvature_y
    
    def calculate_horizontal_strain(self, dx_grid, dy_grid, xi_grid, yi_grid):
        d_dx_dx = np.gradient(dx_grid, xi_grid[0,:], axis=1)
        d_dy_dy = np.gradient(dy_grid, yi_grid[:,0], axis=0)
        d_dx_dy = np.gradient(dx_grid, yi_grid[:,0], axis=0)
        d_dy_dx = np.gradient(dy_grid, xi_grid[0,:], axis=1)
        strain_x = d_dx_dx  # 单位：mm/m
        strain_y = d_dy_dy  # 单位：mm/m
        shear_strain = (d_dx_dy + d_dy_dx) / 2  # 单位：mm/m
        return strain_x, strain_y, shear_strain
    
    def get_statistics(self):
        stats = {
            '节点数量': len(self.data),
            'X坐标范围': [self.x.min(), self.x.max()],
            'Y坐标范围': [self.y.min(), self.y.max()],
            'DX范围(mm)': [self.dx.min(), self.dx.max()],
            'DY范围(mm)': [self.dy.min(), self.dy.max()],
            'DZ范围(mm)': [self.dz.min(), self.dz.max()]
        }
        return stats
