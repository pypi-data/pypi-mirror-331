# from .motors import MotorController
# from .exceptions import MABUException

import serial

class mabu:
    """Main class for controlling the MABU robotic head"""
    
    def __init__(self, port="/dev/ttyUSB0"):
        self.is_powered = False
        self.port = port
        self.ser = serial.Serial(self.port, 57600, timeout=1) 
        
    def on(self):
        """Turn on the MABU robot"""
        try:
            # Construct the command fa 00 02 4f 7f 0b cb
            command = bytearray([0xfa, 0x00, 0x02, 0x4f, 0x7f, 0x0b, 0xcb])
            # Send the command
            self.ser.write(command)
            
            #TODO check answer
            
            self.is_powered = True
            print("MABU is powered on")
        except Exception as e:
            pass
            # raise MABUException(f"Failed to power on: {str(e)}")
            
    def off(self):
        """Turn off the MABU robot"""
        try:
            # Construct the command fa 00 02 4f 8b 4c
            command = bytearray([0xfa, 0x00, 0x02, 0x4f, 0x8b, 0x4c])
            # Send the command
            self.ser.write(command)
            
            #TODO check answer
            
            self.is_powered = False
            print("MABU is powered on")
        except Exception as e:
            pass
            # raise MABUException(f"Failed to power on: {str(e)}")
    
    def fletcher8(self,data):
        sum1 = 0
        sum2 = 0
        for byte in data:
            sum1 = (sum1 + byte) % 255
            sum2 = (sum2 + sum1) % 255
        return (sum2 << 8) | sum1
    
    def move_robot_part(self, part, value):
        # Map parts to their respective command codes
        part_codes = {
            'LDL': 0x40,
            'LDR': 0x20,
            'ELR': 0x10,
            'EUD': 0x08,
            'NE': 0x04,
            'NR': 0x02,
            'NT': 0x01
        }

        if part not in part_codes:
            raise ValueError("Invalid part specified")

        # Map 0-100 to 0-255
        mapped_value = int(value * 2.55)

        # Construct the command
        command = bytearray([0xfa, 0x00, 0x04, 0x01, part_codes[part], 0x01, mapped_value])

        # Calculate checksum usign fletcher8 algorithm
        checksum = self.fletcher8(command)
        command.append(checksum >> 8)
        command.append(checksum & 0xff)

        # Send the command
        self.ser.write(command)
        #time.sleep(0.1)  # Small delay to ensure command is processed
    
    def move_all_parts(self, ldl, ldr, elr, eud, ne, nr, nt):
        self.move_robot_part('LDL', ldl)
        self.move_robot_part('LDR', ldr)
        self.move_robot_part('ELR', elr)
        self.move_robot_part('EUD', eud)
        self.move_robot_part('NE', ne)
        self.move_robot_part('NR', nr)
        self.move_robot_part('NT', nt)
        
    def center_all(self):
        self.move_all_parts(50, 50, 50, 50, 50, 50, 50)
    
    
    # def move_head(self, angle_x=0, angle_y=0):
    #     """Move the robot head to specified angles"""
    #     if not self.is_powered:
    #         raise MABUException("MABU is not powered on")
        
    #     self.motor_controller.move_head(angle_x, angle_y)
        
    # def move_eyes(self, left_angle=0, right_angle=0):
    #     """Move the robot eyes to specified angles"""
    #     if not self.is_powered:
    #         raise MABUException("MABU is not powered on")
            
    #     self.motor_controller.move_eyes(left_angle, right_angle)
        
    # def reset_position(self):
    #     """Reset all motors to their default position"""
    #     if not self.is_powered:
    #         raise MABUException("MABU is not powered on")
            
    #     self.motor_controller.reset_all()
    
    