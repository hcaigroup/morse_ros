#!/usr/bin/env python  
import sys

import roslib
roslib.load_manifest('kitchen_data_player')
import rospy
import math
import tf
from nav_msgs.msg import Odometry

# This file subscribes to TF data from Openni Tracker and writes the transform from /map to /neck_1 into 
# the file provided as argument. 

if __name__ == '__main__':
    rospy.init_node('spram_converter')

    listener = tf.TransformListener()
    pose_pub = rospy.Publisher('/Human/Pose', Odometry)

    FILE = open(sys.argv[1],"w")
    FILE.write("instance,time,BECX,BECY,BECZ,BEC_ROTX,BEC_ROTY,BEC_ROTZ\n") 
    instance = 0
    transform_found = False
    neck = ""

    # HACK TO SKIP SEARCH... 
    transform_found = True
    neck = "neck_1"


    while not transform_found and not rospy.is_shutdown():
        try:
            listener.waitForTransform("/map", "/neck_1", rospy.Time(0), rospy.Duration(1.0))
            (trans,rot) = listener.lookupTransform('/map', '/neck_1', rospy.Time(0))
            print("SUCCESS: Found neck_1 transform!")
            neck = "neck_1"
            transform_found = True
        except (tf.LookupException, tf.ConnectivityException, tf.Exception):
            print( "Trying transform from map to neck_1!")

        try:
            listener.waitForTransform("/map", "/neck_2", rospy.Time(0), rospy.Duration(1.0))
            (trans,rot) = listener.lookupTransform('/map', '/neck_2', rospy.Time(0))
            print("SUCCESS: Found neck_2 transform!")
            neck = "neck_2"
            transform_found = True
        except (tf.LookupException, tf.ConnectivityException, tf.Exception):
            print("Trying transform from map to neck_2!")

        try:
            listener.waitForTransform("/map", "/neck_3", rospy.Time(0), rospy.Duration(1.0))
            (trans,rot) = listener.lookupTransform('/map', '/neck_3', rospy.Time(0))
            print("SUCCESS: Found neck_3 transform!")
            neck = "neck_3"
            transform_found = True
        except (tf.LookupException, tf.ConnectivityException, tf.Exception):
            print("Trying transform from map to neck_3!")

        try:
            listener.waitForTransform("/map", "/neck_4", rospy.Time(0), rospy.Duration(1.0))
            (trans,rot) = listener.lookupTransform('/map', '/neck_4', rospy.Time(0))
            print("SUCCESS: Found neck_4 transform!")
            neck = "neck_4"
            transform_found = True
        except (tf.LookupException, tf.ConnectivityException, tf.Exception):
            print("Trying transform from map to neck_4!")


    while not rospy.is_shutdown():
        try:
            listener.waitForTransform("/map", neck, rospy.Time(0), rospy.Duration(1.0))
            (trans,rot) = listener.lookupTransform('/map', neck, rospy.Time(0))

            now = rospy.Time.now()
            human_pos = Odometry()
            human_pos.header.frame_id = "/map"
            human_pos.child_frame_id = "/human_pose"
            
            human_pos.pose.pose.position.x = trans[0]
            human_pos.pose.pose.position.y = trans[1]
            #human_pos.pose.pose.position.z = trans[2]

            human_pos.pose.pose.orientation.x = rot[0]
            human_pos.pose.pose.orientation.y = rot[1]
            human_pos.pose.pose.orientation.z = rot[2]
            human_pos.pose.pose.orientation.w = rot[3]
            
            human_pos.header.stamp = now
            pose_pub.publish(human_pos)
            
            print("Human is at %s %s %s (time: %s.%s)"%(trans[0], trans[1], trans[2], now.secs, now.nsecs))
            FILE.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%(instance,now,trans[0],trans[1],trans[2],rot[0],rot[1],rot[2],rot[3]))
            instance = instance + 1
            rospy.sleep(0.08)

        except (tf.LookupException, tf.ConnectivityException, tf.Exception):
            print("Could not find transform from map to neck!")

       
