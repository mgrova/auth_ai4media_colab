#!/usr/bin/env python3

from pynput import keyboard
import numpy as np
import os 

from threading import Lock
from copy import deepcopy

'''
Class to generate 6DoF pose using keyboard.
+X, -X -> KeyUp, KeyDown
+Y, -Y -> KeyLeft, KeyRight
+Z, -Z -> Q, A

+pitch, -pitch -> W, S
+yaw, -yaw     -> E, R
'''
class KeyboardController():
    def __init__(self, position_step = 1.0, angle_step = 5.0):
        self.__position_step  = position_step
        self.__angle_step_deg = angle_step

        self.__keyboard_mtx = Lock()
        # x, y, z, roll_deg, pitch_deg, yaw_deg
        self.__pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.__poses_array = []

        # Collect events until released
        self.__listener = keyboard.Listener(on_press=self.__on_press, on_release=self.__on_release)

        self.__received_new_pose = False
        self.__listener.start()

    def __del__(self):
        self.__listener.join()

        if (len(self.__poses_array) > 0):
            self.__save_poses_to_file(self.__poses_array)

    def __save_poses_to_file(self, poses_list):
        file_path = os.getcwd() + '/../trajectory_poses.txt'
        if (os.path.isfile(file_path)):
            os.remove(file_path)
        file = open(file_path, 'w+')
        file.write("#Coordinates in World Coordinate System\n")
        file.write("#x y z roll_rad pitch_rad yaw_rad\n")
        for pose in poses_list:
            file.write("{} {} {} {} {} {}\n".format(pose[0], pose[1], pose[2], 
                                                    np.deg2rad(pose[3]), np.deg2rad(pose[4]), np.deg2rad(pose[5])))
        file.close()


    def listener_alive(self) -> bool:
        return self.__listener.is_alive()

    def get_pose(self) -> list:
        self.__received_new_pose = False
        with self.__keyboard_mtx:
            return deepcopy(self.__pose)
        
    def received_new_pose(self) -> bool:
        return self.__received_new_pose
    
    def __on_press(self, key):
        # print('{} released'.format(key))
        x = str(key)
        x = x.strip("''")
        with self.__keyboard_mtx:
            if x == 'Key.esc':
                print("Exiting mode")
                return False
            # Use up and down to move in X axis
            elif x == 'Key.up':
                self.__pose[0] += self.__position_step
            elif x == 'Key.down':
                self.__pose[0] -= self.__position_step
            # Use left and right to move in Y axis
            elif x == 'Key.left':
                self.__pose[1] += self.__position_step
            elif x == 'Key.right':
                self.__pose[1] -= self.__position_step
            # Use q and a to move in Z axis
            elif x == 'q':
                self.__pose[2] += self.__position_step
            elif x == 'a':
                self.__pose[2] -= self.__position_step
            # Use e and d to control in pitch angle in deg
            elif x == 'w':
                self.__pose[4] += self.__angle_step_deg
            elif x == 's':
                self.__pose[4] -= self.__angle_step_deg
            # Use e and r to control in yaw angle in deg
            elif x == 'e':
                self.__pose[5] += self.__angle_step_deg
            elif x == 'r':
                self.__pose[5] -= self.__angle_step_deg
            # Use enter to save pose to generate path
            elif x == 'Key.enter':
                print(f"Saved position ({self.__pose[0]}, {self.__pose[1]}, {self.__pose[2]}) RPY: ({self.__pose[3]}, {self.__pose[4]}, {self.__pose[5]})")
                self.__poses_array.append(deepcopy(self.__pose))
            else:
                pass
        self.__received_new_pose = True

    def __on_release(self, key):
        try:
            pass
            # print('alphanumeric key {0} pressed'.format(key.char))
        except AttributeError:
            print('special key {0} pressed'.format(key))

if __name__ == "__main__":

    controller = KeyboardController()
    
    while(controller.listener_alive()):
        if (controller.received_new_pose()):
            print(controller.get_pose())