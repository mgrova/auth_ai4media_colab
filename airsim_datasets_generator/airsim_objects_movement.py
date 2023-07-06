#!/usr/bin/env python3

# In settings.json first activate computer vision mode: 
# https://github.com/Microsoft/AirSim/blob/master/docs/image_apis.md#computer-vision-mode

import airsim
import pprint
import time

client = airsim.VehicleClient()
client.confirmConnection()

# all the positions are referenced to "Player Start" coordinate system in UE4 editor

target_object = "Race_Cycling5_center"

# search object by name: 
pose1 = client.simGetObjectPose(target_object)
print(target_object + "- Position: %s, Orientation: %s" % (pprint.pformat(pose1.position),
    pprint.pformat(pose1.orientation)))

# here we move with teleport enabled so collisions are ignored
for t in range(0, 10):
    pose1.position = pose1.position + airsim.Vector3r(1.0, 1.0, 0.0)
    success = client.simSetObjectPose(target_object, pose1, True)
    time.sleep(0.5)
    if not success:
        print("Error moving " + target_object)
        break
