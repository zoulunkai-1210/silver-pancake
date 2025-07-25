import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import config
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.font_manager as fm

# 明确指定项目内字体文件
font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'msyh.ttc')
my_font = fm.FontProperties(fname=font_path)

class Visualizer:
    def __init__(self):
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['mathtext.fontset'] = 'stix'

    def plot_displacement_contour(self, xi, yi, zi, title, filename, displacement_type='位移', unit='mm',
                                 levels=None, vmin=None, vmax=None, contour_lines=10):
        print("config.CONTOUR_LEVELS =", config.CONTOUR_LEVELS, type(config.CONTOUR_LEVELS))
        print("contour_lines =", contour_lines, type(contour_lines))
        if not (isinstance(config.CONTOUR_LEVELS, int) or isinstance(config.CONTOUR_LEVELS, (list, np.ndarray))):
            raise TypeError(f"config.CONTOUR_LEVELS 类型错误: {type(config.CONTOUR_LEVELS)}")
        if not (isinstance(contour_lines, int) or isinstance(contour_lines, (list, np.ndarray))):
            raise TypeError(f"contour_lines 类型错误: {type(contour_lines)}")
        if vmin is not None and vmax is not None:
            N = config.CONTOUR_LEVELS if isinstance(config.CONTOUR_LEVELS, int) else len(config.CONTOUR_LEVELS)
            levels = np.linspace(vmin, vmax, N)
            ticks = list(np.linspace(vmin, vmax, min(N, 6)))
        else:
            if levels is None:
                if isinstance(config.CONTOUR_LEVELS, int):
                    N = config.CONTOUR_LEVELS
                    # 自动取数据范围
                    zmin, zmax = np.nanmin(zi), np.nanmax(zi)
                    levels = np.linspace(zmin, zmax, N)
                    ticks = list(np.linspace(zmin, zmax, min(N, 6)))
                else:
                    levels = np.array(config.CONTOUR_LEVELS)
                    N = len(levels)
                    ticks = list(np.linspace(np.min(levels), np.max(levels), min(N, 6)))
            else:
                if isinstance(levels, int):
                    N = levels
                    zmin, zmax = np.nanmin(zi), np.nanmax(zi)
                    levels = np.linspace(zmin, zmax, N)
                    ticks = list(np.linspace(zmin, zmax, min(N, 6)))
                else:
                    levels = np.array(levels)
                    N = len(levels)
                    ticks = list(np.linspace(np.min(levels), np.max(levels), min(N, 6)))
        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE, dpi=config.DPI)
        contour = ax.contourf(xi, yi, zi, levels=levels, cmap=config.COLORMAP, vmin=vmin, vmax=vmax, extend='both')
        contour_lines_obj = ax.contour(xi, yi, zi, levels=contour_lines, colors='black', linewidths=0.5, alpha=0.7)
        ax.clabel(contour_lines_obj, inline=True, fontsize=8)
        ax.set_xlabel('X 坐标 (m)', fontproperties=my_font)
        ax.set_ylabel('Y 坐标 (m)', fontproperties=my_font)
        ax.set_title(f'地表{displacement_type}云图 - {title}', fontproperties=my_font)
        ax.set_aspect('equal')
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        cbar = plt.colorbar(contour, cax=cax, ticks=ticks, extendfrac=0)
        cbar.set_label(f'{displacement_type} ({unit})', fontproperties=my_font)
        for fmt in config.SAVE_FORMATS:
            save_path = os.path.join(config.RESULTS_DIR, f'{filename}.{fmt}')
            plt.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
            print(f"已保存：{save_path}")
        plt.close(fig)

    def plot_tilt_contour(self, xi, yi, tilt_x, tilt_y, filename,
                         levels=None, vmin=None, vmax=None, contour_lines=10):
        if vmin is not None and vmax is not None:
            N = config.CONTOUR_LEVELS if isinstance(config.CONTOUR_LEVELS, int) else len(config.CONTOUR_LEVELS)
            levels1 = np.linspace(vmin, vmax, N)
            levels2 = np.linspace(vmin, vmax, N)
            ticks1 = list(np.linspace(vmin, vmax, min(N, 6)))
            ticks2 = list(np.linspace(vmin, vmax, min(N, 6)))
        else:
            if levels is None:
                if isinstance(config.CONTOUR_LEVELS, int):
                    N = config.CONTOUR_LEVELS
                    # 自动取数据范围
                    tilt_x_min, tilt_x_max = np.nanmin(tilt_x), np.nanmax(tilt_x)
                    tilt_y_min, tilt_y_max = np.nanmin(tilt_y), np.nanmax(tilt_y)
                    levels1 = np.linspace(tilt_x_min, tilt_x_max, N)
                    levels2 = np.linspace(tilt_y_min, tilt_y_max, N)
                    ticks1 = list(np.linspace(tilt_x_min, tilt_x_max, min(N, 6)))
                    ticks2 = list(np.linspace(tilt_y_min, tilt_y_max, min(N, 6)))
                else:
                    levels1 = np.array(config.CONTOUR_LEVELS)
                    levels2 = np.array(config.CONTOUR_LEVELS)
                    ticks1 = list(np.linspace(np.min(levels1), np.max(levels1), min(len(levels1), 6)))
                    ticks2 = list(np.linspace(np.min(levels2), np.max(levels2), min(len(levels2), 6)))
            else:
                if isinstance(levels, int):
                    N = levels
                    # 自动取数据范围
                    tilt_x_min, tilt_x_max = np.nanmin(tilt_x), np.nanmax(tilt_x)
                    tilt_y_min, tilt_y_max = np.nanmin(tilt_y), np.nanmax(tilt_y)
                    levels1 = np.linspace(tilt_x_min, tilt_x_max, N)
                    levels2 = np.linspace(tilt_y_min, tilt_y_max, N)
                    ticks1 = list(np.linspace(tilt_x_min, tilt_x_max, min(N, 6)))
                    ticks2 = list(np.linspace(tilt_y_min, tilt_y_max, min(N, 6)))
                else:
                    levels1 = np.array(levels)
                    levels2 = np.array(levels)
                    ticks1 = list(np.linspace(np.min(levels1), np.max(levels1), min(len(levels1), 6)))
                    ticks2 = list(np.linspace(np.min(levels2), np.max(levels2), min(len(levels2), 6)))
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=config.DPI)
        contour1 = ax1.contourf(xi, yi, tilt_x, levels=levels1, cmap='RdBu_r', vmin=vmin, vmax=vmax, extend='both')
        contour_lines1 = ax1.contour(xi, yi, tilt_x, levels=contour_lines, colors='black', linewidths=0.5, alpha=0.7)
        ax1.clabel(contour_lines1, inline=True, fontsize=8)
        ax1.set_xlabel('X 坐标 (m)', fontproperties=my_font)
        ax1.set_ylabel('Y 坐标 (m)', fontproperties=my_font)
        ax1.set_title('X方向倾斜变形', fontproperties=my_font)
        ax1.set_aspect('equal')
        divider1 = make_axes_locatable(ax1)
        cax1 = divider1.append_axes("right", size="5%", pad=0.1)
        cbar1 = plt.colorbar(contour1, cax=cax1, ticks=ticks1, extendfrac=0)
        cbar1.set_label('X方向倾斜 (mm/m)', fontproperties=my_font)
        contour2 = ax2.contourf(xi, yi, tilt_y, levels=levels2, cmap='RdBu_r', vmin=vmin, vmax=vmax, extend='both')
        contour_lines2 = ax2.contour(xi, yi, tilt_y, levels=contour_lines, colors='black', linewidths=0.5, alpha=0.7)
        ax2.clabel(contour_lines2, inline=True, fontsize=8)
        ax2.set_xlabel('X 坐标 (m)', fontproperties=my_font)
        ax2.set_ylabel('Y 坐标 (m)', fontproperties=my_font)
        ax2.set_title('Y方向倾斜变形', fontproperties=my_font)
        ax2.set_aspect('equal')
        divider2 = make_axes_locatable(ax2)
        cax2 = divider2.append_axes("right", size="5%", pad=0.1)
        cbar2 = plt.colorbar(contour2, cax=cax2, ticks=ticks2, extendfrac=0)
        cbar2.set_label('Y方向倾斜 (mm/m)', fontproperties=my_font)
        plt.tight_layout()
        for fmt in config.SAVE_FORMATS:
            save_path = os.path.join(config.RESULTS_DIR, f'{filename}.{fmt}')
            plt.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
            print(f"已保存：{save_path}")
        plt.close(fig)

    def plot_curvature_contour(self, xi, yi, curvature_x, curvature_y, filename,
                              levels=None, vmin=None, vmax=None, contour_lines=10):
        if vmin is not None and vmax is not None:
            N = config.CONTOUR_LEVELS if isinstance(config.CONTOUR_LEVELS, int) else len(config.CONTOUR_LEVELS)
            levels1 = np.linspace(vmin, vmax, N)
            levels2 = np.linspace(vmin, vmax, N)
            ticks1 = list(np.linspace(vmin, vmax, min(N, 6)))
            ticks2 = list(np.linspace(vmin, vmax, min(N, 6)))
        else:
            if levels is None:
                if isinstance(config.CONTOUR_LEVELS, int):
                    N = config.CONTOUR_LEVELS
                    # 自动取数据范围
                    curvature_x_min, curvature_x_max = np.nanmin(curvature_x), np.nanmax(curvature_x)
                    curvature_y_min, curvature_y_max = np.nanmin(curvature_y), np.nanmax(curvature_y)
                    levels1 = np.linspace(curvature_x_min, curvature_x_max, N)
                    levels2 = np.linspace(curvature_y_min, curvature_y_max, N)
                    ticks1 = list(np.linspace(curvature_x_min, curvature_x_max, min(N, 6)))
                    ticks2 = list(np.linspace(curvature_y_min, curvature_y_max, min(N, 6)))
                else:
                    levels1 = np.array(config.CONTOUR_LEVELS)
                    levels2 = np.array(config.CONTOUR_LEVELS)
                    ticks1 = list(np.linspace(np.min(levels1), np.max(levels1), min(len(levels1), 6)))
                    ticks2 = list(np.linspace(np.min(levels2), np.max(levels2), min(len(levels2), 6)))
            else:
                if isinstance(levels, int):
                    N = levels
                    # 自动取数据范围
                    curvature_x_min, curvature_x_max = np.nanmin(curvature_x), np.nanmax(curvature_x)
                    curvature_y_min, curvature_y_max = np.nanmin(curvature_y), np.nanmax(curvature_y)
                    levels1 = np.linspace(curvature_x_min, curvature_x_max, N)
                    levels2 = np.linspace(curvature_y_min, curvature_y_max, N)
                    ticks1 = list(np.linspace(curvature_x_min, curvature_x_max, min(N, 6)))
                    ticks2 = list(np.linspace(curvature_y_min, curvature_y_max, min(N, 6)))
                else:
                    levels1 = np.array(levels)
                    levels2 = np.array(levels)
                    ticks1 = list(np.linspace(np.min(levels1), np.max(levels1), min(len(levels1), 6)))
                    ticks2 = list(np.linspace(np.min(levels2), np.max(levels2), min(len(levels2), 6)))
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=config.DPI)
        contour1 = ax1.contourf(xi, yi, curvature_x, levels=levels1, cmap='viridis', vmin=vmin, vmax=vmax, extend='both')
        contour_lines1 = ax1.contour(xi, yi, curvature_x, levels=contour_lines, colors='white', linewidths=0.5, alpha=0.7)
        ax1.clabel(contour_lines1, inline=True, fontsize=8, colors='white')
        ax1.set_xlabel('X 坐标 (m)', fontproperties=my_font)
        ax1.set_ylabel('Y 坐标 (m)', fontproperties=my_font)
        ax1.set_title('X方向曲率', fontproperties=my_font)
        ax1.set_aspect('equal')
        divider1 = make_axes_locatable(ax1)
        cax1 = divider1.append_axes("right", size="5%", pad=0.1)
        cbar1 = plt.colorbar(contour1, cax=cax1, ticks=ticks1, extendfrac=0)
        cbar1.set_label('X方向曲率 (10^-3/m)', fontproperties=my_font)
        contour2 = ax2.contourf(xi, yi, curvature_y, levels=levels2, cmap='viridis', vmin=vmin, vmax=vmax, extend='both')
        contour_lines2 = ax2.contour(xi, yi, curvature_y, levels=contour_lines, colors='white', linewidths=0.5, alpha=0.7)
        ax2.clabel(contour_lines2, inline=True, fontsize=8, colors='white')
        ax2.set_xlabel('X 坐标 (m)', fontproperties=my_font)
        ax2.set_ylabel('Y 坐标 (m)', fontproperties=my_font)
        ax2.set_title('Y方向曲率', fontproperties=my_font)
        ax2.set_aspect('equal')
        divider2 = make_axes_locatable(ax2)
        cax2 = divider2.append_axes("right", size="5%", pad=0.1)
        cbar2 = plt.colorbar(contour2, cax=cax2, ticks=ticks2, extendfrac=0)
        cbar2.set_label('Y方向曲率 (10^-3/m)', fontproperties=my_font)
        plt.tight_layout()
        for fmt in config.SAVE_FORMATS:
            save_path = os.path.join(config.RESULTS_DIR, f'{filename}.{fmt}')
            plt.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
            print(f"已保存：{save_path}")
        plt.close(fig)

    def plot_strain_contour(self, xi, yi, strain_x, strain_y, shear_strain, filename,
                            levels=None, vmin=None, vmax=None, contour_lines=10):
        if vmin is not None and vmax is not None:
            N = config.CONTOUR_LEVELS if isinstance(config.CONTOUR_LEVELS, int) else len(config.CONTOUR_LEVELS)
            levels1 = np.linspace(vmin, vmax, N)
            levels2 = np.linspace(vmin, vmax, N)
            levels3 = np.linspace(vmin, vmax, N)
            ticks1 = list(np.linspace(vmin, vmax, min(N, 6)))
            ticks2 = list(np.linspace(vmin, vmax, min(N, 6)))
            ticks3 = list(np.linspace(vmin, vmax, min(N, 6)))
        else:
            if levels is None:
                if isinstance(config.CONTOUR_LEVELS, int):
                    N = config.CONTOUR_LEVELS
                    # 自动取数据范围
                    strain_x_min, strain_x_max = np.nanmin(strain_x), np.nanmax(strain_x)
                    strain_y_min, strain_y_max = np.nanmin(strain_y), np.nanmax(strain_y)
                    shear_strain_min, shear_strain_max = np.nanmin(shear_strain), np.nanmax(shear_strain)
                    levels1 = np.linspace(strain_x_min, strain_x_max, N)
                    levels2 = np.linspace(strain_y_min, strain_y_max, N)
                    levels3 = np.linspace(shear_strain_min, shear_strain_max, N)
                    ticks1 = list(np.linspace(strain_x_min, strain_x_max, min(N, 6)))
                    ticks2 = list(np.linspace(strain_y_min, strain_y_max, min(N, 6)))
                    ticks3 = list(np.linspace(shear_strain_min, shear_strain_max, min(N, 6)))
                else:
                    levels1 = np.array(config.CONTOUR_LEVELS)
                    levels2 = np.array(config.CONTOUR_LEVELS)
                    levels3 = np.array(config.CONTOUR_LEVELS)
                    ticks1 = list(np.linspace(np.min(levels1), np.max(levels1), min(len(levels1), 6)))
                    ticks2 = list(np.linspace(np.min(levels2), np.max(levels2), min(len(levels2), 6)))
                    ticks3 = list(np.linspace(np.min(levels3), np.max(levels3), min(len(levels3), 6)))
            else:
                if isinstance(levels, int):
                    N = levels
                    # 自动取数据范围
                    strain_x_min, strain_x_max = np.nanmin(strain_x), np.nanmax(strain_x)
                    strain_y_min, strain_y_max = np.nanmin(strain_y), np.nanmax(strain_y)
                    shear_strain_min, shear_strain_max = np.nanmin(shear_strain), np.nanmax(shear_strain)
                    levels1 = np.linspace(strain_x_min, strain_x_max, N)
                    levels2 = np.linspace(strain_y_min, strain_y_max, N)
                    levels3 = np.linspace(shear_strain_min, shear_strain_max, N)
                    ticks1 = list(np.linspace(strain_x_min, strain_x_max, min(N, 6)))
                    ticks2 = list(np.linspace(strain_y_min, strain_y_max, min(N, 6)))
                    ticks3 = list(np.linspace(shear_strain_min, shear_strain_max, min(N, 6)))
                else:
                    levels1 = np.array(levels)
                    levels2 = np.array(levels)
                    levels3 = np.array(levels)
                    ticks1 = list(np.linspace(np.min(levels1), np.max(levels1), min(len(levels1), 6)))
                    ticks2 = list(np.linspace(np.min(levels2), np.max(levels2), min(len(levels2), 6)))
                    ticks3 = list(np.linspace(np.min(levels3), np.max(levels3), min(len(levels3), 6)))
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6), dpi=config.DPI)
        contour1 = ax1.contourf(xi, yi, strain_x, levels=levels1, cmap='RdBu_r', vmin=vmin, vmax=vmax, extend='both')
        contour_lines1 = ax1.contour(xi, yi, strain_x, levels=contour_lines, colors='black', linewidths=0.5, alpha=0.7)
        ax1.clabel(contour_lines1, inline=True, fontsize=8)
        ax1.set_xlabel('X 坐标 (m)', fontproperties=my_font)
        ax1.set_ylabel('Y 坐标 (m)', fontproperties=my_font)
        ax1.set_title('X方向水平变形', fontproperties=my_font)
        ax1.set_aspect('equal')
        divider1 = make_axes_locatable(ax1)
        cax1 = divider1.append_axes("right", size="5%", pad=0.1)
        cbar1 = plt.colorbar(contour1, cax=cax1, ticks=ticks1, extendfrac=0)
        cbar1.set_label('X方向水平变形 (mm/m)', fontproperties=my_font)
        contour2 = ax2.contourf(xi, yi, strain_y, levels=levels2, cmap='RdBu_r', vmin=vmin, vmax=vmax, extend='both')
        contour_lines2 = ax2.contour(xi, yi, strain_y, levels=contour_lines, colors='black', linewidths=0.5, alpha=0.7)
        ax2.clabel(contour_lines2, inline=True, fontsize=8)
        ax2.set_xlabel('X 坐标 (m)', fontproperties=my_font)
        ax2.set_ylabel('Y 坐标 (m)', fontproperties=my_font)
        ax2.set_title('Y方向水平变形', fontproperties=my_font)
        ax2.set_aspect('equal')
        divider2 = make_axes_locatable(ax2)
        cax2 = divider2.append_axes("right", size="5%", pad=0.1)
        cbar2 = plt.colorbar(contour2, cax=cax2, ticks=ticks2, extendfrac=0)
        cbar2.set_label('Y方向水平变形 (mm/m)', fontproperties=my_font)
        contour3 = ax3.contourf(xi, yi, shear_strain, levels=levels3, cmap='RdBu_r', vmin=vmin, vmax=vmax, extend='both')
        contour_lines3 = ax3.contour(xi, yi, shear_strain, levels=contour_lines, colors='black', linewidths=0.5, alpha=0.7)
        ax3.clabel(contour_lines3, inline=True, fontsize=8)
        ax3.set_xlabel('X 坐标 (m)', fontproperties=my_font)
        ax3.set_ylabel('Y 坐标 (m)', fontproperties=my_font)
        ax3.set_title('剪切变形', fontproperties=my_font)
        ax3.set_aspect('equal')
        divider3 = make_axes_locatable(ax3)
        cax3 = divider3.append_axes("right", size="5%", pad=0.1)
        cbar3 = plt.colorbar(contour3, cax=cax3, ticks=ticks3, extendfrac=0)
        cbar3.set_label('剪切变形 (mm/m)', fontproperties=my_font)
        plt.tight_layout()
        for fmt in config.SAVE_FORMATS:
            save_path = os.path.join(config.RESULTS_DIR, f'{filename}.{fmt}')
            plt.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
            print(f"已保存：{save_path}")
        plt.close(fig)