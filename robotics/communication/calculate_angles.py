import string
import numpy as np
from kinematics import *

x_start, y_start = -9, 26  # initial value 

def createCoordMatrix():
    # values to make 
    x_values = np.linspace(x_start, x_start + 16, 9, dtype=int)  # 2++
    y_values = np.linspace(y_start, y_start - 16, 9, dtype=int)  # 2--

    # make coord array (shape : (9,9,3))
    coord_arr = np.array([[(x, y, 5) for x in x_values] for y in y_values], dtype=object)
    return coord_arr


def calFinalPositions(coord_arr):
    def labelIndex(i,j):
        uppercase_alphabet = string.ascii_uppercase
        label = uppercase_alphabet[i] + f'{j}'
        return label
    
    # final_positions dataframe 
    final_positions = pd.DataFrame(columns=['x', 'y', 'z', 'θ1', 'θ2', 'θ3', 'θ4', 'θ5', 'θ6'])
    final_positions.index.name = 'coord'

    indices = []
    num_none = 0

    for i in range(9):
        for j in range(9):
            target_position = coord_arr[i, j]

            # 인덱스 추가 
            label = labelIndex(i,j)
            indices.append(label)

            print(f"목표 좌표: {label}__{target_position}")
            angles = inverseKinematics(target_position)
            
            # 각도 저장 
            if angles is not None:
                final_positions.loc[9*i+j] = np.concatenate([np.array(target_position), np.round(angles)]) 
                print("각 관절의 최적 회전각 (Degrees):", angles)
            
            else:
                final_positions.loc[9*i+j] = np.concatenate([np.array(target_position), np.zeros(6)])
                print("계산에 실패했습니다.(return None)")
                num_none += 1

            print()

    # relabel
    final_positions.index = indices
    print(f"계산하지 못한 각도 개수 : {num_none}")

    return final_positions

if __name__=="__main__":
    coord_arr = createCoordMatrix()
    final_positions = calFinalPositions(coord_arr)
    final_positions.to_csv('./robotics/communication/final_positions.csv')

