import logging
import operator
import pathlib
from omegaconf import DictConfig

from ehdg_gaze.common.face_model import FaceModel
from ehdg_gaze.common.face_model_68 import FaceModel68
from ehdg_gaze.common.face_model_mediapipe import FaceModelMediaPipe

# logger = logging.getLogger(__name__)


def get_3d_face_model(config: DictConfig) -> FaceModel:
    if config.face_detector.mode == 'mediapipe':
        return FaceModelMediaPipe()
    else:
        return FaceModel68()


def _expanduser(path: str) -> str:
    if not path:
        return path
    return pathlib.Path(path).expanduser().as_posix()


def expanduser_all(config: DictConfig) -> None:
    if hasattr(config.face_detector, 'dlib_model_path'):
        config.face_detector.dlib_model_path = _expanduser(
            config.face_detector.dlib_model_path)
    config.gaze_estimator.checkpoint = _expanduser(
        config.gaze_estimator.checkpoint)
    config.gaze_estimator.camera_params = _expanduser(
        config.gaze_estimator.camera_params)
    config.gaze_estimator.normalized_camera_params = _expanduser(
        config.gaze_estimator.normalized_camera_params)
    if hasattr(config.demo, 'image_path'):
        config.demo.image_path = _expanduser(config.demo.image_path)
    if hasattr(config.demo, 'video_path'):
        config.demo.video_path = _expanduser(config.demo.video_path)
    if hasattr(config.demo, 'output_dir'):
        config.demo.output_dir = _expanduser(config.demo.output_dir)


def _check_path(config: DictConfig, key: str) -> None:
    path_str = operator.attrgetter(key)(config)
    path = pathlib.Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f'config.{key}: {path.as_posix()} not found.')
    if not path.is_file():
        raise ValueError(f'config.{key}: {path.as_posix()} is not a file.')


def check_path_all(config: DictConfig) -> None:
    if config.face_detector.mode == 'dlib':
        _check_path(config, 'face_detector.dlib_model_path')
    _check_path(config, 'gaze_estimator.checkpoint')
    _check_path(config, 'gaze_estimator.camera_params')
    _check_path(config, 'gaze_estimator.normalized_camera_params')
    if config.demo.image_path:
        _check_path(config, 'demo.image_path')
    if config.demo.video_path:
        _check_path(config, 'demo.video_path')
