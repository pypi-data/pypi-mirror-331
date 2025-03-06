import sys
import argparse
import json
import csv
import os
import importlib.metadata
from importlib.resources import files
import cv2
import subprocess
import numpy as np
from ehdg_gaze.gaze_detector import GazeDetector
from omegaconf import DictConfig, OmegaConf
import time


def get_package_dir(module_name):
    config_dir = files(module_name)
    return str(config_dir)


def main():
    parser = argparse.ArgumentParser(prog='ehdg_gaze',
                                     description='Eye Health Diagnostic Group Gaze Detector.')
    ehdg_gaze_version = importlib.metadata.version('ehdg_gaze')
    parser.add_argument('--version', action='version', version=ehdg_gaze_version),
    parser.add_argument("-i", dest="input_video", required=True, type=str, help="input video.")
    parser.add_argument("-o", dest="output_video", required=False, default=None, type=str, help="output video.")
    parser.add_argument("-t", dest="model_type", required=False, default="eth-xgaze",
                        type=str, choices=['mpiigaze', 'eth-xgaze'],
                        help="model type (eth-xgaze or mpiigaze). Default is eth-xgaze.")
    parser.add_argument("-c", dest="config_path", required=False, default=None, type=str,
                        help="config file path. It must be .config, .json or .yaml.")
    parser.add_argument("-pu", dest="processing_unit", required=False, default="cpu",
                        type=str, choices=['cpu', 'gpu'],
                        help="processing unit (cpu or gpu). Default is cpu.")
    parser.add_argument("--display", dest="display_bool", action='store_true',
                        help='If specified, the video will be displayed.')
    parser.add_argument("--save_data", dest="write_csv", action='store_true',
                        help='If specified, the gaze data will be saved as csv.')

    args = parser.parse_args()

    input_video = args.input_video
    output_video = args.output_video
    model_type = args.model_type
    config_path = args.config_path
    processing_unit = args.processing_unit
    display_bool = args.display_bool
    write_csv = args.write_csv
    pkg_dir = get_package_dir("ehdg_gaze")

    if not os.path.isfile(input_video):
        print(f"Input video is invalid.")
        print(f"Input video: {input_video} is invalid.")
        return

    if output_video is None:
        print("Output video file -o is not provided.")
        print("Therefore, video file name will be ehdg_gaze_video.mp4 and will be in same directory as input file.")
        input_video_file_name = os.path.basename(input_video)
        output_video = str(input_video).replace(input_video_file_name, "ehdg_gaze_video.mp4")
        print(f"Output Video: {output_video}")
    else:
        if str(output_video).lower().endswith(".mp4"):
            print(f"Output Video: {output_video}")
        else:
            print("Output video file must be mp4.")
            return

    print(f"Model Type: {model_type}")

    if config_path is None:
        print("Config file path is not provided.")
        print("Therefore, built-in config will be used.")
        config_path = os.path.join(pkg_dir, "configs", f"{model_type}_config.yaml")
        if os.path.isfile(config_path):
            print(f"Config dir: {config_path}")
        else:
            raise FileNotFoundError(f"Error in retrieving config file path: {config_path} could not be found.")
    else:
        print(f"Config dir: {config_path}")
    config = OmegaConf.load(config_path)
    config.package_dir = pkg_dir
    config.display_bool = display_bool
    config.write_csv = write_csv

    print(f"Processing Unit Type: {processing_unit}")
    print(f"Display Video: {display_bool}")
    g_detector = GazeDetector(config)
    start_time = time.time()
    g_detector.detect_video(input_video, output_video)
    print(f"The process took {time.time() - start_time} sec.")
