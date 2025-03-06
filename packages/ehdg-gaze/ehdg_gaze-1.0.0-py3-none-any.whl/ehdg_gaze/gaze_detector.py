import datetime
import logging
import sys
import cv2
import numpy as np
from omegaconf import DictConfig
from ehdg_gaze.common import Face, FacePartsName, Visualizer
from ehdg_gaze.gaze_estimator import GazeEstimator
from ehdg_gaze.utils import get_3d_face_model


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# This function is to display the process progressing
def print_percent_done(index_input, total, bar_len=50, title_input='Please wait'):
    percent_done = (index_input + 1) / total * 100
    percent_done_round = round(percent_done, 1)

    done = int(round(percent_done_round / (100 / bar_len)))
    togo = bar_len - done

    done_str = '=' * done
    togo_str = '_' * togo

    sys.stdout.write(f'\r{title_input}: [{done_str}{togo_str}] {percent_done_round}% done')
    sys.stdout.flush()


class GazeDetector:
    def __init__(self, config: DictConfig):
        self.config = config
        self.gaze_estimator = GazeEstimator(config)
        face_model_3d = get_3d_face_model(config)
        self.visualizer = Visualizer(self.gaze_estimator.camera,
                                     face_model_3d.NOSE_INDEX)
        self.stop = False
        self.show_bbox = self.config.demo.show_bbox
        self.show_head_pose = self.config.demo.show_head_pose
        self.show_landmarks = self.config.demo.show_landmarks
        self.show_normalized_image = self.config.demo.show_normalized_image
        self.show_template_model = self.config.demo.show_template_model

    def detect_video(self, video_input, out_dir):
        input_video = cv2.VideoCapture(video_input)
        frame_width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        print("Frame width:", frame_width)
        frame_height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("Frame height:", frame_height)
        frame_rate = int(input_video.get(cv2.CAP_PROP_FPS))
        print("Frame rate:", frame_rate)
        frame_count = int(input_video.get(cv2.CAP_PROP_FRAME_COUNT))
        print("Frame count:", frame_count)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        v_writer = cv2.VideoWriter(out_dir, fourcc, frame_rate, (frame_width, frame_height), True)
        count = 0

        if self.config.write_csv:
            pass

        while True:
            ok, frame = input_video.read()
            if ok:
                gazed_image, faces = self.detect_gaze_and_get_data(frame)
                if self.config.display_bool:
                    cv2.imshow("Gazed Image", gazed_image)
                v_writer.write(gazed_image)
                count += 1
                print_percent_done(count, frame_count)
                if self.config.write_csv:
                    pass
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        v_writer.release()
        print("")
        print(f"{out_dir} is generated.")

    def detect_gaze_and_get_data(self, frame_input):
        undistorted = cv2.undistort(frame_input,
                                    self.gaze_estimator.camera.camera_matrix,
                                    self.gaze_estimator.camera.dist_coefficients)

        self.visualizer.set_image(frame_input.copy())
        faces = self.gaze_estimator.detect_faces(undistorted)
        for face in faces:
            self.gaze_estimator.estimate_gaze(undistorted, face)
            self._draw_face_bbox(face)
            self._draw_head_pose(face)
            self._draw_landmarks(face)
            self._draw_face_template_model(face)
            self._draw_gaze_vector(face)
            self._display_normalized_image(face)

        if self.config.demo.use_camera:
            self.visualizer.image = self.visualizer.image[:, ::-1]

        return self.visualizer.image, faces

    @staticmethod
    def _create_timestamp() -> str:
        dt = datetime.datetime.now()
        return dt.strftime('%Y%m%d_%H%M%S')

    def _draw_face_bbox(self, face: Face) -> None:
        if not self.show_bbox:
            return
        self.visualizer.draw_bbox(face.bbox)

    def _draw_head_pose(self, face: Face) -> None:
        if not self.show_head_pose:
            return
        # Draw the axes of the model coordinate system
        length = self.config.demo.head_pose_axis_length
        self.visualizer.draw_model_axes(face, length, lw=2)

        euler_angles = face.head_pose_rot.as_euler('XYZ', degrees=True)
        pitch, yaw, roll = face.change_coordinate_system(euler_angles)
        # logger.info(f'[head] pitch: {pitch:.2f}, yaw: {yaw:.2f}, '
        #             f'roll: {roll:.2f}, distance: {face.distance:.2f}')

    def _draw_landmarks(self, face: Face) -> None:
        if not self.show_landmarks:
            return
        self.visualizer.draw_points(face.landmarks,
                                    color=(0, 255, 255),
                                    size=1)

    def _draw_face_template_model(self, face: Face) -> None:
        if not self.show_template_model:
            return
        self.visualizer.draw_3d_points(face.model3d,
                                       color=(255, 0, 525),
                                       size=1)

    def _display_normalized_image(self, face: Face) -> None:
        if not self.config.demo.display_on_screen:
            return
        if not self.show_normalized_image:
            return
        if self.config.mode == 'MPIIGaze':
            reye = face.reye.normalized_image
            leye = face.leye.normalized_image
            normalized = np.hstack([reye, leye])
        elif self.config.mode in ['MPIIFaceGaze', 'ETH-XGaze']:
            normalized = face.normalized_image
        else:
            raise ValueError
        if self.config.demo.use_camera:
            normalized = normalized[:, ::-1]
        cv2.imshow('normalized', normalized)

    def _draw_gaze_vector(self, face: Face) -> None:
        length = self.config.demo.gaze_visualization_length
        if self.config.mode == 'MPIIGaze':
            # print(self.config.mode)
            for key in [FacePartsName.REYE, FacePartsName.LEYE]:
                eye = getattr(face, key.name.lower())
                self.visualizer.draw_3d_line(
                    eye.center, eye.center + length * eye.gaze_vector)
                pitch, yaw = np.rad2deg(eye.vector_to_angle(eye.gaze_vector))
                # logger.info(
                #     f'[{key.name.lower()}] pitch: {pitch:.2f}, yaw: {yaw:.2f}')
        elif self.config.mode in ['MPIIFaceGaze', 'ETH-XGaze']:
            # print(self.config.mode)
            self.visualizer.draw_3d_line(
                face.center, face.center + length * face.gaze_vector)
            pitch, yaw = np.rad2deg(face.vector_to_angle(face.gaze_vector))
            # logger.info(f'[face] pitch: {pitch:.2f}, yaw: {yaw:.2f}')
        else:
            raise ValueError
