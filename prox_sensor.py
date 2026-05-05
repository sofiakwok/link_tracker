import serial
import adafruit_us100

class ProximitySensor:
    def __init__(self):
        self.uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
        self.us100 = adafruit_us100.US100(self.uart)

    def get_temp(self):
        return self.us100.temperature
    
    def get_distance(self):
        # distance in cm
        return self.us100.distance
    
    def get_trigger(self):
        dist = self.us100.distance
        if dist < 15:
            return True
        return False

if __name__=="__main__":
    prox = ProximitySensor()
    while True:
        print("Temperature: ", prox.get_temp)
        print("Triggered: ", prox.get_trigger)