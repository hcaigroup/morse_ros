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

# Usage: calculate_plan_confidence_value.py symbolic_plan.csv

def get_gauss_probability(x, mean, deviation):
    return (1/(deviation * math.sqrt(2*math.pi))) * math.exp((-1/2)*( ((x-mean)/deviation) *  ((x-mean)/deviation)))

def get_confidence(d, mean, deviation):
    p_max = (1/(deviation * math.sqrt(2*math.pi))) # get maximum probability  
    p =get_gauss_probability(d, mean, deviation)

    # Here we normalize the probability by its maximum value to receive a confidence value that epresses, how well the observation of the
    # current location-duration fits into our model 
    confidence = p / p_max
    #confidence = p
    return confidence                                                   

objReader = csv.DictReader(open(sys.argv[1], 'rb'), delimiter=',', quotechar='|')

#print('Calculating mean confidence:')

# counters
confidence_sum = 0
confidence_counter = 0

p = 0
confidence = 0

# mean times (1D as gaussians) for robot_table_setting
#table_mean = 2.1076
#table_dev = 1.2662
#drawer_mean = 3.1934
#drawer_dev = 1.0323
#dishwasher_mean = 1.0371
#dishwasher_dev = 0.5608

# mean times (as 1D gaussians) for human table setting
table_mean = 4.85
table_dev = 0.7167
drawer_mean = 5.58
drawer_dev = 0.8833
dishwasher_mean = 2.6167
dishwasher_dev = 0.7167

for row in objReader:
    # Write new csv-file with: instance, time, BECX, BEXY, BECTheta, 
   
    if (row['location'] == 'table'):
        p = get_gauss_probability(float(row['duration']), table_mean, table_dev)
        confidence = get_confidence(float(row['duration']), table_mean, table_dev)
        
    if (row['location'] == 'dishwasher'):
        p = get_gauss_probability(float(row['duration']), dishwasher_mean, dishwasher_dev)
        confidence = get_confidence(float(row['duration']), dishwasher_mean, dishwasher_dev)
       
    if (row['location'] == 'drawer55' or row['location'] == 'drawer115' ):
        p = get_gauss_probability(float(row['duration']), drawer_mean, drawer_dev)
        confidence = get_confidence(float(row['duration']), drawer_mean, drawer_dev)
     
    # We do not account for navigation at the moment
    #if (row['location'] == 'navigation'):
    #    p = get_gauss_probability(float(row['duration']), nav_mean, nav_dev)
    #    confidence = get_confidence(float(row['duration']), nav_mean, nav_dev)
             
    if (float(row['probability']) > 0.005):
        confidence_sum += confidence
        confidence_counter += 1
        #print("confidence: %s (p=%s, location= %s)"%(confidence, p, row['location']))
    else:
        #print("Skipping insecure value: %s"%row['probability'])
        pass

confidence_mean = confidence_sum / confidence_counter

print('[%s] Mean confidence: %s s'%(sys.argv[1], confidence_mean))

        

