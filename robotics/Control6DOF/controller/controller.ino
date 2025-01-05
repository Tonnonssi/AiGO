#include "../Control6DOF.h"

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
  int target_pin[] = {3};
  int pin_movement[] = {70};
  int pin_movement_2[] = {-30};

  controller.rotateJointsTo(1, target_pin, pin_movement);
  delay(1000);
  controller.rotateJointsBy(1, target_pin, pin_movement_2);
  }
