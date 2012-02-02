#!/usr/bin/env python
import csv
import math
import sys
import time

import roslib; roslib.load_manifest('kitchen_data_player')
import rospy
import tf
from tf.transformations import quaternion_from_euler

from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseArray

# This script takes as input kinect data recorded in the Garching Lab using the setup from the TUM kitchen dataset. I generated a symbolic task description based 
# on the location model the is hardcoded here.

# This function checks in which cluster the given point is and assigns the correct location to it. The multivariate gaussians are hardcoded here and generated by WEKA
# TODOTODOTODO: This has to be replaced by an general function that gets the coordinates of the furniture from the knowledge base and generates the gaussian functions dynamically


def calculate_gaussian_prob(x,y,mean_x, mean_y,dev_x, dev_y):
     return math.exp( - ( (((x - mean_x) * (x - mean_x)) / (2 * dev_x * dev_x)) + ((y - mean_y) * (y - mean_y)) / (2 * dev_y * dev_y)))

# This function checks in which cluster the given point is and assigns the correct location to it. The multivariate gaussians are hardcoded here and generated by WEKA
def get_cluster_number(x, y):

    #x = x * 1000
    #y = y * 1000
    p1 = 0
    p2 = 0
    p3 = 0
    p4 = 0
    drawer_gauss_mean = None
    stove_gauss_mean = None
    cupboard_gauss_mean = None
    table_gauss_mean = None

    # get gaussian means depending on furniture positions
    try:
        tf_listener.waitForTransform("map", "table_gauss_mean", rospy.Time(0), rospy.Duration(0.1))
        (table_gauss_mean, table_gauss_rot) = tf_listener.lookupTransform("map", "table_gauss_mean", rospy.Time(0))

        tf_listener.waitForTransform("map", "cupboard_gauss_mean", rospy.Time(0), rospy.Duration(0.1))
        (cupboard_gauss_mean, cupboard_gauss_rot) = tf_listener.lookupTransform("map", "cupboard_gauss_mean", rospy.Time(0))

        tf_listener.waitForTransform("map", "drawer55_gauss_mean", rospy.Time(0), rospy.Duration(0.1))
        (drawer_gauss_mean, drawer_gauss_rot) = tf_listener.lookupTransform("map", "drawer55_gauss_mean", rospy.Time(0))

        tf_listener.waitForTransform("map", "stove_gauss_mean", rospy.Time(0), rospy.Duration(0.1))
        (stove_gauss_mean, stove_gauss_rot) = tf_listener.lookupTransform("map", "stove_gauss_mean", rospy.Time(0))

        # calculate maximum values of gaussians for confidence probability
        #drawer
        p1 = calculate_gaussian_prob(x,y,drawer_gauss_mean[0],drawer_gauss_mean[1], 0.0772,0.09855)
        p1_max = calculate_gaussian_prob(drawer_gauss_mean[0],drawer_gauss_mean[1],drawer_gauss_mean[0],drawer_gauss_mean[1], 0.0772,0.09855)
        # table
        p2 = calculate_gaussian_prob(x,y,table_gauss_mean[0],table_gauss_mean[1], 0.091, 0.1075)
        p2_max = calculate_gaussian_prob(table_gauss_mean[0],table_gauss_mean[1],table_gauss_mean[0],table_gauss_mean[1], 0.091, 0.1075)
        # stove
        p3 =  calculate_gaussian_prob(x,y,stove_gauss_mean[0], stove_gauss_mean[1], 0.0619, 0.13696)
        p3_max = calculate_gaussian_prob(stove_gauss_mean[0], stove_gauss_mean[1],stove_gauss_mean[0], stove_gauss_mean[1], 0.0619, 0.13696)
        # cupboard
        p4 =  calculate_gaussian_prob(x,y,cupboard_gauss_mean[0], cupboard_gauss_mean[1], 0.0706725, 0.0726388)
        p4_max =  calculate_gaussian_prob(cupboard_gauss_mean[0], cupboard_gauss_mean[1],cupboard_gauss_mean[0], cupboard_gauss_mean[1], 0.0706725, 0.0726388)

    except (tf.Exception, tf.LookupException, tf.ConnectivityException):
        print('TF Lookup exception while trying to look up Gaussian means') 

    cluster = -1
    location = ''
    p = 0
    #threshhold = 0.00001
    #threshhold = 0.0000000001
    threshhold = 0.0000000001

    if p1 > p2 and p1 > p3 and p1 > p4 and p1 > threshhold:
        cluster = 1
        location = 'drawer'
        p = p1/p1_max
        #print("Human is in cluster %s with prob: %s"%(location, p1))
    elif p2 > p1 and p2 > p3 and p2 > p4 and p2 > threshhold:
        cluster = 2
        location = 'table'
        p = p2/p2_max
        #print("Human is in cluster %s with prob: %s"%(location, p2))
    elif p3 > p1 and p3 > p2 and p3 > p4 and p3 > threshhold:
        cluster = 3
        location = 'stove'
        p = p3/p3_max
        #print("Human is in cluster %s with prob: %s"%(location, p3))
    elif p4 > p1 and p4 > p2 and p4 > p3 and p4 > threshhold:
        cluster = 4
        location = 'cupboard'
        p = p4/p4_max
        #print("Human is in cluster %s with prob: %s"%(location, p4))
    else:
        cluster = -1
        location = 'none'
        #print("WARNING, could not find location of that object (p1,p2,p3,p4): %s, %s, %s, %s"%(p1, p2, p3, p4))
    return cluster, location, p

# publishes the mean-values of the gaussians for the human positino
def publish_gaussians():
    # Use TF to calculate relative area definitions

    # Gaussians depending on edges of furniture and object/furniture positions
    br.sendTransform((0.205067,-0.0136504 , 0), 
                     quaternion_from_euler(0,0,0),
                     rospy.Time.now(),
                     "table_gauss_mean",
                     "plate_edge")

    br.sendTransform((0.366749, 0.088665, 0), 
                     quaternion_from_euler(0,0,0),
                     rospy.Time.now(),
                     "drawer55_gauss_mean",
                     "drawer55_edge")

    br.sendTransform((0.1462250, 0.1426716 , 0), 
                     quaternion_from_euler(0,0,0),
                     rospy.Time.now(),
                     "stove_gauss_mean",
                     "placemat_edge")
    # TODO Here, i manually set this to minus, but this should actually be calculated 
    # based on the location of the door of the cupboard
    br.sendTransform((0.42658, -0.107175 , 0), 
                     quaternion_from_euler(0,0,0),
                     rospy.Time.now(),
                     "cupboard_gauss_mean",
                     "drawer115_edge")

def publish_kinect():
    kinect_x = -1.249
    kinect_y = 1.34

    br.sendTransform((kinect_x, kinect_y, 0),
                     quaternion_from_euler(0,0,0) ,
                     rospy.Time.now(),
                     "kinect",
                     "countertop_middle")

# Publishes the (hard-coded) locations of the furniture using tf
def publish_furniture():

    #br = tf.TransformBroadcaster()
    # Furniture

    # from logged object data (here relative to table_middle)
    plate_x = -0.15
    plate_y = 0.4
    plate_theta = 3.1415
    
    # from semantic map (Here generated in reference to countertop middle)
    #table_x = 2.59
    #table_y = 4.37
    #table_theta = -1.5707963705062866

    table_depth = 0.60
    table_theta = 3.1415

    # from logged object data
    placemat_x = 0.3815425
    placemat_y = 2.0313084
    placemat_theta = 0
    
    # from sematic map
    stove_x = 0.32918193
    stove_y = 1.9835850
    stove_theta = 0
    stove_depth = 0.5766061

    # from semantic map (Drawer55)
    #drawer55_x = 1.0533205
    drawer55_x = 1.1533205
    drawer55_y = 1.1516107
    drawer55_theta = -0.08859264105558395
    drawer55_depth = 0.580982

    # from semantic map (Drawer155)
    #drawer115_x = -1.87053
    #drawer115_y = 1.1917095
    drawer115_x = -1.57053
    drawer115_y = 1.3917095
    drawer115_theta = -0.08859264105558395
    drawer115_depth = 0.6

    dishwasher_x = 1.0941718
    dishwasher_y = 0.44037533
    dishwasher_theta =-0.08859264850616455
    dishwasher_depth = 0.580982

    #countertop_middle_x = -1.9426385
    #countertop_middle_y = 2.0035133
    countertop_middle_x = -1.5426385
    countertop_middle_y = 2.29133
    countertop_middle_theta = -1.6593890190124512
    countertop_middle_width = 0.79999995
    countertop_middle_depth = 2.49

    countertop_kitchenette_x = 1.1006587
    countertop_kitchenette_y = 0.54706275
    countertop_kitchenette_theta = -1.6593890190124512
    countertop_kitchenette_width = 0.575
    countertop_kitchenette_depth = 2.05
    

    br.sendTransform((countertop_middle_x, countertop_middle_y, 0),
                     tf.transformations.quaternion_from_euler(0, 0, countertop_middle_theta),
                     rospy.Time.now(),
                     "countertop_middle",
                     "map")

    br.sendTransform((countertop_kitchenette_x, countertop_kitchenette_y, 0),
                     tf.transformations.quaternion_from_euler(0, 0, countertop_kitchenette_theta),
                     rospy.Time.now(),
                     "countertop_kitchenette",
                     "map")

    br.sendTransform((countertop_middle_depth/2, countertop_middle_width/2, 0),
                     tf.transformations.quaternion_from_euler(0, 0, 0),
                     rospy.Time.now(),
                     "countertop_middle_edge",
                     "countertop_middle")

    br.sendTransform((1.41, 0.395, 0),
                     tf.transformations.quaternion_from_euler(0, 0, 0),
                     rospy.Time.now(),
                     "table_middle",
                     "countertop_middle_edge")
    
    br.sendTransform((countertop_kitchenette_x, countertop_kitchenette_y, 0),
                     tf.transformations.quaternion_from_euler(0, 0, countertop_kitchenette_theta),
                     rospy.Time.now(),
                     "countertop_kitchenette",
                     "map")

    br.sendTransform((drawer115_x, drawer115_y, 0),
                     tf.transformations.quaternion_from_euler(0, 0, drawer115_theta),
                     rospy.Time.now(),
                     "drawer115",
                     "map")

    br.sendTransform((dishwasher_x, dishwasher_y, 0),
                     tf.transformations.quaternion_from_euler(0, 0, dishwasher_theta),
                     rospy.Time.now(),
                     "dishwasher",
                     "map")

    br.sendTransform((0, 0, 0),
                     tf.transformations.quaternion_from_euler(0, 0, 0),
                     rospy.Time.now(),
                     "table",
                     "table_middle")
                     
    br.sendTransform((-table_depth/2, 0, 0),
                     tf.transformations.quaternion_from_euler(0, 0, 3.1415),
                     rospy.Time.now(),
                     "table_edge",
                     "table")
    
    br.sendTransform((plate_x, plate_y, 0),
                     tf.transformations.quaternion_from_euler(0, 0, plate_theta),
                     rospy.Time.now(),
                     "plate",
                     "table_middle")

    br.sendTransform((drawer55_x, drawer55_y, 0),
                     tf.transformations.quaternion_from_euler(0, 0, drawer55_theta),
                     rospy.Time.now(),
                     "drawer55",
                     "map")
    
    # Edge of drawer as reference to where human is standing                 
    br.sendTransform((-drawer55_depth/2, 0, 0),
                     tf.transformations.quaternion_from_euler(0, 0, 3.1415),
                     rospy.Time.now(),
                     "drawer55_edge",
                     "drawer55")

    # object that is on the dishwasher
    br.sendTransform((0, 0, 0),
                     tf.transformations.quaternion_from_euler(0, 0, 0),
                     rospy.Time.now(),
                     "placemat",
                     "dishwasher")
    
    br.sendTransform((-dishwasher_depth/2, 0, 0),
                     tf.transformations.quaternion_from_euler(0, 0, 3.1415),
                     rospy.Time.now(),
                     "dishwasher_edge",
                     "dishwasher")
    br.sendTransform((0, 0, 0),
                     tf.transformations.quaternion_from_euler(0, 0, 0),
                     rospy.Time.now(),
                     "placemat_edge",
                     "dishwasher_edge")               

    br.sendTransform((drawer115_depth/2, 0, 0),
                     tf.transformations.quaternion_from_euler(0, 0, 0),
                     rospy.Time.now(),
                     "drawer115_edge",
                     "drawer115")
    try:
        now = rospy.Time.now() - rospy.Duration(0.0)
        tf_listener.waitForTransform("dishwasher_edge", "placemat", rospy.Time(0), rospy.Duration(0.001))
        (placemat_trans, placemat_rot) = tf_listener.lookupTransform("dishwasher_edge", "placemat", rospy.Time(0))

        tf_listener.waitForTransform("table_edge", "plate", rospy.Time(0), rospy.Duration(0.001))
        (plate_trans, plate_rot) = tf_listener.lookupTransform("table_edge", "plate", rospy.Time(0))
        #print("Trans: %s, %s, %s"%(trans[0], trans[1], trans[2]))
        
        br.sendTransform((0, 0, 0),
                     tf.transformations.quaternion_from_euler(0, 0, 0),
                     rospy.Time.now(),
                     "placemat_edge",
                     "dishwasher_edge")
                     
        br.sendTransform((0, plate_trans[1], 0),
                     tf.transformations.quaternion_from_euler(0, 0, 0),
                     rospy.Time.now(),
                     "plate_edge",
                     "table_edge")
    except (tf.Exception, tf.LookupException, tf.ConnectivityException):
        print('.')

            
posesReader = csv.DictReader(open(sys.argv[1], 'rb'), delimiter=',', quotechar='|')

# Init ROSnode
pose_pub = rospy.Publisher('kitchen_pose', PoseStamped)             # current pose

rospy.init_node('kitchen_player')

br = tf.TransformBroadcaster()
tf_listener = tf.TransformListener()
global_x = 0
global_y = 0
last_global_x = 0
last_global_y = 0
location = 'none'
last_location = 'none'
true_location = None
timesteps = 0
true_time = 0
semantic_instance = 0
velocity = 0

# for velocity calculateion
framecounter = 0
moving_counter = 0
standing_counter = 0
standing_still = False
timecounter = 0

location_starttime = 0
location_endtime = 0
ctime = 0
last_ctime = 0
loc_duration = 0
delta_time = 0

p_sum = 0
p_count = 0
p_avg = 0
last_p_avg = 0

FILE = open(sys.argv[2],"w")
FILE.write("instance,location,duration,probability\n") 

for row in posesReader:
    publish_furniture()
    publish_kinect()
    publish_gaussians()

    #TODO: include and calculate orientation
    theta = 0
    
    quat = quaternion_from_euler(0,0,0)
    br.sendTransform((float(row['z']), float(row['x']), 0),
                     quat,
                     rospy.Time.now(),
                     "human_pose",
                     "kinect")

    # get human position in reference to map
    try:
        now = rospy.Time.now() - rospy.Duration(0.0)
        tf_listener.waitForTransform("map", "human_pose", rospy.Time(0), rospy.Duration(0.001))
        (human_trans, human_rot) = tf_listener.lookupTransform("map", "human_pose", rospy.Time(0))
        global_x = human_trans[0]
        global_y = human_trans[1]
        #print("humantrans: x: %s, y: %s"%(human_trans[0], human_trans[1]))
       
    except (tf.Exception, tf.LookupException, tf.ConnectivityException):
        print('WARNING: TF could not lookup human_pose->map transformation')

    frames = 15

    if framecounter%frames == 1:
        last_global_x = global_x
        last_global_y = global_y
        
    if framecounter%frames == 0:
            #print("stand/move: %s/%s"%(standing_counter, moving_counter))
        
        # Calculate travelled distance and velocity in current frame
        if last_global_x != 0 and last_global_y != 0:
            delta_x = global_x - last_global_x
            delta_y = global_y - last_global_y
            delta_dist = math.sqrt((delta_x * delta_x) + (delta_y * delta_y))
            velocity = delta_dist * frames

            # If human travelled less than 10 cm, consider him as standing
            # 0.3 seems to not be bad
            if delta_dist < 0.025:
                standing_counter += 1

            # if human is standing
            if standing_counter > 0:
                # get his current location
                cluster, location, p = get_cluster_number(global_x, global_y)

                # if we are standing in a new location than before
                if last_location != location:
                    
                    #last_ctime = float(row['time']) #remember time when location was entered
                    last_ctime = (float(row['Hour']) * 3600 + float(row['Min']) * 60 + float(row['Sek']) + float(row['mSek'])/1000)

                    if p_count != 0:
                    #    print("P: %s"%(p_sum/p_count))
                        p_avg = p_sum/p_count
                       
                        
                    # resetP probability counter and set probability to initial
                    p_count = 1
                    p_sum = p

                    # Write out to file and screen and do not account for human standing somewhere else...
                    if last_location != 'none' and loc_duration > 0.0000000001:
                        print("%s -> %s ( %f seconds, p = %s)"%(semantic_instance, last_location, loc_duration, p_avg))
                        FILE.write("%s,%s,%s,%s\n"%(semantic_instance, last_location, loc_duration,p_avg))
                        semantic_instance += 1
                       
                    # reset duration
                    loc_duration = 0
                    last_location = location

                else: # if we are still in the same location, accumulate time the human spends at the location
                    last_location = location
                    p_sum += p
                    p_count += 1

                    # save for last location at end of logfile
                    last_p_avg = p_sum/p_count

                    ctime = (float(row['Hour']) * 3600 + float(row['Min']) * 60 + float(row['Sek']) + float(row['mSek'])/1000)
                    delta_time = ctime - last_ctime
                    #print("----- %s ----time: %s (delta: %s)"%(location, ctime, delta_time))
                    loc_duration = delta_time
            # if the human is moving
            else:
                #print("Moving")
                location = 'navigation'
                last_ctime = (float(row['Hour']) * 3600 + float(row['Min']) * 60 + float(row['Sek']) + float(row['mSek'])/1000)
                #location_starttime = (float(row['Hour']) * 3600 + float(row['Min']) * 60 + float(row['Sek']) + float(row['mSek'])/1000)
                timecounter = 0

        standing_counter = 0
        moving_counter = 0

    framecounter += 1

    last_global_x = global_x
    last_global_y = global_y
    #realtime
    #time.sleep(0.033333333333)

    time.sleep(0.001)

print("%s -> %s ( %f seconds, p = %s)"%(semantic_instance, last_location, loc_duration, last_p_avg))
FILE.write("%s,%s,%s,%s\n"%(semantic_instance, last_location, loc_duration, last_p_avg))

tf_listener.waitForTransform("map", "table_gauss_mean", rospy.Time(0), rospy.Duration(0.1))
(table_gauss_mean, table_gauss_rot) = tf_listener.lookupTransform("map", "table_gauss_mean", rospy.Time(0))

tf_listener.waitForTransform("map", "cupboard_gauss_mean", rospy.Time(0), rospy.Duration(0.1))
(cupboard_gauss_mean, cupboard_gauss_rot) = tf_listener.lookupTransform("map", "cupboard_gauss_mean", rospy.Time(0))

tf_listener.waitForTransform("map", "drawer55_gauss_mean", rospy.Time(0), rospy.Duration(0.1))
(drawer_gauss_mean, drawer_gauss_rot) = tf_listener.lookupTransform("map", "drawer55_gauss_mean", rospy.Time(0))

tf_listener.waitForTransform("map", "stove_gauss_mean", rospy.Time(0), rospy.Duration(0.1))
(stove_gauss_mean, stove_gauss_rot) = tf_listener.lookupTransform("map", "stove_gauss_mean", rospy.Time(0))

print("table gauss mean: %s, %s, %s"%table_gauss_mean)
print("cupboard gauss mean (drawer115): %s, %s, %s"%cupboard_gauss_mean)
print("drawer gauss mean (drawer55): %s, %s, %s"%drawer_gauss_mean)
print("dishwasher: %s, %s, %s"%stove_gauss_mean)
