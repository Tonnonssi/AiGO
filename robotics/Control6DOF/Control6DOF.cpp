#include <Arduino.h>
#include <Wire.h>
#include "PCA9685.h" 
#include "control6DOF.h"

Control6DOF::Control6DOF(int input_pins[6]) : pwmController() { // init pwmcontroller  
    for (int i = 0; i < 6; ++i) { servo_pins[i] = input_pins[i]; } 
}

void Control6DOF::setUp() {
    Wire.begin();                // init I2C 
    pwmController.resetDevices(); // init PCA9685
    pwmController.init();         
    pwmController.setPWMFreqServo(); // PWM 주파수 설정 (50Hz)
}

/**
 * @brief Controls two speed-related parameters to ensure smooth motor operation.
 * 
 * This function manages parameters that affect the motor's speed and movement stability.
 * 
 * @param step_size Initial value is set to 1 to maintain stable movement. 
 *                  Since the *by* movement logic depends on this value, it is recommended not to modify it.
 * 
 * @param speed_delay Ensures smooth and gentle motor movements. 
 *                    Without this delay, the motor might move erratically. 
 *                    The default initial value is set to 10.
 */

void Control6DOF::setSpeed(int step_size, int speed_delay) {
    this->step_size = step_size;
    this->speed_delay = speed_delay;
}

/**
 * @brief Print current two speed-related parameters. 
*/

void Control6DOF::showSpeedParams() {
    Serial.print("Step Size: ");
    Serial.println(this->step_size);
    Serial.print("Speed Delay: ");
    Serial.println(this->speed_delay);
}

/**
 * @brief Controls a single joint to move to a specific position.
 * 
 * This function allows precise control of a specified joint by setting its position.
 * 
 * @param joint_num The index of the joint to be controlled.
 *                  
 * @param joint_position The desired position for the indexed joint, sepcified as a value between 0 and 180 degrees.            
 */

void Control6DOF::rotateSingleJointTo(int joint_num, int joint_position) {
    int current_position = this->current_positions[joint_num];
    int target_position = clamp(joint_position, 0, 180);

    unsigned long current_time = millis();
    unsigned long last_updated_times = 0;

    if (current_time - last_updated_times >= this->speed_delay) {
        last_updated_times = current_time;

        while (current_position != target_position) {
            if (current_position < target_position) {
                current_position += this->step_size;
                if (current_position > target_position) { current_position = target_position; } // bound

            } else if (current_position > target_position) {
                current_position -= this->step_size;
                if (current_position < target_position) { current_position = target_position; } // bound
            }

        int pulse_length = map(current_position, 0, 180, this->servo_min, this->servo_max);
        int joint_pin = servo_pins[joint_num];
        pwmController.setChannelPWM(joint_pin, pulse_length);
        this->current_positions[joint_num] = current_position;
        Serial.println(this->current_positions[joint_num]);
    }}}

/** 
 * @brief Controls a single joint to move incrementally by steps.
 * 
 * This function provides precise control over a specified joint by moving it 
 * in incremental(or decrement) steps. 
 * The final position is calculated as thr current position + the specified step value,
 * and it is clamped to remain within the valid range of 0 to 180 degrees. 
 * 
 * @param joint_num The index of the joint to be controlled.
 *                  
 * @param joint_step The number of steps to move the joint.
 *                   This value can range from -180 to 180 degrees.    
 */

void Control6DOF::rotateSingleJointBy(int joint_num, int joint_step) {
    int current_position = this->current_positions[joint_num];
    int target_position = current_position + joint_step;

    target_position = clamp(target_position, 0, 180); 

    rotateSingleJointTo(joint_num, target_position);
    
}

/**
 * @brief Controls multiple joints to move to specific positions.
 * 
 * This function provides precise simultaneous control over multiple joints by setting
 * each joint to its desired position. The positions are specified for a subset of joints,
 * and the remaining joints are unaffected. 
 * 
 * @param active_joints_n The number of joints to be controlled. 
 * 
 * @param joint_nums An array containing the indices of the joints to be controlled. 
 *                  
 * @param joint_positions An array containing the desired positions for each joint, 
 *                        specified as values between 0 and 180 degrees.          
 */

void Control6DOF::rotateJointsTo(int active_joints_n, int joint_nums[], int joint_positions[]) {
    for (int i=0 ; i < active_joints_n; i++){
        rotateSingleJointTo(joint_nums[i], joint_positions[i]);
    }
}

/**
 * @brief Controls multiple joints to move incrementally by steps.
 * 
 * This function allows precise and simultaneous control over multiple joints by moving 
 * them in incremental (or decremental) steps. The function calculates the new position
 * for each joint based on its current position and the specified step value, ensuring
 * all joints move together in a coordinated manner.
 * 
 * @param active_joints_n The number of joints to be controlled. 
 * 
 * @param joint_nums An array containing the indices of the joints to be controlled.
 * 
 * @param joint_steps An array containing the desired step values (increments or decrements) 
 *                    for each joint. Each step value is specified as a value between -180 
 *                    and 180 degrees. The resulting positions are clamped between 0 and 
 *                    180 degrees to ensure they remain within the valid range.
 */

void Control6DOF::rotateJointsBy(int active_joints_n, int joint_nums[], int joint_steps[]) {
    for (int i=0 ; i < active_joints_n; i++){
        rotateSingleJointBy(joint_nums[i], joint_steps[i]);
    }
}

/**
 * @brief reset entire 6 joints to init positions. 
 */

void Control6DOF::resetPosition() {
    int joints[] = {0, 1, 2, 3, 4, 5};
    rotateJointsTo(6, joints, this->init_positions);
}

int Control6DOF::clamp(int value, int min_val, int max_val) {
    return (value < min_val) ? min_val : (value > max_val) ? max_val : value;
}