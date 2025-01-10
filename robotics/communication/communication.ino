#include "Control6DOF.h"

// 핀 초기화
int pins[6] = {0, 3, 4, 7, 8, 11};
Control6DOF controller(pins); 

void setup() {
    controller.setUp();
    Serial.begin(115200); // 시리얼 통신 시작
    Serial.println("Setup complete");
} 

void loop() {
    if (Serial.available()) {
        int absolute_angles[6];
        for (int i = 0; i < 6; i++) {
            values[i] = Serial.parseInt(); // 각도 데이터 읽기 
        }
        
        Serial.println("Received: ");
        for (int i = 0; i < 6; i++) {
            Serial.println(absolute_angles[i], 6); // 소수점 6자리 출력
            Serial.println(" ");
        }

        int target_pin[] = {0 ,1, 2, 3, 4, 5};
        controller.rotateJointsTo(6, target_pin, absolute_angles);
    }
}
