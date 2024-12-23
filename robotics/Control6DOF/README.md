## Develop Language 
![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white)  

## Information
**Creator** : Jimin Lee  
**Date** : 2024-12-23  
**Version** : 0.1.0  

## Dependency
> 1 Library is needed.  

1. PCA9685.h

## Structure
```
Control6DOF 
 - Control6DOF.h
 - Control6DOF.cpp
 - controller
   - controller.ino
```

## Key Methods 
> Refer to **the header and cpp files** for further instructions.  
```cpp 
void Control6DOF::rotateJointsBy(int active_joints_n, int joint_nums[], int joint_steps[])
````
```cpp 
void Control6DOF::rotateJointsBy(int active_joints_n, int joint_nums[], int joint_steps[])
````


## Example 
```cpp
#include "Control6DOF.h"

// init pins 
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
  int pin_movement_1[] = {70};
  int pin_movement_2[] = {-30};

  controller.rotateJointsTo(1, target_pin, pin_movement_1); // pin 3 linked motor rotates to 70
  delay(1000);
  controller.rotateJointsBy(1, target_pin, pin_movement_2); // pin 3 linked motor rotates to 40
  }
```
