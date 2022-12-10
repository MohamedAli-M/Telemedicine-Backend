import serial
import time
import sys
import ast 

class Serial:
    def __init__(self):
        try:
            self.reader = serial.Serial(port='/dev/cu.usbserial-2140', baudrate=115200, timeout=.1)
            return 
        except:
            print("No serial port detected. Trying again ..")
            try: 
                self.reader = serial.Serial('/dev/tty0', 115200)
            except:
                print("No serial port detected. Please ensure connection and try again. \n")
                # ADD THIS LATER ON 
                # sys.exit(1)
                
    def read_serial(self) -> str:
        data = self.reader.readline()
        str_data = str(data, 'utf-8')
        if str_data != "":
            return ast.literal_eval(str_data)
        else:
            return ""
    
    def decode_data(self, data) -> list:
        str_data = str(data, 'utf-8')
        if(type(str_data) == dict):
            dict_data = ast.literal_eval(str_data)
        else:
            dict_data = {}
        return dict_data




