"""
Web应用模块

提供基于Streamlit的Web界面
"""

import os
import json
import time
import tempfile
import cv2
import numpy as np
from PIL import Image
import torch
import io
import streamlit as st
from typing import Optional, Dict, List, Any

from ..core.detector import DetectionProcessor
from ..models import get_default_model_path, is_cuda_available


def run_webapp(
    model_path: Optional[str] = None,
    output_dir: str = "results",
    port: int = 8501,
    address: str = "127.0.0.1"
):
    """
    启动Web应用
    
    参数:
        model_path: 模型路径，如果为None则使用默认模型
        output_dir: 结果输出目录
        port: 服务端口
        address: 服务地址
    """
    # 确保输出目录存在
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 设置环境变量
    os.environ["STREAMLIT_SERVER_PORT"] = str(port)
    os.environ["STREAMLIT_SERVER_ADDRESS"] = address
    
    # 启动应用
    import sys
    sys.argv = ["streamlit", "run", __file__]
    import streamlit.web.cli as stcli
    stcli.main()


# 页面配置
st.set_page_config(
    page_title="CCTV 智能检测系统",
    page_icon="🔍",
    layout="wide"
)

# 获取应用程序文件所在的目录
app_dir = os.path.dirname(os.path.abspath(__file__))

# 标题和说明
st.title("CCTV 智能检测系统")
st.subheader("上传图像进行智能检测与警报分析")

# 侧边栏配置区域
with st.sidebar:
    st.header("配置参数")
    
    # 模型路径 - 使用基于应用目录的路径
    default_model_path = get_default_model_path()
    model_path = st.text_input("模型路径", default_model_path)
    
    # 显示当前工作目录信息，帮助用户理解路径问题
    with st.expander("路径信息", expanded=False):
        st.write(f"当前工作目录: {os.getcwd()}")
        st.write("注意: 相对路径以当前工作目录为基准，推荐使用绝对路径")
    
    # 检测阈值
    conf_threshold = st.slider("置信度阈值", 0.0, 1.0, 0.25, 0.01)
    iou_threshold = st.slider("IOU阈值", 0.0, 1.0, 0.45, 0.01)
    
    # 设备选择
    device_options = ["cpu", "cuda:0"] if is_cuda_available() else ["cpu"]
    device = st.selectbox("推理设备", device_options)
    
    # 添加一个分隔线
    st.markdown("---")
    
    # 显示项目信息
    st.markdown("### 关于")
    st.markdown("CCTV 智能检测系统是一个基于 YOLOv8 的对象检测与警报系统，专为货舱监控设计。")
    st.markdown("支持检测：人员、船只、机械、摄像头异常等情况，以及货舱覆盖状态。")

# 上传文件
uploaded_file = st.file_uploader("上传图像", type=['jpg', 'jpeg', 'png'])

# 处理上传的图像
if uploaded_file is not None:
    # 显示上传的图像
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("原始图像")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
    
    # 保存上传的文件到临时目录
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_path = tmp_file.name
    
    # 显示处理中提示
    with st.spinner('处理图像中...'):
        try:
            # 初始化处理器
            processor = DetectionProcessor(
                model_path=model_path,
                conf=conf_threshold,
                iou=iou_threshold,
                device=device,
                output_dir="results"
            )
            
            # 处理图像
            start_time = time.time()
            result = processor.process_image(temp_path)
            process_time = time.time() - start_time
            
            # 移除临时文件路径信息
            if "data" in result and "image_path" in result["data"]:
                result["data"]["image_path"] = os.path.basename(result["data"]["image_path"])
            
            if "data" in result and "visualization_path" in result["data"]:
                # 读取可视化结果
                vis_image = cv2.imread(result["data"]["visualization_path"])
                vis_image = cv2.cvtColor(vis_image, cv2.COLOR_BGR2RGB)
                
                # 记录可视化图像路径用于后续下载
                vis_path = result["data"]["visualization_path"]
                
                # 更新可视化路径为文件名
                result["data"]["visualization_path"] = os.path.basename(result["data"]["visualization_path"])
                
                # 在右侧显示可视化结果
                with col2:
                    st.subheader("检测结果可视化")
                    st.image(vis_image, use_container_width=True)
            
            # 显示处理时间
            st.success(f"图像处理完成！耗时: {process_time:.2f} 秒")
            
            # 检查是否有警报
            if "data" in result and "alarms" in result["data"] and result["data"]["alarms"]:
                st.warning("⚠️ 检测到告警情况！")
                
                # 美化警报类型名称显示
                alarm_display_names = {
                    "person_intrusion": "人员入侵",
                    "vessel_approach": "船只接近",
                    "machinery_intrusion": "机械入侵",
                    "camera_alarm": "摄像头异常"
                }
                
                # 创建告警展示区
                with st.container():
                    st.subheader("🚨 告警信息")
                    
                    # 计算总告警数量
                    total_alarms = sum(len(alarms) for alarms in result["data"]["alarms"].values())
                    st.markdown(f"**共检测到 {total_alarms} 个告警**")
                    
                    # 展示所有告警
                    for alarm_type, alarms in result["data"]["alarms"].items():
                        alarm_name = alarm_display_names.get(alarm_type, alarm_type)
                        st.markdown(f"#### {alarm_name} ({len(alarms)})")
                        
                        # 创建告警列表
                        for alarm in alarms:
                            confidence = alarm["confidence"]
                            object_class = alarm["object_class"]
                            location = alarm["location"]
                            
                            # 使用更紧凑的格式显示告警
                            st.markdown(f"""
                            <div style="border-left: 3px solid #FF4B4B; padding-left: 10px; margin-bottom: 10px;">
                                <strong>{object_class}</strong> (置信度: {confidence:.2f})<br>
                                位置: [{location['x1']}, {location['y1']}, {location['x2']}, {location['y2']}]
                            </div>
                            """, unsafe_allow_html=True)
            
            # 显示检测结果
            with st.container():
                st.subheader("🔍 检测对象")
                if "data" in result and "detections" in result["data"] and result["data"]["detections"]:
                    # 显示检测对象数量
                    st.markdown(f"**共检测到 {len(result['data']['detections'])} 个目标**")
                    
                    # 创建一个表格显示主要信息
                    detection_data = []
                    for det in result["data"]["detections"]:
                        detection_data.append({
                            "ID": det.get("id", ""),
                            "类别": det.get("class_name", ""),
                            "置信度": f"{det.get('confidence', 0):.2f}",
                            "位置": f"[{det['bbox']['x1']}, {det['bbox']['y1']}, {det['bbox']['x2']}, {det['bbox']['y2']}]"
                        })
                    
                    if detection_data:
                        st.dataframe(detection_data, use_container_width=True)
                else:
                    st.info("未检测到任何对象")
            
            # 显示完整的JSON结果和下载按钮
            col1, col2 = st.columns([3, 1])
            with col1:
                with st.expander("查看完整JSON结果", expanded=False):
                    st.json(result)
            
            with col2:
                # 提供下载结果的功能
                json_str = json.dumps(result, indent=2, ensure_ascii=False)
                st.download_button(
                    label="下载JSON结果",
                    data=json_str,
                    file_name=f"detection_result_{int(time.time())}.json",
                    mime="application/json"
                )
                
                # 如果有可视化结果，提供下载
                if "data" in result and "visualization_path" in result["data"] and locals().get("vis_path") and os.path.exists(vis_path):
                    with open(vis_path, "rb") as f:
                        vis_bytes = f.read()
                    
                    st.download_button(
                        label="下载可视化图像",
                        data=vis_bytes,
                        file_name=f"visualization_{int(time.time())}.jpg",
                        mime="image/jpeg"
                    )
            
        except Exception as e:
            st.error(f"处理过程中出错: {str(e)}")
        
        # 清理临时文件
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except:
            pass

# 如果没有上传文件，显示说明信息
if 'uploaded_file' not in locals() or uploaded_file is None:
    st.info("请上传图像以开始检测")
    st.markdown("""
    ### 功能介绍：
    1. 上传图像进行对象检测
    2. 自动检测货舱覆盖状态（已覆盖/部分覆盖/未覆盖）
    3. 监测人员、船只、机械等进入货舱区域的情况并发出警报
    4. 摄像头异常监测
    5. 检测结果可视化，并提供JSON格式的详细信息
    6. 支持下载检测结果和可视化内容
    
    ### 使用方法：
    1. 在左侧边栏调整检测参数
    2. 上传图像文件并等待系统处理
    3. 查看检测结果和警报信息
    """)

# 页脚
st.markdown("---")
st.markdown("CCTV 智能检测系统 | 基于YOLOv8与Streamlit开发")


# 直接运行此文件时启动应用
if __name__ == "__main__":
    run_webapp() 