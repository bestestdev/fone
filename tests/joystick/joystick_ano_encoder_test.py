from machine import Pin
import time

# ANO Directional Navigation and Scroll Wheel Rotary Encoder Pin Configuration
# COM pin is connected to GND. All pins are active low with internal pull-up.
encoder_pins = {
    'ENCA': Pin(17, Pin.IN, Pin.PULL_UP),   # Rotary encoder A pin
    'ENCB': Pin(22, Pin.IN, Pin.PULL_UP),   # Rotary encoder B pin
    'SW1': Pin(6, Pin.IN, Pin.PULL_UP),     # Center button
    'SW2': Pin(5, Pin.IN, Pin.PULL_UP),     # Down button
    'SW3': Pin(4, Pin.IN, Pin.PULL_UP),     # Right button  
    'SW4': Pin(19, Pin.IN, Pin.PULL_UP),    # Up button
    'SW5': Pin(18, Pin.IN, Pin.PULL_UP),    # Left button
}

# Rotary encoder state tracking
encoder_state = {
    'last_a': 1,
    'last_b': 1,
    'position': 0
}

def read_encoder():
    """Read rotary encoder and update position"""
    current_a = encoder_pins['ENCA'].value()
    current_b = encoder_pins['ENCB'].value()
    
    # Check for state changes on encoder A pin
    if encoder_state['last_a'] != current_a:
        if current_a == 0:  # Falling edge on A
            if current_b == 0:
                encoder_state['position'] += 1  # Clockwise
            else:
                encoder_state['position'] -= 1  # Counter-clockwise
    
    encoder_state['last_a'] = current_a
    encoder_state['last_b'] = current_b
    
    return encoder_state['position']

def get_button_states():
    """Read the state of all encoder buttons."""
    states = {}
    for name, pin in encoder_pins.items():
        if name.startswith('SW'):
            # Pins are active low, so not pin.value() is True when pressed
            states[name] = not pin.value()
    return states

def get_direction_string(states):
    """Convert button states to a direction string."""
    directions = []
    
    if states['SW4']:  # Up
        directions.append("UP")
    if states['SW2']:  # Down
        directions.append("DOWN")
    if states['SW5']:  # Left
        directions.append("LEFT")
    if states['SW3']:  # Right
        directions.append("RIGHT")
        
    if not directions:
        return "CENTER"
        
    return "+".join(directions)

def test_encoder_basic():
    """Basic encoder and button test."""
    print("\n=== ANO Encoder and Button Test ===")
    print("Rotate encoder wheel and press buttons.")
    print("Press Ctrl+C to stop.")
    print("\nEncoder | Direction | Center | Status")
    print("--------------------------------------")
    
    try:
        while True:
            # Read encoder position
            position = read_encoder()
            
            # Read button states
            states = get_button_states()
            direction = get_direction_string(states)
            
            center_state = "PRESSED" if states['SW1'] else "       "
            
            # Show any pressed directional buttons
            pressed_buttons = []
            if states['SW2']: pressed_buttons.append("DOWN")
            if states['SW3']: pressed_buttons.append("RIGHT") 
            if states['SW4']: pressed_buttons.append("UP")
            if states['SW5']: pressed_buttons.append("LEFT")
            
            status = "+".join(pressed_buttons) if pressed_buttons else ""
            
            print(f"{position:7d} | {direction:<9} | {center_state} | {status:<12}", end='\r')
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped.")

def test_encoder_only():
    """Test only the rotary encoder functionality."""
    print("\n=== Rotary Encoder Only Test ===")
    print("Rotate the encoder wheel.")
    print("Press Ctrl+C to stop.")
    print("\nPosition | Direction | Delta")
    print("---------------------------")
    
    last_position = encoder_state['position']
    
    try:
        while True:
            position = read_encoder()
            delta = position - last_position
            
            if delta != 0:
                direction = "CW" if delta > 0 else "CCW"
                print(f"{position:8d} | {direction:<9} | {delta:+4d}")
                last_position = position
            
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped.")

def test_buttons_only():
    """Test only the directional buttons."""
    print("\n=== Button Only Test ===")
    print("Press directional and center buttons.")
    print("Press Ctrl+C to stop.")
    print("\nSW1(Center) | SW2(Down) | SW3(Right) | SW4(Up) | SW5(Left)")
    print("-----------------------------------------------------------")
    
    try:
        while True:
            states = get_button_states()
            
            sw1_state = "PRESSED" if states['SW1'] else "       "
            sw2_state = "PRESSED" if states['SW2'] else "       "
            sw3_state = "PRESSED" if states['SW3'] else "       "
            sw4_state = "PRESSED" if states['SW4'] else "       "
            sw5_state = "PRESSED" if states['SW5'] else "       "
            
            print(f"{sw1_state:11} | {sw2_state:9} | {sw3_state:10} | {sw4_state:7} | {sw5_state:8}", end='\r')
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped.")

def run_comprehensive_test():
    """Run all ANO encoder tests"""
    print("=== ANO Directional Navigation and Scroll Wheel Test ===")
    print("Testing rotary encoder with directional navigation buttons")
    print()
    
    while True:
        print("\n=== Test Menu ===")
        print("1. Basic encoder and button test")
        print("2. Rotary encoder only test")
        print("3. Buttons only test")
        print("4. Exit")
        
        try:
            choice = input("Select test (1-4): ").strip()
            
            if choice == '1':
                test_encoder_basic()
            elif choice == '2':
                test_encoder_only()
            elif choice == '3':
                test_buttons_only()
            elif choice == '4':
                print("Exiting ANO encoder test.")
                break
            else:
                print("Invalid choice. Please select 1-4.")
                
        except KeyboardInterrupt:
            print("\nTest interrupted.")
            break

if __name__ == "__main__":
    print("Initializing ANO Encoder Test...")
    run_comprehensive_test()