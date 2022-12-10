from serial_handler import Serial
from state_machine import StateMachine


class Main:
    def __init__(self):
        self.sh = Serial()
        self.sm = StateMachine()
        
    def init_state_machine(self):
        self.sm.add_state("init_state", self.sm.start_transition)
        self.sm.add_state("userdata_state", self.sm.userdata_transition)
        self.sm.add_state("height_state", self.sm.height_transition)
        self.sm.add_state("temp_state", self.sm.temp_transition)
        self.sm.add_state("oxy_state", self.sm.oxy_transition)
        self.sm.add_state("heart_state", self.sm.heart_transition)
        self.sm.add_state("fingerprint_state", self.sm.fingerprint_transition)
        self.sm.add_state("final_state", None, end_state=1)
        self.sm.set_start_state("init_state")
    
    def start(self):
        self.sm.run()


if __name__ == '__main__':
    main = Main()
    main.start()