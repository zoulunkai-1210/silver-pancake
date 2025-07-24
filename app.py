import streamlit as st
import os
import tempfile
import numpy as np
from src.data_processor import DataProcessor
from src.visualization import Visualizer
import config

st.set_page_config(page_title="FLAC3D后处理可视化工具", layout="wide")
st.title("FLAC3D后处理交互式可视化工具")
st.markdown("""
本工具支持上传FLAC3D位移数据(txt)，一键生成多种可视化结果。\
上传数据后可自定义插值分辨率，点击各自“生成”按钮即可在下方查看和下载图片。
""")

# 1. 文件上传和基础参数
uploaded_file = st.file_uploader("请上传FLAC3D位移数据(txt)", type=["txt"])
col1, col2 = st.columns(2)
with col1:
    grid_res = st.slider("插值网格分辨率", 50, 500, config.GRID_RESOLUTION)
with col2:
    interp_method = st.selectbox("插值方法", ["linear", "cubic", "nearest"], index=["linear", "cubic", "nearest"].index(config.INTERPOLATION_METHOD))

# 2. 数据处理与插值（只做一次，缓存到session_state）
if 'data_ready' not in st.session_state:
    st.session_state['data_ready'] = False

if uploaded_file and st.button("数据预处理/刷新"):
    with st.spinner("正在处理数据..."):
        results_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(results_dir, exist_ok=True)
        data_path = os.path.join(results_dir, "input.txt")
        with open(data_path, "wb") as f:
            f.write(uploaded_file.read())
        config.INPUT_PATH = data_path
        config.GRID_RESOLUTION = grid_res
        config.INTERPOLATION_METHOD = interp_method
        config.RESULTS_DIR = results_dir
        processor = DataProcessor()
        if not processor.load_data():
            st.error("数据加载失败，请检查数据格式！")
            st.session_state['data_ready'] = False
        else:
            xi_grid, yi_grid, nx, ny = processor.create_interpolation_grid()
            dx_grid = processor.interpolate_displacement(xi_grid, yi_grid, processor.dx)
            dy_grid = processor.interpolate_displacement(xi_grid, yi_grid, processor.dy)
            dz_grid = processor.interpolate_displacement(xi_grid, yi_grid, processor.dz)
            tilt_x, tilt_y = processor.calculate_tilt(dz_grid, xi_grid, yi_grid)
            curvature_x, curvature_y = processor.calculate_curvature(dz_grid, xi_grid, yi_grid)
            strain_x, strain_y, shear_strain = processor.calculate_horizontal_strain(dx_grid, dy_grid, xi_grid, yi_grid)
            # 缓存所有数据
            st.session_state['data_ready'] = True
            st.session_state['xi_grid'] = xi_grid
            st.session_state['yi_grid'] = yi_grid
            st.session_state['dx_grid'] = dx_grid
            st.session_state['dy_grid'] = dy_grid
            st.session_state['dz_grid'] = dz_grid
            st.session_state['tilt_x'] = tilt_x
            st.session_state['tilt_y'] = tilt_y
            st.session_state['curvature_x'] = curvature_x
            st.session_state['curvature_y'] = curvature_y
            st.session_state['strain_x'] = strain_x
            st.session_state['strain_y'] = strain_y
            st.session_state['shear_strain'] = shear_strain
            st.session_state['results_dir'] = results_dir
            st.success("数据处理完成！可生成各类云图。")

# 3. 各云图独立分区和按钮
if st.session_state.get('data_ready', False):
    visualizer = Visualizer()
    xi_grid = st.session_state['xi_grid']
    yi_grid = st.session_state['yi_grid']
    dx_grid = st.session_state['dx_grid']
    dy_grid = st.session_state['dy_grid']
    dz_grid = st.session_state['dz_grid']
    tilt_x = st.session_state['tilt_x']
    tilt_y = st.session_state['tilt_y']
    curvature_x = st.session_state['curvature_x']
    curvature_y = st.session_state['curvature_y']
    strain_x = st.session_state['strain_x']
    strain_y = st.session_state['strain_y']
    shear_strain = st.session_state['shear_strain']
    results_dir = st.session_state['results_dir']
    img_dir = results_dir

    # X方向位移
    with st.expander("X方向位移云图", expanded=True):
        x_auto_saturate = st.checkbox("自动色阶饱和（1%~99%分位数）", value=True, key="x_auto_saturate")
        if x_auto_saturate:
            x_vmin_auto = float(np.nanpercentile(dx_grid, 1))
            x_vmax_auto = float(np.nanpercentile(dx_grid, 99))
        else:
            x_vmin_auto = float(np.nanmin(dx_grid))
            x_vmax_auto = float(np.nanmax(dx_grid))
        x_vmin = st.number_input("色阶最小值", value=x_vmin_auto, key="x_vmin")
        x_vmax = st.number_input("色阶最大值", value=x_vmax_auto, key="x_vmax")
        x_contour_lines = st.slider("线型等高线数量", 2, 30, 10, key="x_contour_lines")
        if st.button("生成X方向位移云图"):
            visualizer.plot_displacement_contour(
                xi_grid, yi_grid, dx_grid, "X方向位移", "displacement_x", "X方向位移", "mm",
                vmin=x_vmin, vmax=x_vmax, contour_lines=x_contour_lines
            )
            img_path = os.path.join(img_dir, "displacement_x.png")
            if os.path.exists(img_path):
                st.image(img_path)
                with open(img_path, "rb") as f:
                    st.download_button("下载X方向位移图片", f.read(), file_name="displacement_x.png")

    # Y方向位移
    with st.expander("Y方向位移云图", expanded=False):
        y_auto_saturate = st.checkbox("自动色阶饱和（1%~99%分位数）", value=True, key="y_auto_saturate")
        if y_auto_saturate:
            y_vmin_auto = float(np.nanpercentile(dy_grid, 1))
            y_vmax_auto = float(np.nanpercentile(dy_grid, 99))
        else:
            y_vmin_auto = float(np.nanmin(dy_grid))
            y_vmax_auto = float(np.nanmax(dy_grid))
        y_vmin = st.number_input("色阶最小值", value=y_vmin_auto, key="y_vmin")
        y_vmax = st.number_input("色阶最大值", value=y_vmax_auto, key="y_vmax")
        y_contour_lines = st.slider("线型等高线数量", 2, 30, 10, key="y_contour_lines")
        if st.button("生成Y方向位移云图"):
            visualizer.plot_displacement_contour(
                xi_grid, yi_grid, dy_grid, "Y方向位移", "displacement_y", "Y方向位移", "mm",
                vmin=y_vmin, vmax=y_vmax, contour_lines=y_contour_lines
            )
            img_path = os.path.join(img_dir, "displacement_y.png")
            if os.path.exists(img_path):
                st.image(img_path)
                with open(img_path, "rb") as f:
                    st.download_button("下载Y方向位移图片", f.read(), file_name="displacement_y.png")

    # Z方向位移
    with st.expander("Z方向位移云图", expanded=False):
        z_auto_saturate = st.checkbox("自动色阶饱和（1%~99%分位数）", value=True, key="z_auto_saturate")
        if z_auto_saturate:
            z_vmin_auto = float(np.nanpercentile(dz_grid, 1))
            z_vmax_auto = float(np.nanpercentile(dz_grid, 99))
        else:
            z_vmin_auto = float(np.nanmin(dz_grid))
            z_vmax_auto = float(np.nanmax(dz_grid))
        z_vmin = st.number_input("色阶最小值", value=z_vmin_auto, key="z_vmin")
        z_vmax = st.number_input("色阶最大值", value=z_vmax_auto, key="z_vmax")
        z_contour_lines = st.slider("线型等高线数量", 2, 30, 10, key="z_contour_lines")
        if st.button("生成Z方向位移云图"):
            visualizer.plot_displacement_contour(
                xi_grid, yi_grid, dz_grid, "Z方向位移", "displacement_z", "Z方向位移", "mm",
                vmin=z_vmin, vmax=z_vmax, contour_lines=z_contour_lines
            )
            img_path = os.path.join(img_dir, "displacement_z.png")
            if os.path.exists(img_path):
                st.image(img_path)
                with open(img_path, "rb") as f:
                    st.download_button("下载Z方向位移图片", f.read(), file_name="displacement_z.png")

    # 倾斜变形
    with st.expander("倾斜变形云图", expanded=False):
        tilt_auto_saturate = st.checkbox("自动色阶饱和（1%~99%分位数）", value=True, key="tilt_auto_saturate")
        if tilt_auto_saturate:
            tilt_vmin_auto = float(np.nanpercentile(np.concatenate([tilt_x.flatten(), tilt_y.flatten()]), 1))
            tilt_vmax_auto = float(np.nanpercentile(np.concatenate([tilt_x.flatten(), tilt_y.flatten()]), 99))
        else:
            tilt_vmin_auto = float(np.nanmin([np.nanmin(tilt_x), np.nanmin(tilt_y)]))
            tilt_vmax_auto = float(np.nanmax([np.nanmax(tilt_x), np.nanmax(tilt_y)]))
        tilt_vmin = st.number_input("色阶最小值", value=tilt_vmin_auto, key="tilt_vmin")
        tilt_vmax = st.number_input("色阶最大值", value=tilt_vmax_auto, key="tilt_vmax")
        tilt_contour_lines = st.slider("线型等高线数量", 2, 30, 10, key="tilt_contour_lines")
        if st.button("生成倾斜变形云图"):
            visualizer.plot_tilt_contour(
                xi_grid, yi_grid, tilt_x, tilt_y, "surface_tilt",
                vmin=tilt_vmin, vmax=tilt_vmax, contour_lines=tilt_contour_lines
            )
            img_path = os.path.join(img_dir, "surface_tilt.png")
            if os.path.exists(img_path):
                st.image(img_path)
                with open(img_path, "rb") as f:
                    st.download_button("下载倾斜变形图片", f.read(), file_name="surface_tilt.png")

    # 曲率
    with st.expander("曲率云图", expanded=False):
        curv_auto_saturate = st.checkbox("自动色阶饱和（1%~99%分位数）", value=True, key="curv_auto_saturate")
        if curv_auto_saturate:
            curv_vmin_auto = float(np.nanpercentile(np.concatenate([curvature_x.flatten(), curvature_y.flatten()]), 1))
            curv_vmax_auto = float(np.nanpercentile(np.concatenate([curvature_x.flatten(), curvature_y.flatten()]), 99))
        else:
            curv_vmin_auto = float(np.nanmin([np.nanmin(curvature_x), np.nanmin(curvature_y)]))
            curv_vmax_auto = float(np.nanmax([np.nanmax(curvature_x), np.nanmax(curvature_y)]))
        curv_vmin = st.number_input("色阶最小值", value=curv_vmin_auto, key="curv_vmin")
        curv_vmax = st.number_input("色阶最大值", value=curv_vmax_auto, key="curv_vmax")
        curv_contour_lines = st.slider("线型等高线数量", 2, 30, 10, key="curv_contour_lines")
        if st.button("生成曲率云图"):
            visualizer.plot_curvature_contour(
                xi_grid, yi_grid, curvature_x, curvature_y, "surface_curvature",
                vmin=curv_vmin, vmax=curv_vmax, contour_lines=curv_contour_lines
            )
            img_path = os.path.join(img_dir, "surface_curvature.png")
            if os.path.exists(img_path):
                st.image(img_path)
                with open(img_path, "rb") as f:
                    st.download_button("下载曲率图片", f.read(), file_name="surface_curvature.png")

    # 水平变形
    with st.expander("水平变形云图", expanded=False):
        strain_auto_saturate = st.checkbox("自动色阶饱和（1%~99%分位数）", value=True, key="strain_auto_saturate")
        if strain_auto_saturate:
            strain_vmin_auto = float(np.nanpercentile(np.concatenate([strain_x.flatten(), strain_y.flatten(), shear_strain.flatten()]), 1))
            strain_vmax_auto = float(np.nanpercentile(np.concatenate([strain_x.flatten(), strain_y.flatten(), shear_strain.flatten()]), 99))
        else:
            strain_vmin_auto = float(np.nanmin([np.nanmin(strain_x), np.nanmin(strain_y), np.nanmin(shear_strain)]))
            strain_vmax_auto = float(np.nanmax([np.nanmax(strain_x), np.nanmax(strain_y), np.nanmax(shear_strain)]))
        strain_vmin = st.number_input("色阶最小值", value=strain_vmin_auto, key="strain_vmin")
        strain_vmax = st.number_input("色阶最大值", value=strain_vmax_auto, key="strain_vmax")
        strain_contour_lines = st.slider("线型等高线数量", 2, 30, 10, key="strain_contour_lines")
        if st.button("生成水平变形云图"):
            visualizer.plot_strain_contour(
                xi_grid, yi_grid, strain_x, strain_y, shear_strain, "horizontal_strain",
                vmin=strain_vmin, vmax=strain_vmax, contour_lines=strain_contour_lines
            )
            img_path = os.path.join(img_dir, "horizontal_strain.png")
            if os.path.exists(img_path):
                st.image(img_path)
                with open(img_path, "rb") as f:
                    st.download_button("下载水平变形图片", f.read(), file_name="horizontal_strain.png") 