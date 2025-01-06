#include <Arduino.h>
#include <Wire.h>
#include <PCA9685.h>

// File: Control6DOF.h
// Author: Jimin Lee(Tonnonssi)
// Date: 2024-12-23
// Description: This library controls 6 servo motors by using pca9685 servo motor driver.

#ifndef CONTROL6DOF_H
#define CONTROL6DOF_H

class Control6DOF {
private:
    PCA9685 pwmController;

    // params for control speed 
    int step_size = 1; 
    int speed_delay = 10; 

    // 6 motors position, update time info
    int current_positions[6] = {0, 0, 0, 0, 0, 0};
    int init_positions[6] = {0, 0, 0, 0, 0, 0};
    unsigned long last_updated_times[6] = {0, 0, 0, 0, 0, 0};

    // servo pulses
    const int servo_min = 102; // 최소 펄스 (0도)
    const int servo_max = 512; // 최대 펄스 (180도)

    // single movement
    void rotateSingleJointTo(int joint_num, int joint_position);
    void rotateSingleJointBy(int joint_num, int joint_step);

    int clamp(int value, int min_val, int max_val); // keep in range 

public:
    Control6DOF(int input_pins[6]);

    int servo_pins[6]; // 6DOF servo motors' pins

    void setUp(); // init setting for pca9685.
    
    // speed related methods 
    void setSpeed(int step_size, int speed_delay); 
    void showSpeedParams();

    // joint related key methods
    void rotateJointsTo(int active_joints_n, int joint_nums[], int joint_positions[]); // move multiple joints to specific degrees : range(0-180)
    void rotateJointsBy(int active_joints_n, int joint_nums[], int joint_steps[]); // move multiple joints by specific degress : step can be either + or -

    void resetPosition(); // reset position to init_position. 

};

#endif