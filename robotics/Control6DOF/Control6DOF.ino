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
  int target_pin[] = {0 ,1, 2, 3, 4, 5};
  int pin_movement[] = {20, 40, 50,20, 40, 50};
  int pin_movement_2[] = {20, -30, 30,20, -30, 30};

  controller.rotateJointsTo(6, target_pin, pin_movement);
  delay(1000);
  controller.rotateJointsBy(6, target_pin, pin_movement_2);
  }
