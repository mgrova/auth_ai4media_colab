#!/usr/bin/env python3

import os 
import sys
import numpy as np
import math

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from argparse import ArgumentParser

uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
sys.path.append(uppath(__file__, 2))

from datasets.dataset_utils import read_trajectory_poses_from_file, save_pose_to_file, create_poses_file


def __create_vec_btw_poses(curr_pos, tgt_pos, num_steps):
    # Calculate step size for each axis
    step_x = (tgt_pos[0] - curr_pos[0]) / num_steps
    step_y = (tgt_pos[1] - curr_pos[1]) / num_steps
    step_z = (tgt_pos[2] - curr_pos[2]) / num_steps

    movement_vec = []
    movement_vec.append(curr_pos)

    fixed_roll, fixed_pitch, fixed_yaw = curr_pos[3], curr_pos[4], curr_pos[5]

    current_x = curr_pos[0]
    current_y = curr_pos[1]
    current_z = curr_pos[2]
    for _ in range(num_steps):
        # Increment position
        current_x += step_x
        current_y += step_y
        current_z += step_z
        movement_vec.append([current_x, current_y, current_z, fixed_roll, fixed_pitch, fixed_yaw])

    movement_vec.append(tgt_pos)

    return movement_vec

def interpolate_trajectory(input_traj_path, output_traj_path, desired_len):
    poses = read_trajectory_poses_from_file(input_traj_path)
    
    if (len(poses) > desired_len):
        print(f"Input path ({len(poses)}) is longer than desired len ({desired_len})")
        return
    
    interpolated_traj = []
    step_between_poses = int(desired_len / (len(poses) - 1))
    
    # NOTE: We are going to keep orientation during positions interpolation
    curr_pose = poses.pop(0)
    for pose in poses:
        movement_vec = __create_vec_btw_poses(curr_pose, pose, step_between_poses)
        curr_pose = movement_vec.pop(-1)
        interpolated_traj = interpolated_traj + movement_vec

    # Save interpolated trajectory to a file 
    create_poses_file(output_traj_path)
    for pose in interpolated_traj:
        save_pose_to_file(output_traj_path, pose[0:3], pose[3:6])

    print(f"Saved trajectory generated with {len(interpolated_traj)} poses to file '{output_traj_path}'")

if __name__ == "__main__":
    parser = ArgumentParser(description="Interpolate positions of trajectory to desired lenght")
    parser.add_argument('--traj_file', type=str, default=os.getcwd() + '/trajectory_poses.txt')
    parser.add_argument('--output_file', type=str, default=os.getcwd() + '/interpolated_trajectory_poses.txt')
    parser.add_argument('--desired_len', type=int)
    args = parser.parse_args()

    interpolate_trajectory(args.traj_file, args.output_file, args.desired_len)