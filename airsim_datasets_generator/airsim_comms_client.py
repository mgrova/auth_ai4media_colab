#!/usr/bin/env python3

# In settings.json first activate computer vision mode:
# https://github.com/Microsoft/AirSim/blob/master/docs/image_apis.md#computer-vision-mode

import airsim

import datetime
from argparse import ArgumentParser
import numpy as np
import cv2
import os
from tqdm import tqdm

from datasets.dataset_utils import create_airsim_dataset_folder, read_trajectory_poses_from_file, build_K_from_params

# Be able to configure the cameras
class AirsimManager:
    def __init__(self, args) -> None:
        client = airsim.VehicleClient()
        client.confirmConnection()
        self.__client = client

        '''
        We are attaching the camera to the origin of the vehicle, so we only 
        need to move the vehicle to change the camera pose.
        '''
        initial_camera_pose = airsim.Pose(airsim.Vector3r(0.0, 0.0, 0.0), 
                                          airsim.to_quaternion(0.0, 0.0, 0.0)) #radians
        self.__client.simSetCameraPose("0", initial_camera_pose)

        cv2.startWindowThread()
        cv2.namedWindow("RGB Image",   cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow("Depth Image", cv2.WINDOW_AUTOSIZE)
        
        self.__curr_imgs_id = 0
        self.__save_dataset = args.save_dataset
        if (self.__save_dataset):
            if args.dataset_folder.endswith('/'):
                args.dataset_folder = args.dataset_folder[:-1]
            
            self.__dataset_folder = args.dataset_folder + '/dataset_{}'.format(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
            create_airsim_dataset_folder(self.__dataset_folder)

        self.requests = [airsim.ImageRequest("0", airsim.ImageType.Scene, False, False),
                         airsim.ImageRequest("0", airsim.ImageType.DepthPlanar, True, False)]

        if (self.__save_dataset):
            intrinsics = self.get_camera_intrinsics(0)
            with open(self.__dataset_folder + '/intrinsics.txt', "ab") as file:
                np.savetxt(file, intrinsics, fmt='%.6f', delimiter=' ')
                file.write(b"\n")

    def __del__(self) -> None:
        # currently reset() doesn't work in CV mode. Below is the workaround
        self.__client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(0.0, 0.0, -50.0), 
                                                    airsim.to_quaternion(0.0, 0.0, 0.0)), True)
        cv2.destroyAllWindows()
    
    def enable_weather(self):
        self.__client.simEnableWeather(True)

    def change_weather(self, weather_param, percentage):
        # if percentage not in range(0.0, 1.0):
            # print('Invalid value')
            # return
        self.__client.simSetWeatherParameter(weather_param, percentage)

    def get_camera_intrinsics(self, camera_name):
        raw_img = self.__client.simGetImage(str(camera_name),airsim.ImageType.Scene)
        if not raw_img:
            print("Unable to obtain image to estimate intrinsics")
            return
        png = cv2.imdecode(airsim.string_to_uint8_array(raw_img), cv2.IMREAD_UNCHANGED)
        height, width, _ = png.shape
        fov = self.__client.simGetCameraInfo(str(camera_name)).fov

        K_mat = build_K_from_params(width, height, fov)
        return K_mat
        
        
    def get_vehicle_images(self) -> None:
        responses = self.__client.simGetImages(self.requests)
        id_str = str(self.__curr_imgs_id).zfill(4)
        for response in responses:
            if (response.image_type == airsim.ImageType.DepthPlanar):
                img_depth = np.array(response.image_data_float, dtype=np.float32)
                img_depth = img_depth.reshape(response.height, response.width)
                
                normalized_depth = cv2.normalize(img_depth, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
                colored_depth = cv2.applyColorMap(normalized_depth, cv2.COLORMAP_JET)
                cv2.imshow("Depth Image", colored_depth)

                if (self.__save_dataset):
                    cv2.imwrite(self.__dataset_folder + '/depth/depth_{}.png'.format(id_str), img_depth)

            elif (response.image_type == airsim.ImageType.Scene):
                img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
                img_rgb = img1d.reshape(response.height, response.width, 3)
                cv2.imshow("RGB Image", img_rgb)
                
                if (self.__save_dataset):
                    cv2.imwrite(self.__dataset_folder + '/rgb/rgb_{}.png'.format(id_str), img_rgb)
    
            else:
                print("Error: Unrecognized image type: {}".format(response.image_type))
                return

        if (self.__save_dataset):
            curr_uav_pos = self.get_vehicle_pose().position
            curr_uav_ori = self.get_vehicle_pose().orientation

            # pitch, roll, yaw = airsim.to_eularian_angles(curr_uav_ori)
            
            with open(self.__dataset_folder + '/poses.txt', "a") as file:
                file.write("{} {} {} {} {} {} {} {}\n".format(id_str, curr_uav_pos.x_val, curr_uav_pos.y_val, -1.0 * curr_uav_pos.z_val,
                        curr_uav_ori.w_val, curr_uav_ori.x_val, curr_uav_ori.y_val, curr_uav_ori.z_val))

        self.__curr_imgs_id = self.__curr_imgs_id + 1
        cv2.waitKey(1)

    def update_vehicle_pose(self, position, roll_rad, pitch_rad, yaw_rad):
        self.__client.simSetVehiclePose(
            airsim.Pose(position, airsim.to_quaternion(pitch_rad, roll_rad, yaw_rad)), 
            True)

    def get_vehicle_pose(self) -> airsim.Pose:
        return self.__client.simGetVehiclePose()
    
    def update_camera_orientation(self, camera_name, roll_rad, pitch_rad, yaw_rad) -> None:
        camera_position = airsim.Vector3r(0.0, 0.0, 0.0)
        self.__curr_gimbal_q = airsim.to_quaternion(pitch_rad, roll_rad, yaw_rad)
        self.__client.simSetCameraPose(camera_name, 
                                       airsim.Pose(camera_position, self.__curr_gimbal_q)
                                       )
        
    def get_camera_pose(self, camera_name) -> airsim.Pose:
        return self.__client.simGetCameraPose(camera_name)


def main(args):

    manager = AirsimManager(args)
    print("Created AirsimManager")

    if args.sim_weather:
        manager.enable_weather()
        manager.change_weather(airsim.WeatherParameter.Fog, 0.2)

    poses = read_trajectory_poses_from_file(os.getcwd() + '/trajectory_poses.txt')
    for pose in poses:
        curr_position = airsim.Vector3r(pose[0], pose[1], -1.0 * pose[2])
        manager.update_vehicle_pose(curr_position, pose[3], pose[4], pose[5])

        manager.get_vehicle_images()


if __name__ == "__main__":
    # Implement argument parser to select stuff
    parser = ArgumentParser(description="Simulate specified trajectory in Airsim")
    parser.add_argument("--save_dataset", action="store_true", default=False)
    parser.add_argument('--dataset_folder', type=str, default=os.getcwd())
    parser.add_argument("--sim_weather", action="store_true", default=False)

    args = parser.parse_args()
    # TODO: Configure sensors and cameras in settings.json

    main(args)



