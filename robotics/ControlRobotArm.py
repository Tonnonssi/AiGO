import serial 
import time
import pandas as pd

class ControlRobotArm:
    def __init__(self, 
                 initial_position=None, 
                 target_position_path='./robotics/final_positions.csv', 
                 serial_path='/dev/cu.usbserial-1110', 
                 serial_num=115200
                 ):
        
        # Target position df by coord
        self.target_positions_df = pd.read_csv(target_position_path, index_col=0)
        self.target_positions_df = self.target_positions_df.iloc[:, :4] # preprocess 

        # start position (list) : [ waist, shoulder, elbow, wrist ]
        self.start_position = self.target_positions_df.loc['start'].tolist()
        self.stay_position = self.start_position[:]
        self.stay_position[-1] = 90
        self.stay_position[-2] += 50

        # Tracking values 
        # current position (list) : [ waist, shoulder, elbow, wrist ]
        self.current_position = initial_position if initial_position is not None else self.stay_position[:]
        self.vacuum_on = False

        # Serial setting 
        self.serial = self._connect_serial(serial_path, serial_num)

        # Init movement 
        self.send_to_robot(self.current_position + [int(self.vacuum_on)])

    def _connect_serial(self, serial_path:str, serial_num:int):
        '''
        connect Arduino Serial with serial path
        '''
        ser = serial.Serial(serial_path, serial_num, timeout=None)
        print("Communication Successfully started") # 연결 확인용
        time.sleep(2)
        return ser

    def move_to_coord(self, coord:tuple):
        print("start")
        # coord 
        coord_idx = f"{coord[0]},{coord[1]}" #   ex : 3,4
        coord_absolute_angles = self.target_positions_df.loc[coord_idx].tolist()

        # 1. back to start to pick stone 
        # self.back_to_start()

        # 2. vacuum on 
        self.vacuum_on = True
        self.send_to_robot(self.current_position + [int(self.vacuum_on)])

        # update current position 
        self.current_position = coord_absolute_angles[:]
        print(f"{coord}'s angle : {self.current_position}")

        # 3. 
        self.current_position[1] -= 15
        self.current_position[2] += 15
        self.send_to_robot(self.current_position + [int(self.vacuum_on)])

        # move to coord
        self.current_position = coord_absolute_angles[:]
        self.send_to_robot(self.current_position + [int(self.vacuum_on)]) 

        # 4. vacuum off 
        self.vacuum_on = False
        self.send_to_robot(self.current_position + [int(self.vacuum_on)])

        # 5. up 
        self.current_position[1] -= 15
        self.current_position[2] += 15
        self.send_to_robot(self.current_position + [int(self.vacuum_on)])
        # 6. go back to stay position
        self.back_to_stay()


    def send_to_robot(self, angles_lst:list):
        if not isinstance(angles_lst, list):
            raise ValueError("Error: angles must be a list.")
        
        if len(angles_lst) != 5:
            raise ValueError("Error: list must have 5 elements (waist, shoulder, elbow, wrist, vacuum_on).")
        
        data_str = ' '.join(f"{int(angle)}" for angle in angles_lst)  
        self.serial.write((data_str + '\r\n').encode())  
        
        # self.serial.flush()  # 버퍼 비우기
        time.sleep(2)  # 데이터 전송 안정화
        
        # print("Sent:", data_str)  
        # self.waiting_robot()


    def back_to_start(self):
        self.send_to_robot(self.start_position + [int(self.vacuum_on)])
        self.current_position = self.start_position
        # print(f"starting point's angle : {self.current_position}")

    def back_to_stay(self):
        stay_position = [0,90,90,90]
        self.send_to_robot(stay_position + [int(self.vacuum_on)])
        self.current_position = stay_position[:]
        # print(f"stay point's angle : {self.current_position}")

    def grasp_stone(self, position=None):
        position = self.start_position if position is None else position
        self.send_to_robot(position + [int(self.vacuum_on)])
        self.vacuum_on = True
        self.send_to_robot(position + [int(self.vacuum_on)])
        
    def ungrasp_stone(self, position=None):
        position = self.start_position if position is None else position
        self.vacuum_on = False
        self.send_to_robot(position + [int(self.vacuum_on)])

    def move_by_angle(self, coord:tuple, angles:list):
        print("start")
        # coord 
        coord_idx = f"{coord[0]},{coord[1]}" #   ex : 3,4
        coord_absolute_angles = angles

        # 1. back to start to pick stone 
        # self.back_to_start()

        # 2. vacuum on 
        self.vacuum_on = True
        self.send_to_robot(self.current_position + [int(self.vacuum_on)])

        # update current position 
        self.current_position = coord_absolute_angles[:]
        print(f"{coord}'s angle : {self.current_position}")

        # 3. 
        self.current_position[1] -= 15
        self.current_position[2] += 15
        self.send_to_robot(self.current_position + [int(self.vacuum_on)])

        # move to coord
        self.current_position = coord_absolute_angles[:]
        self.send_to_robot(self.current_position + [int(self.vacuum_on)]) 

        # 4. vacuum off 
        self.vacuum_on = False
        self.send_to_robot(self.current_position + [int(self.vacuum_on)])

        # 5. up 
        self.current_position[1] -= 15
        self.current_position[2] += 15
        self.send_to_robot(self.current_position + [int(self.vacuum_on)])
        # 6. go back to stay position
        self.back_to_stay()

        

    def waiting_robot(self):
        while True:
            if self.serial.in_waiting > 0:  
                response = self.serial.readline().decode().strip()
                print(f"Arduino Response: {response}")


if __name__=="__main__":

    controller = ControlRobotArm(serial_path='/dev/cu.usbserial-110')
    coord = (3,4)
    controller.move_to_coord(coord)
    controller.move_by_angle(coord=(3,4), angles=[80,168,160,55]) # 