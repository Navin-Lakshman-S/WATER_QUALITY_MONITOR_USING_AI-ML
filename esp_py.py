import serial as s
import json as j

comp = input("please Enter the COM Port [/dev/ttyUSB0 or /dev/ttyACM0 on linux / com3 or com4 on windows]: ")
baud_rate = int(input("please Enter the Baud Rate: "))

ser = s.Serial(comp, baud_rate)

def get_data():
    line = ser.readline().decode('utf-8')
    print(line)
    try:
        while(True):
            
            line = ser.readline().decode('utf-8')

            line = dict(eval(line))
            print(line)

            if line:
                return line
            
        # print(type(line)==type(dict()))
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    res = get_data()

    print(f'got {res}')