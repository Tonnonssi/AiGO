#include "Control6DOF.h"

int pins[6] = {0, 3, 4, 7, 8, 11};
Control6DOF controller(pins);

void convertLongToInt(long longArray[], int intArray[], int size) {
    for (int i = 0; i < size; i++) {
        intArray[i] = (int) longArray[i]; 
    }
}

void setup() {
    controller.setUp();
    Serial.begin(115200);
    // Serial.println("Setup complete");
}

void loop() {
    if (Serial.available()) {
        // 문자열 읽기
        String data = Serial.readStringUntil('\n');  // 개행 문자까지 읽음

        // 문자열을 공백(' ') 기준으로 분할하여 배열로 변환
        int absolute_angles[6];
        int index = 0;
        char *ptr = strtok((char *)data.c_str(), " "); // 공백 기준으로 자름
        while (ptr != NULL && index < 6) {
            absolute_angles[index++] = atoi(ptr);  // 문자열을 정수로 변환
            ptr = strtok(NULL, " ");
        }

        // 데이터 확인용 출력
//        Serial.println("Received:");
        for (int i = 0; i < 6; i++) {
            Serial.print(absolute_angles[i]);
            Serial.print(" .");
        }
        Serial.println();

        // 모터 제어
        int target_pin[] = {0, 1, 2, 3, 4, 5};
        controller.rotateJointsTo(6, target_pin, absolute_angles);
    }
}
