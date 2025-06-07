from machine import Pin, I2C
import time
import struct

# ADS1115 I2C Configuration
ADS1115_ADDR = 0x48  # Default address (ADDR pin to GND)
I2C_SCL = Pin(21)    # I2C0 SCL
I2C_SDA = Pin(20)    # I2C0 SDA

# ADS1115 Registers
ADS1115_REG_CONVERSION = 0x00
ADS1115_REG_CONFIG = 0x01

# ADS1115 Configuration bits
ADS1115_MUX_AIN0 = 0x4000  # Channel 0 (left X)
ADS1115_MUX_AIN1 = 0x5000  # Channel 1 (left Y) 
ADS1115_MUX_AIN2 = 0x6000  # Channel 2 (right X)
ADS1115_MUX_AIN3 = 0x7000  # Channel 3 (right Y)

# Use ±6.144V range to handle 5V joystick operation (0-5V maps to full ADC range)
ADS1115_PGA_6_144V = 0x0000  # +/-6.144V range (required for 5V joysticks)
ADS1115_MODE_SINGLE = 0x0100  # Single-shot mode
ADS1115_DR_128SPS = 0x0080   # 128 samples per second
ADS1115_COMP_QUE_DISABLE = 0x0003  # Disable comparator

# Initialize I2C
i2c = I2C(0, scl=I2C_SCL, sda=I2C_SDA, freq=400000)

# Joystick switch pins (active low)
left_sw = Pin(25, Pin.IN, Pin.PULL_UP)    # Left joystick switch
right_sw = Pin(24, Pin.IN, Pin.PULL_UP)   # Right joystick switch

# Calibration values based on actual centered readings
calibration = {
    'left_x_center': 53683,  # Raw center from measurement
    'left_y_center': 53557,  # Raw center from measurement  
    'right_x_center': 53581, # Raw center from measurement
    'right_y_center': 53742, # Raw center from measurement
    'deadzone': 1200  # Adjusted for actual range of ~32,759
}

def write_ads1115_config(channel_mux):
    """Write configuration to ADS1115 for specified channel"""
    config = (ADS1115_MUX_AIN0 if channel_mux == 0 else
              ADS1115_MUX_AIN1 if channel_mux == 1 else  
              ADS1115_MUX_AIN2 if channel_mux == 2 else
              ADS1115_MUX_AIN3) | \
             ADS1115_PGA_6_144V | \
             ADS1115_MODE_SINGLE | \
             ADS1115_DR_128SPS | \
             ADS1115_COMP_QUE_DISABLE | \
             0x8000  # Start single conversion
    
    config_bytes = struct.pack('>H', config)
    i2c.writeto_mem(ADS1115_ADDR, ADS1115_REG_CONFIG, config_bytes)

def read_ads1115_channel(channel):
    """Read ADC value from specified ADS1115 channel (0-3)"""
    try:
        # Configure for the specified channel
        write_ads1115_config(channel)
        
        # Wait for conversion (minimum time for 128 SPS)
        time.sleep(0.01)
        
        # Read conversion result
        data = i2c.readfrom_mem(ADS1115_ADDR, ADS1115_REG_CONVERSION, 2)
        raw_adc = struct.unpack('>h', data)[0]  # Signed 16-bit
        
        # Convert to positive range for easier handling
        # ADS1115 at ±4.096V gives -32768 to +32767
        # 3.3V joysticks: ~0.8V = -20000, 1.65V = ~10000, 3.3V = +32767
        # Convert to 0-65535 range: add 32768
        return raw_adc + 32768
        
    except Exception as e:
        print(f"Error reading ADS1115 channel {channel}: {e}")
        return 32768  # Return center value on error

def get_joystick_values():
    """Read all joystick values from ADS1115"""
    # Read all 4 analog channels
    left_x_raw = read_ads1115_channel(0)    # AIN0
    left_y_raw = read_ads1115_channel(1)    # AIN1  
    right_x_raw = read_ads1115_channel(2)   # AIN2
    right_y_raw = read_ads1115_channel(3)   # AIN3
    
    # Invert left joystick axes since it's mounted upside down
    # Use actual range (32777 + 65535) for proper inversion
    left_x_inverted = (32777 + 65535) - left_x_raw  # Left/Right swapped
    left_y_inverted = (32777 + 65535) - left_y_raw  # Up/Down swapped
    
    # Center the values around 0 (range: -32768 to +32767)
    left_x = left_x_inverted - calibration['left_x_center']
    left_y = left_y_inverted - calibration['left_y_center']
    right_x = right_x_raw - calibration['right_x_center']
    right_y = right_y_raw - calibration['right_y_center']
    
    # Apply deadzone
    def apply_deadzone(value, deadzone):
        if abs(value) < deadzone:
            return 0
        return value
    
    left_x = apply_deadzone(left_x, calibration['deadzone'])
    left_y = apply_deadzone(-left_y, calibration['deadzone'])  # Invert Y for correct up/down
    right_x = apply_deadzone(right_x, calibration['deadzone'])
    right_y = apply_deadzone(-right_y, calibration['deadzone'])  # Invert Y for correct up/down
    
    # Read switch states (active low)
    left_pressed = not left_sw.value()
    right_pressed = not right_sw.value()
    
    return {
        'left': {'x': left_x, 'y': left_y, 'pressed': left_pressed, 'raw_x': left_x_raw, 'raw_y': left_y_raw},
        'right': {'x': right_x, 'y': right_y, 'pressed': right_pressed, 'raw_x': right_x_raw, 'raw_y': right_y_raw}
    }

def get_direction_string(x, y, threshold=10000):
    """Convert X,Y values to direction string"""
    directions = []
    
    if y > threshold:
        directions.append("UP")
    elif y < -threshold:
        directions.append("DOWN")
    
    if x > threshold:
        directions.append("RIGHT")
    elif x < -threshold:
        directions.append("LEFT")
    
    if not directions:
        return "CENTER"
    
    return "+".join(directions)

def check_ads1115_connection():
    """Check if ADS1115 is connected and responding"""
    try:
        # Try to read the config register
        data = i2c.readfrom_mem(ADS1115_ADDR, ADS1115_REG_CONFIG, 2)
        print(f"ADS1115 found at address 0x{ADS1115_ADDR:02X}")
        return True
    except Exception as e:
        print(f"ADS1115 not found at address 0x{ADS1115_ADDR:02X}: {e}")
        print("Check I2C wiring and 5V power supply.")
        return False

def test_voltage_range():
    """Test the voltage range of joysticks to verify 3.3V operation"""
    print("\n=== Voltage Range Test ===")
    print("Move joysticks to extreme positions to test 3.3V range.")
    print("Good 3.3V joysticks should show values from ~20000 to ~65535.")
    print("Press Ctrl+C when done.")
    
    # Track min/max values for each channel
    ranges = {
        'ch0': {'min': 65535, 'max': 0},
        'ch1': {'min': 65535, 'max': 0},
        'ch2': {'min': 65535, 'max': 0},
        'ch3': {'min': 65535, 'max': 0}
    }
    
    try:
        while True:
            # Read all channels
            ch0 = read_ads1115_channel(0)
            ch1 = read_ads1115_channel(1)
            ch2 = read_ads1115_channel(2)
            ch3 = read_ads1115_channel(3)
            
            # Update ranges
            ranges['ch0']['min'] = min(ranges['ch0']['min'], ch0)
            ranges['ch0']['max'] = max(ranges['ch0']['max'], ch0)
            ranges['ch1']['min'] = min(ranges['ch1']['min'], ch1)
            ranges['ch1']['max'] = max(ranges['ch1']['max'], ch1)
            ranges['ch2']['min'] = min(ranges['ch2']['min'], ch2)
            ranges['ch2']['max'] = max(ranges['ch2']['max'], ch2)
            ranges['ch3']['min'] = min(ranges['ch3']['min'], ch3)
            ranges['ch3']['max'] = max(ranges['ch3']['max'], ch3)
            
            print(f"L_X: {ranges['ch0']['min']:5d}-{ranges['ch0']['max']:5d} | "
                  f"L_Y: {ranges['ch1']['min']:5d}-{ranges['ch1']['max']:5d} | "
                  f"R_X: {ranges['ch2']['min']:5d}-{ranges['ch2']['max']:5d} | "
                  f"R_Y: {ranges['ch3']['min']:5d}-{ranges['ch3']['max']:5d}", end='\r')
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print(f"\n\nFinal 3.3V Range Test Results:")
        print(f"Left  X: {ranges['ch0']['min']:5d} to {ranges['ch0']['max']:5d} (range: {ranges['ch0']['max']-ranges['ch0']['min']:5d})")
        print(f"Left  Y: {ranges['ch1']['min']:5d} to {ranges['ch1']['max']:5d} (range: {ranges['ch1']['max']-ranges['ch1']['min']:5d})")
        print(f"Right X: {ranges['ch2']['min']:5d} to {ranges['ch2']['max']:5d} (range: {ranges['ch2']['max']-ranges['ch2']['min']:5d})")
        print(f"Right Y: {ranges['ch3']['min']:5d} to {ranges['ch3']['max']:5d} (range: {ranges['ch3']['max']-ranges['ch3']['min']:5d})")
        print(f"\nGood 3.3V operation should show ranges of ~40000+ for full deflection.")

def calibrate_joysticks():
    """Calibrate joystick center positions using ADS1115"""
    print("\n=== ADS1115 Joystick Calibration (3.3V) ===")
    print("Please ensure both joysticks are in center position...")
    print("Calibrating in 3 seconds...")
    
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("Calibrating...")
    
    # Take multiple samples for better accuracy
    samples = 20  # Fewer samples since ADS1115 is slower
    left_x_total = 0
    left_y_total = 0
    right_x_total = 0
    right_y_total = 0
    
    for i in range(samples):
        print(f"Sample {i+1}/{samples}...", end='\r')
        left_x_total += (32777 + 65535) - read_ads1115_channel(0)  # Invert left X
        left_y_total += (32777 + 65535) - read_ads1115_channel(1)  # Invert left Y
        right_x_total += read_ads1115_channel(2)
        right_y_total += read_ads1115_channel(3)
        time.sleep(0.1)  # Longer delay for ADS1115
    
    # Calculate averages
    calibration['left_x_center'] = left_x_total // samples
    calibration['left_y_center'] = left_y_total // samples
    calibration['right_x_center'] = right_x_total // samples
    calibration['right_y_center'] = right_y_total // samples
    
    print(f"\nCalibration complete!")
    print(f"Left center: X={calibration['left_x_center']}, Y={calibration['left_y_center']}")
    print(f"Right center: X={calibration['right_x_center']}, Y={calibration['right_y_center']}")
    print(f"Values should be near 53563 for good 3.3V operation.")

def test_joystick_basic():
    """Basic joystick reading test"""
    print("\n=== Basic ADS1115 Joystick Test (3.3V) ===")
    print("Move joysticks and press buttons. Press Ctrl+C to stop.")
    print("Format: LEFT(x,y,btn) | RIGHT(x,y,btn) | Directions | RAW values")
    
    try:
        while True:
            values = get_joystick_values()
            
            left = values['left']
            right = values['right']
            
            left_dir = get_direction_string(left['x'], left['y'])
            right_dir = get_direction_string(right['x'], right['y'])
            
            # Format output
            left_btn = "PRESSED" if left['pressed'] else "      "
            right_btn = "PRESSED" if right['pressed'] else "      "
            
            print(f"LEFT({left['x']:6d},{left['y']:6d},{left_btn}) | "
                  f"RIGHT({right['x']:6d},{right['y']:6d},{right_btn}) | "
                  f"L:{left_dir:<12} R:{right_dir:<12} | "
                  f"RAW: L({left['raw_x']:5d},{left['raw_y']:5d}) R({right['raw_x']:5d},{right['raw_y']:5d})", end='\r')
            
            time.sleep(0.15)  # Optimized update rate for ADS1115
            
    except KeyboardInterrupt:
        print("\nTest stopped.")

def test_joystick_raw():
    """Raw ADS1115 values test"""
    print("\n=== Raw ADS1115 Values Test (3.3V) ===")
    print("Displaying raw ADS1115 values (0-65535). Press Ctrl+C to stop.")
    print("Format: L_RAW(x,y) | R_RAW(x,y) | Switches")
    
    try:
        while True:
            values = get_joystick_values()
            
            left = values['left']
            right = values['right']
            
            left_btn = "L_SW" if left['pressed'] else "    "
            right_btn = "R_SW" if right['pressed'] else "    "
            
            print(f"L_RAW({left['raw_x']:5d},{left['raw_y']:5d}) | "
                  f"R_RAW({right['raw_x']:5d},{right['raw_y']:5d}) | "
                  f"{left_btn} {right_btn}", end='\r')
            
            time.sleep(0.15)
            
    except KeyboardInterrupt:
        print("\nTest stopped.")

def test_ads1115_channels():
    """Test individual ADS1115 channels"""
    print("\n=== ADS1115 Channel Test (3.3V) ===")
    print("Testing each channel individually with raw and processed values.")
    print("Raw values show actual ADC readings.")
    print("Processed values show after left Y-axis inversion.")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            ch0 = read_ads1115_channel(0)  # Left X
            ch1 = read_ads1115_channel(1)  # Left Y (raw)
            ch2 = read_ads1115_channel(2)  # Right X
            ch3 = read_ads1115_channel(3)  # Right Y
            
            # Apply left joystick inversions like in get_joystick_values()
            ch0_inverted = (32777 + 65535) - ch0  # Left X inversion
            ch1_inverted = (32777 + 65535) - ch1  # Left Y inversion
            
            print(f"RAW:  L_X:{ch0:5d} | L_Y:{ch1:5d} | R_X:{ch2:5d} | R_Y:{ch3:5d}")
            print(f"PROC: L_X:{ch0_inverted:5d} | L_Y:{ch1_inverted:5d} | R_X:{ch2:5d} | R_Y:{ch3:5d}")
            print("", end='\r')
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\nTest stopped.")

def show_calibration_values():
    """Display current calibration values and suggest adjustments"""
    print("\n=== Current Calibration Values ===")
    print(f"Left  X center: {calibration['left_x_center']}")
    print(f"Left  Y center: {calibration['left_y_center']}")
    print(f"Right X center: {calibration['right_x_center']}")
    print(f"Right Y center: {calibration['right_y_center']}")
    print(f"Deadzone: {calibration['deadzone']}")
    print(f"Direction threshold: 12000")
    
    print("\n=== Current Raw Values (center position) ===")
    print("Move joysticks to center position for comparison:")
    
    for i in range(5):
        left_x_raw = read_ads1115_channel(0)
        left_y_raw = read_ads1115_channel(1)
        right_x_raw = read_ads1115_channel(2)
        right_y_raw = read_ads1115_channel(3)
        
        # Show both raw and inverted values for left joystick
        left_x_inv = (32777 + 65535) - left_x_raw
        left_y_inv = (32777 + 65535) - left_y_raw
        
        print(f"Sample {i+1}: L_raw({left_x_raw:5d},{left_y_raw:5d}) L_inv({left_x_inv:5d},{left_y_inv:5d}) R_raw({right_x_raw:5d},{right_y_raw:5d})")
        time.sleep(0.5)

def run_comprehensive_test():
    """Run all ADS1115 joystick tests"""
    print("=== Comprehensive ADS1115 Joystick Test (3.3V Operation) ===")
    print("This test uses ADS1115 for full 4-channel analog control at 3.3V")
    print("Left joystick is mounted upside down (both X and Y axes inverted)")
    print()
    
    # Check ADS1115 connection first
    if not check_ads1115_connection():
        print("ERROR: Cannot communicate with ADS1115!")
        print("Check I2C wiring and 3.3V power supply.")
        return
    
    # Calibrate first
    calibrate_joysticks()
    
    while True:
        print("\n=== Test Menu ===")
        print("1. Basic joystick test (processed values)")
        print("2. Raw ADS1115 values test")
        print("3. Individual channel test")
        print("4. 3.3V voltage range test")
        print("5. Recalibrate joysticks")
        print("6. Check ADS1115 connection")
        print("7. Show calibration values")
        print("8. Exit")
        
        try:
            choice = input("Select test (1-8): ").strip()
            
            if choice == '1':
                test_joystick_basic()
            elif choice == '2':
                test_joystick_raw()
            elif choice == '3':
                test_ads1115_channels()
            elif choice == '4':
                test_voltage_range()
            elif choice == '5':
                calibrate_joysticks()
            elif choice == '6':
                check_ads1115_connection()
            elif choice == '7':
                show_calibration_values()
            elif choice == '8':
                print("Exiting ADS1115 joystick test.")
                break
            else:
                print("Invalid choice. Please select 1-8.")
                
        except KeyboardInterrupt:
            print("\nTest interrupted.")
            break

# Usage
print("Initializing ADS1115 joystick test (3.3V Operation)...")

run_comprehensive_test() 