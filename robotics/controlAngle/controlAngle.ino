#include <Servo.h>

Servo air_pump;
Servo solenoid_valve;

Servo waist;
Servo shoulder;
Servo elbow;
Servo wrist;

// 각 서보의 현재 각도 저장 변수
int waist_angle = 14;
int shoulder_angle = 104;
int elbow_angle = 48;
int wrist_angle = 17;

void setup() {
    Serial.begin(9600); // 시리얼 통신 시작
    
    // suction
    solenoid_valve.attach(2);
    air_pump.attach(3);

    // robot arm
    waist.attach(4);
    shoulder.attach(5);
    elbow.attach(6);
    wrist.attach(7);

    initializeSystem();
}

void initializeSystem() {
    // vacuum
    air_pump.write(0);
    solenoid_valve.write(180);
    
    // robot arm 초기화
    waist.write(waist_angle);
    shoulder.write(shoulder_angle);
    elbow.write(elbow_angle);
    wrist.write(wrist_angle);
    delay(1000);

    Serial.println("System Initialized");
}

void loop() {
    if (Serial.available() > 0) {
        char command = Serial.read();
        
        if (command == '1') {
            increaseWaist();
        } else if(command == '2') {
            increaseShoulder();
        } else if(command == '3') {
            increaseElbow();
        } else if (command == '4') {
            increaseWrist();
        } else if (command == '5') {
            decreaseWaist();
        } else if (command == '6') {
            decreaseShoulder();
        } else if (command == '7') {
            decreaseElbow();
        } else if (command == '8') {
            decreaseWrist();
        } else if (command == '9') {
            activateSuction();
        } else if (command == '0') {
            releaseSuction();
            turnOffPump();
        } else if (command == 'i') {  
            printServoAngles();
        } else if(command == 's') {
            backToStart();
        } else if(command == 'x') {
            setCustomAngles();
        }
    }
}

// 현재 서보 모터 각도를 출력하는 함수
void printServoAngles() {
    Serial.println("---- Current Servo Angles ----");
    Serial.print("Waist: "); Serial.println(waist_angle);
    Serial.print("Shoulder: "); Serial.println(shoulder_angle);
    Serial.print("Elbow: "); Serial.println(elbow_angle);
    Serial.print("Wrist: "); Serial.println(wrist_angle);
    Serial.println("-----------------------------");
}

void backToStart() {
  waist_angle = 14;
  shoulder_angle = 104;
  elbow_angle = 48;
  wrist_angle = 17;

  initializeSystem();
}

// 사용자 지정 각도 입력 (x 입력 시 동작)
void setCustomAngles() {
    Serial.println("Enter angles for Waist, Shoulder, Elbow, Wrist (separated by space or newline):");

    while (Serial.available() == 0); // 대기
    waist_angle = Serial.parseInt();
    while (Serial.available() == 0);
    shoulder_angle = Serial.parseInt();
    while (Serial.available() == 0);
    elbow_angle = Serial.parseInt();
    while (Serial.available() == 0);
    wrist_angle = Serial.parseInt();

    // 버퍼 비우기 (추가적인 개행 문자나 공백 제거)
    while (Serial.available() > 0) {
        Serial.read();
    }

    // 유효 범위 검사
    if (waist_angle < 0 || waist_angle > 180 ||
        shoulder_angle < 0 || shoulder_angle > 180 ||
        elbow_angle < 0 || elbow_angle > 180 ||
        wrist_angle < 0 || wrist_angle > 180) {
        Serial.println("Invalid angles! Please enter values between 0 and 180.");
        return;
    }

    // 서보 모터 이동
    waist.write(waist_angle);
    shoulder.write(shoulder_angle);
    elbow.write(elbow_angle);
    wrist.write(wrist_angle);

    Serial.println("Updated Servo Angles:");
    printServoAngles();
}

// waist 
void increaseWaist() {
  if (waist_angle < 180) waist_angle++;
  waist.write(waist_angle);
  Serial.print("Waist: "); Serial.println(waist_angle); 
  delay(1000);
}

void decreaseWaist() {
  if (waist_angle > 0) waist_angle--;
  waist.write(waist_angle);
  Serial.print("Waist: "); Serial.println(waist_angle); 
  delay(1000);
}

// shoulder
void increaseShoulder() {
  if (shoulder_angle < 180) shoulder_angle++;
  shoulder.write(shoulder_angle);
  Serial.print("Shoulder: "); Serial.println(shoulder_angle); 
  delay(1000);
}

void decreaseShoulder() {
  if (shoulder_angle > 0) shoulder_angle--;
  shoulder.write(shoulder_angle);
  Serial.print("Shoulder: "); Serial.println(shoulder_angle); 
  delay(1000);
}

// elbow 
void increaseElbow() {
  if (elbow_angle < 180) elbow_angle++;
  elbow.write(elbow_angle);
  Serial.print("Elbow: "); Serial.println(elbow_angle); 
  delay(1000);
}

void decreaseElbow() {
  if (elbow_angle > 0) elbow_angle--;
  elbow.write(elbow_angle);
  Serial.print("Elbow: "); Serial.println(elbow_angle); 
  delay(1000);
}

// Wrist
void increaseWrist() {
  if (wrist_angle < 180) wrist_angle++;
  wrist.write(wrist_angle);
  Serial.print("Wrist: "); Serial.println(wrist_angle); 
  delay(1000);
}

void decreaseWrist() {
  if (wrist_angle > 0) wrist_angle--;
  wrist.write(wrist_angle);
  Serial.print("Wrist: "); Serial.println(wrist_angle);
  delay(1000);
}

// vacuum
void activateSuction() {
    air_pump.write(180); // Air pump on
    solenoid_valve.write(0);   // Solenoid valve closed (vacuum created)
    delay(3000);
}

void releaseSuction() {
    solenoid_valve.write(180); // Solenoid valve open (air escapes, vacuum released)
    delay(1000);
}

void turnOffPump() {
    air_pump.write(0); // Air pump off
    delay(2000);
}
