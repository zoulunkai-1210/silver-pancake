import os
import sys
import glob
import config
from src.data_processor import DataProcessor
from src.visualization import Visualizer

def main():
    print("=== FLAC3D 数值模拟后处理工具 ===")

    # 检查data目录
    if not os.path.exists(config.DATA_DIR):
        print(f"错误：找不到数据文件夹 {config.DATA_DIR}")
        input("按回车键退出...")
        return

    # 自动查找data目录下的txt文件
    data_files = glob.glob(os.path.join(config.DATA_DIR, "*.txt"))
    if not data_files:
        print(f"错误：data文件夹下没有找到任何txt数据文件，请放入原始数据后重试。")
        input("按回车键退出...")
        return
    else:
        print(f"检测到数据文件：{data_files[0]}")
        config.INPUT_PATH = data_files[0]  # 动态指定数据文件

    # 创建结果文件夹
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    # 初始化处理器和可视化器
    processor = DataProcessor()
    visualizer = Visualizer()

    # 加载数据
    print("\n1. 加载数据...")
    if not processor.load_data():
        input("按回车键退出...")
        return

    # 显示数据统计信息
    stats = processor.get_statistics()
    print("\n数据统计信息：")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 创建插值网格
    print("\n2. 创建插值网格...")
    xi_grid, yi_grid, nx, ny = processor.create_interpolation_grid()
    print(f"网格分辨率: {nx} x {ny}")

    # 插值处理
    print("\n3. 进行数据插值...")
    dx_grid = processor.interpolate_displacement(xi_grid, yi_grid, processor.dx)
    dy_grid = processor.interpolate_displacement(xi_grid, yi_grid, processor.dy)
    dz_grid = processor.interpolate_displacement(xi_grid, yi_grid, processor.dz)

    # 计算倾斜变形
    print("\n4. 计算倾斜变形...")
    tilt_x, tilt_y = processor.calculate_tilt(dz_grid, xi_grid, yi_grid)

    # 计算曲率
    print("\n5. 计算曲率...")
    curvature_x, curvature_y = processor.calculate_curvature(dz_grid, xi_grid, yi_grid)

    # 计算水平变形
    print("\n6. 计算水平变形...")
    strain_x, strain_y, shear_strain = processor.calculate_horizontal_strain(
        dx_grid, dy_grid, xi_grid, yi_grid)

    # 绘制云图
    print("\n7. 生成可视化结果...")

    # 绘制位移云图
    visualizer.plot_displacement_contour(xi_grid, yi_grid, dx_grid,
                                       "X方向位移", "displacement_x", "X方向位移", "mm")
    visualizer.plot_displacement_contour(xi_grid, yi_grid, dy_grid,
                                       "Y方向位移", "displacement_y", "Y方向位移", "mm")
    visualizer.plot_displacement_contour(xi_grid, yi_grid, dz_grid,
                                       "Z方向位移", "displacement_z", "Z方向位移", "mm")

    # 绘制倾斜变形云图
    visualizer.plot_tilt_contour(xi_grid, yi_grid, tilt_x, tilt_y, "surface_tilt")

    # 绘制曲率云图
    visualizer.plot_curvature_contour(xi_grid, yi_grid, curvature_x, curvature_y, "surface_curvature")

    # 绘制水平变形云图
    visualizer.plot_strain_contour(xi_grid, yi_grid, strain_x, strain_y, shear_strain, "horizontal_strain")

    print("\n=== 处理完成！ ===")
    print(f"结果文件保存在：{config.RESULTS_DIR}")

    # 自动打开结果文件夹（仅Windows）
    try:
        if sys.platform.startswith('win'):
            os.startfile(config.RESULTS_DIR)
    except Exception:
        pass

    input("按回车键退出...")

if __name__ == "__main__":
    main()
