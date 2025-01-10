from kinematics import *
import serial 
import time

class ControlRobotArm:
    def __init__(self, 
                 initial_positions=initial_positions, 
                 target_position_path='./robotics/communication/final_positions.csv', 
                 serial_path='/dev/cu.usbserial-110', 
                 serial_num=115200
                 ):
        
        # init values 
        self.target_positions = pd.read_csv(target_position_path, index_col=0)
        self.grasping_state = {'open' : 90, 'close' : 0, 'grasp' : 30}
        self.current_position = initial_positions
        self.initial_positions = initial_positions

        # serial info 
        self.serial = self._connectSerial(serial_path, serial_num)

    def _connectSerial(self, serial_path:str, serial_num:str):
        ser = serial.Serial(serial_path, serial_num, timeout=None)
        print("Communication Successfully started") # 연결 확인용
        time.sleep(2)
        return ser

    def moveToCoord(self, coord:str):
        coord_absolute_angles = list(self.target_positions.loc[coord][3:])
        self.sendToRobot(coord_absolute_angles)

        self.current_position = coord_absolute_angles # 현재 위치 업데이트 
        print(self.current_position)

    def ungraspStone(self):
        # open gripper and let stone 
        gripper_open = self.current_position
        gripper_open[5] = self.grasping_state['open']
        self.sendToRobot(gripper_open)

        time.sleep(100)

        # close gripper 
        gripper_close = self.current_position
        gripper_close[5] = self.grasping_state['close']
        self.sendToRobot(gripper_close)

        # 현재 위치 업데이트 
        self.current_position = gripper_close 

        print(self.current_position)

    def graspStone(self):
        # open gripper
        gripper_open = self.current_position
        gripper_open[5] = self.grasping_state['open']
        self.sendToRobot(gripper_open)

        time.sleep(100)

        # grasp stone 
        gripper_close = self.current_position
        gripper_close[5] = self.grasping_state['grasp']
        self.sendToRobot(gripper_close)

        # 현재 위치 업데이트 
        self.current_position = gripper_close 
        print(self.current_position)


    def sendToRobot(self, angles:list):
        data_str = ','.join(f"{int(angle)}" for angle in angles)  # 6자리 소수점까지 변환
        self.serial.write((data_str + '\n').encode())  # 문자열로 변환 후 전송
        print("Sent:", data_str)


    def backToInit(self):
        self.sendToRobot(self.initial_positions)
        self.current_position = initial_positions


    def moveTo(self, coord:str):
        self.graspStone()
        time.sleep(100)
        self.moveToCoord(coord)
        time.sleep(100)
        self.ungraspStone()
        time.sleep(100)
        self.backToInit()


if __name__=="__main__":
    controller = ControlRobotArm()
    controller.moveToCoord('A1')
    controller.graspStone()
