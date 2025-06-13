from machine import Pin
import time

# 5-Way Digital Navigation Joystick Pin Configuration (from README)
# COM pin is connected to GND. All pins are active low with internal pull-up.
joystick_pins = {
    'UP': Pin(18, Pin.IN, Pin.PULL_UP),
    'DOWN': Pin(19, Pin.IN, Pin.PULL_UP),
    'LEFT': Pin(4, Pin.IN, Pin.PULL_UP),
    'RIGHT': Pin(5, Pin.IN, Pin.PULL_UP),
    'MID': Pin(6, Pin.IN, Pin.PULL_UP),
    'SET': Pin(17, Pin.IN, Pin.PULL_UP),
    'RST': Pin(22, Pin.IN, Pin.PULL_UP),
}

def get_joystick_states():
    """Read the state of all joystick buttons."""
    states = {}
    for name, pin in joystick_pins.items():
        # Pins are active low, so not pin.value() is True when pressed.
        states[name] = not pin.value()
    return states

def get_direction_string(states):
    """Convert joystick states to a direction string."""
    directions = []
    
    if states['UP']:
        directions.append("UP")
    if states['DOWN']:
        directions.append("DOWN")
    if states['LEFT']:
        directions.append("LEFT")
    if states['RIGHT']:
        directions.append("RIGHT")
        
    if not directions:
        return "CENTER"
        
    return "+".join(directions)

def test_joystick_basic():
    """Basic joystick reading test."""
    print("\n=== 5-Way Digital Joystick Test ===")
    print("Press any direction or button on the joystick.")
    print("Press Ctrl+C to stop.")
    print("\nDirection | MID | SET | RST")
    print("---------------------------------")
    
    try:
        while True:
            states = get_joystick_states()
            
            direction = get_direction_string(states)
            
            mid_state = "PRESSED" if states['MID'] else "       "
            set_state = "PRESSED" if states['SET'] else "       "
            rst_state = "PRESSED" if states['RST'] else "       "
            
            print(f"{direction:<9} | {mid_state} | {set_state} | {rst_state}", end='\r')
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped.")

if __name__ == "__main__":
    print("Initializing 5-Way Digital Joystick Test...")
    test_joystick_basic() 