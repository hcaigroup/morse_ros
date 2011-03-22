#include "mhpm3d.h"
#include <display.h>
#include <mhpError.h>
#include <globalVars.h>

static int writePath2Struct(double costs, MHP_NAV_TRAJECTORY & ABS_NAV_traj);

ACTIVITY_EVENT mhp_initialize_navigation(int *report)
{
  int dimx,dimy;
  
  MHP_BTSET = hri_bt_create_bitmaps();
  
  if(MHP_BTSET==NULL){
    printf("Problem in navigation initialization.\n");
    return FAIL;
  }
  else{
    printf("MHP is set with %d humans\n",MHP_BTSET->human_no);
  }
  
  if(MHP_ENV==NULL){
    printf("Problem in navigation initialization. Environment is NULL\n");
    return FAIL;
  }
  
  dimx = (int)((MHP_ENV->box.x2 - MHP_ENV->box.x1)/grid_sampling);
  dimy = (int)((MHP_ENV->box.y2 - MHP_ENV->box.y1)/grid_sampling);
  
  if(!hri_bt_init_bitmaps(MHP_BTSET, dimx, dimy, 1, grid_sampling)){
    printf("**MHP** Can't initialize grids\n");
    /* TODO : free the BTSET */
    *report = S_mhp_NAV_NOT_INITIALIZED;
    return FAIL;
  }
  else{
    printf("**MHP** Navigation Grids succesfully initialized\n");
  }
  
  BTSET = MHP_BTSET; // BTSET is a global variable used in the visualization of Move3D

  return ETHER;
}



/*------------------------------------------------------------------------
 * UpdatePosAndFindNavTraj
 *
 * Description:
 *
 * Reports:      OK
 *              S_mhp_NAV_NOT_INITIALIZED
 *              S_mhp_NAV_START_IN_OBSTACLE
 *              S_mhp_NAV_GOAL_IN_OBSTACLE
 *              S_mhp_NAV_HUMAN_TOO_CLOSE
 *              S_mhp_NAV_NO_PATH_FOUND
 *              S_mhp_NAV_INTERNAL_ERROR
 *              S_mhp_NAV_ALREADY_REACHED
 */


// void initBitmapset(int *report) {
//   p3d_env * env;
//   int dimx,dimy;
//   int state = FALSE;

// //  BTSET = hri_bt_create_bitmapsworobots();
//   BTSET = hri_bt_create_bitmaps();
//   //    BTSET->human = MHP_GIK->human;
//   //    BTSET->human_no = MHP_GIK->human_no;
//   BTSET->robot = MHP_ROBOT;
// //  BTSET->visball = visball;
//   env = (p3d_env *) p3d_get_desc_curid(P3D_ENV);
//   dimx = (int)((env->box.x2 - env->box.x1)/SDI_F->Param.MHP_NAV_GRID_SAMPLING);
//   dimy = (int)((env->box.y2 - env->box.y1)/SDI_F->Param.MHP_NAV_GRID_SAMPLING);

//   state = hri_bt_init_bitmaps(BTSET,dimx,dimy,1, SDI_F->Param.MHP_NAV_GRID_SAMPLING);
//   if(state==FALSE){
//     printf("**MHP** Can't initialize grids\n");
//     *report = S_mhp_NAV_NOT_INITIALIZED;
//   }
// }

/* mhpUpdPosAndFindNavTrajExec  -  codel EXEC of UpdatePosAndFindNavTraj
   Returns:  EXEC END ETHER FAIL ZOMBIE */
ACTIVITY_EVENT
mhpUpdPosAndFindNavTrajExec(MHP_UPD_FINDPATH & findpath_params, MHP_NAV_TRAJECTORY &result, int *report)
{

	/*
	    * This method only wraps several calls to mhp in order to
	    * prevent 2 clients from interfering with each other.
	    * This is a workaround until MHP is able to deal with several
	    * robots, or each client can have his own MHP instance.
	    * The key idea for 2 clients is that 2 robots will use MHP,
	    * each regarding the other as a human.
	    */

	//  if(!mhp_fetch_and_update_env(report))
	//    printf("Warning: Cannot fetch the current environment\n");


	  if(MHP_BTSET == NULL){
	    printf("Not initialized, initializing MHP_BTSET!\n");
	    // TODO default init?
	    //initBitmapset(report);
	    //if (*report != OK) {
	      *report = S_mhp_NAV_NOT_INITIALIZED;
	      return *report;
	      //}
	  }

	  MHP_AGENT_POSITION addedObject;
	  addedObject.pan = 0;
	  addedObject.tilt = 0;

	   if (findpath_params.humpos1.id>=0){
	     // ignore report result in these calls, as we don't care
	//     mhpSetHumanPositionMain(&findpath_params.humpos1, report);
	     strcpy(addedObject.name.name, "HUMAN1");
	     addedObject.pos.x = findpath_params.humpos1.pos.x;
	     addedObject.pos.y = findpath_params.humpos1.pos.y;
	     addedObject.pos.th = RTOD(findpath_params.humpos1.pos.th);
	     addedObject.state = findpath_params.humpos1.state;
	     mhpPlaceAgentMain(&addedObject, report);
	     if ((*report != OK ) && (*report != S_mhp_NAV_BAD_ID)) {
	       printf("Warning: setHumanPosition 1 returned %d !\n", *report);
	     }
	     *report = OK;
	   }

	   if (findpath_params.humpos2.id>=0){
	     //     mhpSetHumanPositionMain(&findpath_params.humpos2, report);
	     strcpy(addedObject.name.name, "HUMAN2");
	     addedObject.pos.x = findpath_params.humpos2.pos.x;
	     addedObject.pos.y = findpath_params.humpos2.pos.y;
	     addedObject.pos.th = RTOD(findpath_params.humpos2.pos.th);
	     addedObject.state = findpath_params.humpos2.state;
	     mhpPlaceAgentMain(&addedObject, report);
	     if ((*report != OK ) && (*report != S_mhp_NAV_BAD_ID)) {
	       printf("Warning: setHumanPosition 2 returned %d !\n", *report);
	     }
	     *report = OK;
	   }
	   if (findpath_params.humpos3.id>=0){
	     //     mhpSetHumanPositionMain(&findpath_params.humpos3, report);
	     strcpy(addedObject.name.name, "HUMAN3");
	     addedObject.pos.x = findpath_params.humpos3.pos.x;
	     addedObject.pos.y = findpath_params.humpos3.pos.y;
	     addedObject.pos.th = RTOD(findpath_params.humpos3.pos.th);
	     addedObject.state = findpath_params.humpos3.state;
	     mhpPlaceAgentMain(&addedObject, report);
	     if ((*report != OK ) && (*report != S_mhp_NAV_BAD_ID)) {
	       printf("Warning: setHumanPosition 3 returned %d !\n", *report);
	     }
	     *report = OK;
	   }
	   if (findpath_params.humpos4.id>=0){
	     //     mhpSetHumanPositionMain(&findpath_params.humpos4, report);
	     strcpy(addedObject.name.name, "HUMAN4");
	     addedObject.pos.x = findpath_params.humpos4.pos.x;
	     addedObject.pos.y = findpath_params.humpos4.pos.y;
	     addedObject.pos.th = RTOD(findpath_params.humpos4.pos.th);
	     addedObject.state = findpath_params.humpos4.state;
	     mhpPlaceAgentMain(&addedObject, report);
	     if ((*report != OK ) && (*report != S_mhp_NAV_BAD_ID)) {
	       printf("Warning: setHumanPosition 4 returned %d !\n", *report);
	     }
	     *report = OK;
	   }
	   if (findpath_params.humpos5.id>=0){
	     //     mhpSetHumanPositionMain(&findpath_params.humpos5, report);
	     strcpy(addedObject.name.name, "HUMAN5");
	     addedObject.pos.x = findpath_params.humpos5.pos.x;
	     addedObject.pos.y = findpath_params.humpos5.pos.y;
	     addedObject.pos.th = RTOD(findpath_params.humpos5.pos.th);
	     addedObject.state = findpath_params.humpos5.state;
	     mhpPlaceAgentMain(&addedObject, report);
	     if ((*report != OK ) && (*report != S_mhp_NAV_BAD_ID)) {
	       printf("Warning: setHumanPosition 5 returned %d !\n", *report);
	     }
	     *report = OK;
	   }

	   return mhpFindNavTrajExec(findpath_params.search_definition, result, report);

	//   return ETHER;
}

/* mhpFindNavTrajExec  -  codel EXEC of FindNavTraj
   Returns:  EXEC END ETHER FAIL ZOMBIE */
ACTIVITY_EVENT
mhpFindNavTrajExec(MHP_NAV_POS &MotionCoord, MHP_NAV_TRAJECTORY &result, int *report)
{
  double x1, y1, z1, x2, y2, z2;
  double moveaway_distance, approachpoint_distance;
  double path_costs;
  //  double rx,ry,rth;
  double searchstart[3], searchgoal[3]; //x, y, az
  *report = OK;


//  if(!mhp_fetch_and_update_env(report))
//    printf("Warning: Cannot fetch the current environment\n");

  x1 = MotionCoord.startpos.x;
  y1 = MotionCoord.startpos.y;
  z1 = MotionCoord.startpos.th;

  x2 = MotionCoord.goalpos.x;
  y2 = MotionCoord.goalpos.y;
  z2 = MotionCoord.goalpos.th;

  moveaway_distance = MotionCoord.configuration;
  approachpoint_distance = MotionCoord.linelen;

  if(MHP_BTSET == NULL){
    printf("Not initialized, initializing MHP_BTSET!\n");
    // TODO default init?
    //initBitmapset(report);
    //if (*report != OK) {
    *report = S_mhp_NAV_NOT_INITIALIZED;
    return *report;
    //}
  }
  if(MHP_BTSET->robot == NULL){
    printf("Robot not initialized!\n");
    *report = S_mhp_NAV_NOT_INITIALIZED;
    return *report;
  }

  // make sure theta is between -pi and pi
  if(-M_PI > z1 )
    z1 += M_2PI;
  else if( z1 > M_PI)
    z1 -= M_2PI;

  if(-M_PI > z2 )
    z2 += M_2PI;
  else if( z2 > M_PI)
    z2 -= M_2PI;

  // set robot start position for path search
  MHP_BTSET->robot->ROBOT_POS[6]  = searchstart[0] = x1;
  MHP_BTSET->robot->ROBOT_POS[7]  = searchstart[1] = y1;
  MHP_BTSET->robot->ROBOT_POS[11] =  z1;
  searchstart[2] = 0;

  // set robot goal position for path search (set first to avoid it being shown during path calculation)
  MHP_BTSET->robot->ROBOT_GOTO[6] = searchgoal[0] = x2;
  MHP_BTSET->robot->ROBOT_GOTO[7] = searchgoal[1] = y2;
  MHP_BTSET->robot->ROBOT_GOTO[11]  = z2;
  searchgoal[2] = 0;

//  hri_bt_reset_path(MHP_BTSET);
  path_costs = hri_bt_start_search(searchstart, searchgoal, MHP_BTSET, FALSE);

  if (path_costs < 0){
    // for negative costs, the costs are an error code (surprise!)
    switch((int) path_costs){
    case HRI_PATH_SEARCH_ERROR_NAV_START_IN_OBSTACLE:
    PrintWarning(("Cannot find a path: Start position is in obstacle\n"));
    *report = S_mhp_NAV_START_IN_OBSTACLE;
    return *report;
    case HRI_PATH_SEARCH_ERROR_NAV_GOAL_IN_OBSTACLE:
    PrintWarning(("Cannot find a path: Goal position is in obstacle\n"));
    *report = S_mhp_NAV_GOAL_IN_OBSTACLE;
    return *report;
    case HRI_PATH_SEARCH_ERROR_NAV_HUMAN_TOO_CLOSE:
    PrintWarning(("Human too close to Start position\n"));
    *report = S_mhp_NAV_HUMAN_TOO_CLOSE;
    return *report;
    case HRI_PATH_SEARCH_ERROR_NAV_INTERNAL_ERROR:
    PrintWarning(("Start or goal cells do not exist\n"));
    *report = S_mhp_NAV_INTERNAL_ERROR;
    return *report;
    case HRI_PATH_SEARCH_ERROR_NAV_NAV_NO_PATH_FOUND:
    PrintWarning(("Cannot find a path\n"));
    *report = S_mhp_NAV_NO_PATH_FOUND;
    return *report;
    case HRI_PATH_SEARCH_ERROR_NAV_NAV_ALREADY_REACHED: {
      if(z2 == z1) {
        PrintWarning(("We are already there\n"));
        *report =  S_mhp_NAV_ALREADY_REACHED;

      } else {
        PrintWarning(("Only Orientation\n"));
//        MHP_BTSET->pathexist = TRUE;
//
//        /* AKIN TEST - VERY UGLY WAY OF TREATING THIS ORIENTATION THING */
//        REL_NAV_traj.header.absOrRel = PILO_RELATIVE_TRAJ;
//        REL_NAV_traj.header.maxInitAngleDev = 0.3;
//        REL_NAV_traj.header.maxInitLengthDev = 0.3;
//        REL_NAV_traj.header.segType = PILO_LINE_SEG; /*  PILO_LINE_SEG/PILO_ARC_SEG
//                                             Pilo will use arcs */
//        REL_NAV_traj.header.x0 = x1;
//        REL_NAV_traj.header.y0 = y1;
//        REL_NAV_traj.header.theta0 = z1;
//
//        REL_NAV_traj.seg[0].dL = 0;
//        REL_NAV_traj.seg[0].e = 0.5;
//        REL_NAV_traj.seg[0].dTheta = z2 - z1;
//
//        REL_NAV_traj.header.nbSegs = 1;
//        /* ------------  */
      }
      return *report;
    }
    default:
      PrintWarning(("Unexpected error code: %i\n", (int) path_costs));
      *report = S_mhp_NAV_INTERNAL_ERROR;
    } // end switch
  }

  // copy waypoints from bitmap to path array (required for write path2poster, else a waste of time and space, maybe leaking memory)
  if(!hri_bt_write_TRAJ(MHP_BTSET,MHP_BTSET->robot->joints[1])){ /** ALLOC*/
    printf("Couldn't create path structure\n");
    *report = S_mhp_NAV_INTERNAL_ERROR;
    return *report;
  }

  if(writePath2Struct(path_costs, result)==FALSE) {
    printf("Couldn't write to the poster\n");
    *report = S_mhp_NAV_INTERNAL_ERROR;
    return *report;
  }

  return *report;


}


/**
 * writes the path in MHP_BTSET->bitmap[BT_PATH] to genom poster
 *
 */
static int writePath2Struct(double costs, MHP_NAV_TRAJECTORY & ABS_NAV_traj)
{
	 hri_bitmap * bitmap;
	  int i, abs_coord, skipno, pstcoord;

	  if(MHP_BTSET == NULL || MHP_BTSET->bitmap[BT_PATH] == NULL){
	    printf("null bitmap\n");
	    return FALSE;
	  }

	  if(MHP_BTSET->path == NULL){
	    printf("Path structure not created\n");
	    return FALSE;
	  }

	  bitmap = MHP_BTSET->bitmap[BT_PATH];
	  skipno = 1;//(int)(Param.MHP_NAV_PATH_SEG_LENGTH/MHP_BTSET->pace);
	  if (skipno < 1) skipno = 1;
	  if (skipno > 1) {
	    printf("Skipping : %d waypoints\n", skipno-1 );
	  }

	  ABS_NAV_traj.cost = costs;


	  pstcoord = 0;
	  abs_coord = 0;
	  for(i=0; i<MHP_BTSET->path->length; i+=skipno) {
	    ABS_NAV_traj.xcoord[abs_coord] = MHP_BTSET->path->xcoord[i];   /* ABS trajectory Poster */
	    ABS_NAV_traj.ycoord[abs_coord] = MHP_BTSET->path->ycoord[i];   /* ABS trajectory Poster */
	    ABS_NAV_traj.theta[abs_coord]  = MHP_BTSET->path->theta[i];    /* ABS trajectory Poster */
	    //printf("Added waypoint: %i (%f,%f)\n", i, MHP_BTSET->path->xcoord[abs_coord], MHP_BTSET->path->ycoord[abs_coord]);
	    abs_coord++;                                                      /* ABS trajectory Poster */
	    if (abs_coord > MHP_NAV_MAX_TRAJ_LENTGH || abs_coord > MHPPILO_MAX_TRAJ_SEGMENTS) {
	        printf("Path length longer than allowed by MHP: %d > MAX (%d, %d)\n", MHP_BTSET->path->length, MHP_NAV_MAX_TRAJ_LENTGH, MHPPILO_MAX_TRAJ_SEGMENTS );
	//      return FALSE;
	      break;
	    }

	  }

	  if (skipno > 1 && ((MHP_BTSET->path->length -1) % skipno) > 0) {
	    // have skipped last node in path
	    if (abs_coord > MHP_NAV_MAX_TRAJ_LENTGH || abs_coord > MHPPILO_MAX_TRAJ_SEGMENTS) {
	      printf("Path length longer than allowed by MHP: %d > MAX (%d, %d)\n", MHP_BTSET->path->length, MHP_NAV_MAX_TRAJ_LENTGH, MHPPILO_MAX_TRAJ_SEGMENTS );
	      ABS_NAV_traj.xcoord[abs_coord - 1] = MHP_BTSET->path->xcoord[MHP_BTSET->path->length-1];   /* ABS trajectory Poster */
	      ABS_NAV_traj.ycoord[abs_coord -1 ] = MHP_BTSET->path->ycoord[MHP_BTSET->path->length-1];   /* ABS trajectory Poster */
	      ABS_NAV_traj.theta[abs_coord - 1]  = MHP_BTSET->path->theta[MHP_BTSET->path->length-1];    /* ABS trajectory Poster */
	      ABS_NAV_traj.no = abs_coord;
	    } else {
	      // add a last wp
	      ABS_NAV_traj.xcoord[abs_coord] = MHP_BTSET->path->xcoord[MHP_BTSET->path->length-1];   /* ABS trajectory Poster */
	      ABS_NAV_traj.ycoord[abs_coord] = MHP_BTSET->path->ycoord[MHP_BTSET->path->length-1];   /* ABS trajectory Poster */
	      ABS_NAV_traj.theta[abs_coord]  = MHP_BTSET->path->theta[MHP_BTSET->path->length-1];    /* ABS trajectory Poster */

	      ABS_NAV_traj.no = abs_coord + 1; /* ABS trajectory Poster */
	    }
	  } else {
	    ABS_NAV_traj.no = abs_coord;
	  }
	  //printf("Added waypoints no: %i\n", abs_coord + 1);


	  return TRUE;
}
