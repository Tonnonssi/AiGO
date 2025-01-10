import numpy as np
import pandas as pd
from scipy.optimize import minimize

link_lengths = [7.5, 12.3, 12.7, 17.5] # ( 단위 : cm )
'''
L1 = 7.5   # Base to shoulder
L2 = 12.3  # Shoulder to elbow
L3 = 12.7  # Elbow to wrist
L4 = 17.5  # Wrist to end-effector
'''

initial_positions = np.radians([90, 90, 90, 90, 90, 0])

bounds = [(np.radians(0), np.radians(180)),   # θ1: 허리 회전
          (np.radians(0), np.radians(180)),   # θ2: 어깨
          (np.radians(0), np.radians(180)),   # θ3: 팔꿈치
          (np.radians(0), np.radians(180)),   # θ4: 손목 회전
          (np.radians(0), np.radians(180)),   # θ5: 손목 pitch
          (np.radians(0), np.radians(90))]    # θ6: 집게

# === 정방향 기구학 (Forward Kinematics) ===
def forwardKinematics(joint_angles):
    θ1, θ2, θ3, θ4, _, _ = joint_angles  # 각도 입력

    # 어깨(Shoulder) 좌표 계산
    x_shoulder = link_lengths[0] * np.cos(θ1)
    y_shoulder = link_lengths[0] * np.sin(θ1)

    # 팔꿈치(Elbow) 좌표 계산
    x_elbow = x_shoulder + link_lengths[1] * np.cos(θ2) * np.cos(θ1)
    y_elbow = y_shoulder + link_lengths[1] * np.cos(θ2) * np.sin(θ1)
    z_elbow = link_lengths[1] * np.sin(θ2)

    # 손목(Wrist) 좌표 계산
    x_wrist = x_elbow + link_lengths[2] * np.cos(θ2 + θ3) * np.cos(θ1)
    y_wrist = y_elbow + link_lengths[2] * np.cos(θ2 + θ3) * np.sin(θ1)
    z_wrist = z_elbow + link_lengths[2] * np.sin(θ2 + θ3)

    # End-Effector(집게 손) 좌표 계산
    x_end = x_wrist + link_lengths[3] * np.cos(θ2 + θ3 + θ4) * np.cos(θ1)
    y_end = y_wrist + link_lengths[3] * np.cos(θ2 + θ3 + θ4) * np.sin(θ1)
    z_end = z_wrist + link_lengths[3] * np.sin(θ2 + θ3 + θ4)

    return np.array([x_end, y_end, z_end])


# === 역기구학 (Inverse Kinematics) ===
def inverseKinematics(target_position):
    def objectiveFunction(joint_angles):
        "목표 좌표와 현재 FK 결과의 차이를 최소화"
        current_position = forwardKinematics(joint_angles)
        return np.linalg.norm(current_position - target_position)

    result = minimize(objectiveFunction, initial_positions, method='L-BFGS-B', bounds=bounds)

    if result.success:
        return np.round(np.degrees(result.x), 1)  # 결과를 degree로 변환
    
    # else: -> None 


if __name__=="__main__":
    target_position = np.array([-20, 10, 15])
    angles = inverseKinematics(target_position)
    print("각 관절의 최적 회전각 (Degrees):", list(angles))