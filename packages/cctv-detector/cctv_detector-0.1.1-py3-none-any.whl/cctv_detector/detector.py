#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CCTV Intelligent Detection System Core Module
"""

import os
import json
import numpy as np
import torch
from ultralytics import YOLO
import cv2
import time
import uuid
from .visualizer import visualize_detections

class DetectionProcessor:
    def __init__(self, model_path, conf=0.25, iou=0.45, device=None, output_dir="results"):
        """Initialize the detection processor
        
        Args:
            model_path (str): Path to the YOLOv8 model file
            conf (float, optional): Confidence threshold. Defaults to 0.25
            iou (float, optional): IoU threshold. Defaults to 0.45
            device (str, optional): Device to run on ('cuda' or 'cpu'). Defaults to None
            output_dir (str, optional): Directory to save results. Defaults to "results"
        """
        self.conf = conf
        self.iou = iou
        self.output_dir = output_dir
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Device configuration
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        if self.device == 'cuda':
            torch.backends.cudnn.benchmark = True
        
        # Load model
        print(f"Loading model: {model_path}, using device: {self.device}")
        self.model = YOLO(model_path)
        self.model.to(self.device)
        
        # Configure settings
        self.configure_settings()
    
    def configure_settings(self):
        """Configure detection and alarm settings"""
        # Alarm type configuration
        self.alarm_types = {
            "person_intrusion": ["person", "人", "人员"],
            "vessel_approach": ["ship", "boat", "vessel", "船", "船只"],
            "machinery_intrusion": ["machinery", "machine", "机械"],
            "camera_alarm": ["camera_error", "error"]
        }
        
        # Detection box color configuration (BGR format)
        self.colors = {
            "covered": (0, 255, 0),      # Green - fully covered
            "partially": (0, 255, 255),  # Yellow - partially covered
            "uncovered": (0, 0, 255),    # Red - uncovered
            "default": (255, 0, 0)       # Blue - other detections
        }
    
    def process_image(self, image_path):
        """Process a single image and return JSON format results
        
        Args:
            image_path (str): Path to the input image

        Returns:
            dict: Detection results in JSON format
        """
        start_time = time.time()
        
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return self._error_response(f"Image file does not exist: {image_path}")
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return self._error_response(f"Cannot read image: {image_path}")
            
            # Perform detection
            results = self.model(image_path, conf=self.conf, iou=self.iou, verbose=False)
            result = results[0]
            
            # Process detections
            detections, alarms = self._process_detections(result)
            
            # Visualize results
            vis_path = visualize_detections(image, result, image_path, alarms, self.colors, self.output_dir)
            
            # Prepare output
            output = {
                "success": True,
                "data": {
                    "image_path": image_path,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "processing_time": round(time.time() - start_time, 3),
                    "detections": detections,
                    "alarms": alarms,
                    "visualization_path": vis_path
                },
                "error": None
            }
            
            return output
            
        except Exception as e:
            return self._error_response(str(e))
    
    def _process_detections(self, result):
        """Process detection results, generate detection list and alarm information"""
        detections = []
        alarms = {}
        cargo_areas = []  # Store cargo areas
        
        # If no detection results, return directly
        if result.boxes is None or len(result.boxes) == 0:
            return detections, alarms
        
        # Initialize alarm categories
        for alarm_type in self.alarm_types.keys():
            alarms[alarm_type] = []
        
        # First pass: collect cargo areas
        for box in result.boxes:
            cls_id = int(box.cls.item())
            cls_name = result.names[cls_id].lower()
            if cls_name in ["covered", "partially", "partially_covered", "uncovered"]:
                xyxy = box.xyxy.cpu().numpy()[0].astype(int)
                cargo_areas.append(xyxy)
        
        # Process each detection box
        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls.item())
            cls_name = result.names[cls_id]
            if cls_name.lower() == "error":
                cls_name = "camera_error"
            confidence = float(box.conf.item())
            xyxy = box.xyxy.cpu().numpy()[0].astype(int)
            
            # Create detection result
            detection = {
                "id": i,
                "class_name": cls_name,
                "confidence": round(confidence, 3),
                "bbox": {
                    "x1": int(xyxy[0]),
                    "y1": int(xyxy[1]),
                    "x2": int(xyxy[2]),
                    "y2": int(xyxy[3])
                }
            }
            detections.append(detection)
            
            # Check if alarm needs to be generated
            for alarm_type, keywords in self.alarm_types.items():
                if any(keyword == cls_name.lower() for keyword in keywords):
                    if alarm_type in ["person_intrusion", "vessel_approach", "machinery_intrusion"]:
                        if not cargo_areas or not self._check_overlap_with_cargo(xyxy, cargo_areas):
                            continue
                    
                    alarm = {
                        "object_class": cls_name,
                        "confidence": round(confidence, 3),
                        "location": detection["bbox"]
                    }
                    alarms[alarm_type].append(alarm)
        
        # Remove empty alarm categories
        alarms = {k: v for k, v in alarms.items() if v}
        
        return detections, alarms
    
    def _check_overlap_with_cargo(self, obj_box, cargo_areas):
        """Check if target overlaps with any cargo area"""
        def calculate_overlap(box1, box2):
            x1 = max(box1[0], box2[0])
            y1 = max(box1[1], box2[1])
            x2 = min(box1[2], box2[2])
            y2 = min(box1[3], box2[3])
            
            if x1 < x2 and y1 < y2:
                return True
            return False
        
        for cargo_box in cargo_areas:
            if calculate_overlap(obj_box, cargo_box):
                return True
        return False
    
    def _error_response(self, error_message):
        """Generate error response"""
        return {
            "success": False,
            "data": None,
            "error": error_message
        } 