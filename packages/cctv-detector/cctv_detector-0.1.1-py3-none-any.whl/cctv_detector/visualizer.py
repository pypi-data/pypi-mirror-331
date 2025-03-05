"""
可视化模块
提供检测结果的可视化功能
"""

import os
import cv2
import numpy as np
import uuid

def visualize_detections(image, result, image_path, alarms, colors, output_dir=None):
    """
    可视化检测结果
    
    Args:
        image: 原始图像
        result: YOLO检测结果
        image_path: 图像路径
        alarms: 告警信息
        colors: 颜色配置
        output_dir: 输出目录
    
    Returns:
        str: 可视化结果保存路径，如果不保存则返回None
    """
    try:
        vis_image = image.copy()
        h, w = image.shape[:2]
        
        # 处理掩码和检测框
        if result.masks is not None and result.boxes is not None:
            masks = result.masks.data.cpu().numpy()
            for i, (mask, box) in enumerate(zip(masks, result.boxes)):
                # 获取基本信息
                cls_id = int(box.cls.item())
                cls_name = result.names[cls_id].lower()
                confidence = float(box.conf.item())
                xyxy = box.xyxy.cpu().numpy()[0].astype(int)
                x1, y1, x2, y2 = xyxy
                
                # 根据覆盖状态确定颜色
                if cls_name == "covered":
                    color = colors["covered"]
                elif cls_name == "partially_covered" or cls_name == "partially":
                    color = colors["partially"]
                elif cls_name == "uncovered":
                    color = colors["uncovered"]
                else:
                    color = colors["default"]
                
                # 处理掩码
                if mask.shape[:2] != (h, w):
                    mask = cv2.resize(mask, (w, h))
                
                # 创建彩色掩码
                colored_mask = np.zeros((h, w, 3), dtype=np.uint8)
                colored_mask[mask > 0.5] = color
                
                # 将掩码叠加到图像上（半透明效果）
                alpha = 0.15
                vis_image = cv2.addWeighted(vis_image, 1, colored_mask, alpha, 0)
                
                # 确定是否是告警对象
                is_alarm = False
                if alarms:
                    for alerts in alarms.values():
                        for alert in alerts:
                            if (cls_name == alert["object_class"].lower() and
                                x1 == alert["location"]["x1"] and
                                y1 == alert["location"]["y1"]):
                                is_alarm = True
                                break
                
                # 绘制检测框
                thickness = 3 if is_alarm else 2
                cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, thickness)
                
                # 绘制标签
                label = f"{cls_name} {confidence:.2f}"
                text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                
                # 确定标签位置（优先上方，如果上方放不下就放在下方）
                if y1 - text_size[1] - 5 < 0:  # 上方放不下
                    label_y = min(y2 + text_size[1] + 5, h - 5)  # 放在下方，但不超出图像
                else:  # 放在上方
                    label_y = y1 - 5
                
                # 绘制标签背景和文本
                cv2.rectangle(vis_image,
                            (x1, label_y - text_size[1] - 5),
                            (x1 + text_size[0], label_y),
                            (0, 0, 0), -1)
                cv2.putText(vis_image, label, (x1, label_y - 5),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # 保存结果
        if output_dir:
            base_name = os.path.basename(image_path)
            name, ext = os.path.splitext(base_name)
            unique_id = uuid.uuid4().hex[:8]
            output_path = os.path.join(output_dir, f"{name}_result_{unique_id}{ext}")
            cv2.imwrite(output_path, vis_image)
            return output_path
        
        return None
        
    except Exception as e:
        print(f"可视化过程出错: {str(e)}")
        return None 