#include "Control6DOF.h"

// 핀 초기화
int pins[6] = {0, 3, 4, 7, 8, 11};
Control6DOF controller(pins); 

void setup() {
   controller.setUp();
   Serial.begin(9600);
   Serial.println("Serial test");
} 

void loop() {
  delay(1000);
  int target_pin[] = {2};
//  int pin_movement[] = {90, 90, 90, 90, 90, 90};
//  int pin_movement_2[] = {0, 0, 0, 0, 0, 0};
  int pin_movement[] = {0};
//  int pin_movement_2[] = {180};


  controller.rotateJointsTo(1, target_pin, pin_movement);
  delay(1000);
//  controller.rotateJointsTo(1, target_pin, pin_movement_2);
  
//  controller.rotateJointsTo(6, target_pin, pin_movement);
//  delay(1000);
//  controller.rotateJointsTo(6, target_pin, pin_movement_2);
//  controller.rotateJointsBy(6, target_pin, pin_movement_2);
  }
