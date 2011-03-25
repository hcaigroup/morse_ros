#include <human_aware_navigation/human_aware_navigation.h>

PLUGINLIB_DECLARE_CLASS(human_nav_plugin, HumanAwareNavigation, human_nav_plugin::HumanAwareNavigation, nav_core::BaseGlobalPlanner)

/**
 * A human-aware-navigation-plugin to replace the global planner of nav_core with a human-friendly navigation
 */

namespace human_nav_plugin{

  ros::Publisher plan_pub;
  geometry_msgs::PoseStamped humanPose = geometry_msgs::PoseStamped();
  bool pose_init = false;

// call planPath service of human_nav_node
nav_msgs::Path planPath(const geometry_msgs::PoseStamped& start, const geometry_msgs::PoseStamped& goal, const human_nav_node::HumanState* humanPosesArray, const int& numberOfHumanPoses) {
  ros::NodeHandle n;
  ros::ServiceClient client = n.serviceClient<human_nav_node::HANaviPlan>("HANaviPlan");
  human_nav_node::HANaviPlan srv;
  // Starting point
  geometry_msgs::Pose startPose = start.pose;
  // Goal point
  geometry_msgs::Pose goalPose = goal.pose;

  std::vector<human_nav_node::HumanState> humanPosesVector;
  for(int i=0; i<numberOfHumanPoses; i++) {
    humanPosesVector.push_back(humanPosesArray[i]);
    // ROS_INFO("Found human at: %f, %f", humanPosesArray[i].simpleBodyPose.position.x, humanPosesArray[i].simpleBodyPose.position.y;
  }
  srv.request.request.start = startPose;
  srv.request.request.goal = goalPose;
  srv.request.request.humans = humanPosesVector;

  if (client.call(srv))
   {
     ROS_INFO("planPath service call successful");
   }
   else
   {
     ROS_ERROR("Failed to call planPath service");
   }
   return srv.response.path;
}

// call initScene Service of human-nav-node
void changeIFace(bool showObst, bool showDist, bool showVis, bool showShadows) {
  ros::NodeHandle n;
  ros::ServiceClient client = n.serviceClient<human_nav_node::ChangeInterfaceParams>("ChangeInterfaceParams");
  //human_nav_node::Move3dInterfaceParams srv;
  human_nav_node::ChangeInterfaceParams srv;
  srv.request.params.show_nav_obstacles = showObst;
  srv.request.params.show_nav_distance_grid = showDist;
  srv.request.params.show_nav_visibility_grid = showVis;
  srv.request.params.shadows = showShadows;

  if (client.call(srv))
  {
    ROS_INFO("changeIFace service call successful");
  }
  else
  {
    ROS_ERROR("Failed to call changeIFace service");
  }
}

void changeCamPos(float xdest, float ydest, float zdest, float dist, float hrot, float vrot) {
  ros::NodeHandle n;
  ros::ServiceClient client = n.serviceClient<human_nav_node::ChangeCamPos>("ChangeCamPos");
  human_nav_node::ChangeCamPos srv;
  srv.request.xdest = xdest;
  srv.request.ydest = ydest;
  srv.request.zdest = zdest;
  srv.request.dist = dist;
  srv.request.hrot = hrot;
  srv.request.vrot = vrot;

  if (client.call(srv))
    {
      ROS_INFO("changeCamPos service call successful");
    }
    else
    {
      ROS_ERROR("Failed to call changeCamPos service");
    }
}

// callback function for human pose
void humanPoseCallback(const nav_msgs::Odometry& pose)
{
    //ROS_INFO("Found human at: [%g, %g]", pose.pose.pose.position.x, pose.pose.pose.position.y);
    humanPose.pose.position = pose.pose.pose.position;
    humanPose.pose.orientation = pose.pose.pose.orientation;
    pose_init = true;
}


//Initialise subscriber and spin until first position is received
void initSub(){
  // Subscriber for human pose
  pose_init = false;
  ros::NodeHandle n1;
  ros::Subscriber sub = n1.subscribe("/Human/GPS", 10, humanPoseCallback);
  ros::Rate r(1); // 10 hz
  while (!pose_init) {
    ros::spinOnce();
    ros::Rate r(1); // 10 hz
  }
}

//Initialise publisher for gui_path
void initPub(){
  // Gui_path publisher
  ros::NodeHandle n2;
  plan_pub = n2.advertise<nav_msgs::Path>("human_aware_plan", 1);
}

// make plan for 1 human
bool HumanAwareNavigation::makePlan(const geometry_msgs::PoseStamped& start,
                                 const geometry_msgs::PoseStamped& goal,
                                 std::vector<geometry_msgs::PoseStamped>& plan){

  ROS_INFO("[human_navigation] Getting start point (%g,%g) and goal point (%g,%g)",
               start.pose.position.x, start.pose.position.y,goal.pose.position.x, goal.pose.position.y);
  plan.clear();

  // Initialise Subscriber to get human pose
  initSub();
  // Initialise Publisher for gui_plan
  initPub();
  ROS_INFO("Found human at: [%g, %g]", humanPose.pose.position.x, humanPose.pose.position.y);
  ROS_INFO("Starting human-friendly planner...");

  human_nav_node::HumanState humanPosesArray[1];
  human_nav_node::HumanState humanPose1;
  humanPose1.simpleBodyPose.position = humanPose.pose.position;
  humanPose1.simpleBodyPose.orientation = humanPose.pose.orientation;
  humanPose1.id = "0";
  humanPose1.locked = false;
  humanPose1.moving = true;
  humanPosesArray[0] = humanPose1;

  // plan the path using human_nav_node service
  nav_msgs::Path waypoints= planPath(start, goal, humanPosesArray, 1);
  ROS_INFO("Got path with %Zu waypoints", waypoints.poses.size());

  changeIFace(false, true, false, false);
  changeCamPos(0, 0, 3, 13, -0.4, 0.8);

  nav_msgs::Path gui_path;
  gui_path.header.frame_id = "map";
  for (uint j=0; j < waypoints.poses.size(); j++) {
     // fill plan for global planner
     plan.push_back(waypoints.poses.at(j));
     // create visualisation plan for GUI
     geometry_msgs::PoseStamped waypoint_tmp = waypoints.poses.at(j);
     waypoint_tmp.header.frame_id = "map";
     waypoint_tmp.header.stamp = ros::Time::now();
     //waypoint_tmp.pose.position.x = waypoint_tmp.pose.position.x;
     //waypoint_tmp.pose.position.y = waypoint_tmp.pose.position.y;
     gui_path.poses.push_back(waypoint_tmp);
  }
  // publish visualization plan
  plan_pub.publish(gui_path);
  ros::spinOnce();

  return true;
}
};
