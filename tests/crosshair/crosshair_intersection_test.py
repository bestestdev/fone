from machine import Pin, I2C, PWM
import utime
import struct
import math
import sys
sys.path.insert(0, '../../hw')
from epd import EPD_2in9_B_V4_Landscape, DISPLAY_WIDTH, DISPLAY_HEIGHT  # type: ignore

# ADS1115 I2C Configuration
ADS1115_ADDR = 0x48
I2C_SCL = Pin(21)    # I2C0 SCL
I2C_SDA = Pin(20)    # I2C0 SDA

# ADS1115 Registers and Configuration
ADS1115_REG_CONVERSION = 0x00
ADS1115_REG_CONFIG = 0x01
ADS1115_MUX_AIN0 = 0x4000  # Left X
ADS1115_MUX_AIN1 = 0x5000  # Left Y
ADS1115_MUX_AIN2 = 0x6000  # Right X
ADS1115_MUX_AIN3 = 0x7000  # Right Y
ADS1115_PGA_6_144V = 0x0000
ADS1115_MODE_SINGLE = 0x0100
ADS1115_DR_128SPS = 0x0080
ADS1115_COMP_QUE_DISABLE = 0x0003

# Vibration motor control (GP16)
vibration_motor = PWM(Pin(16))
vibration_motor.freq(1000)

# Initialize I2C for joysticks
i2c = I2C(0, scl=I2C_SCL, sda=I2C_SDA, freq=400000)

# Joystick calibration values
calibration = {
    'left_x_center': 53683,
    'left_y_center': 53557,
    'right_x_center': 53581,
    'right_y_center': 53742,
    'deadzone': 1200
}

# Display class is now imported from hw.epd

# Joystick functions
def write_ads1115_config(channel_mux):
    config = (ADS1115_MUX_AIN0 if channel_mux == 0 else
              ADS1115_MUX_AIN1 if channel_mux == 1 else
              ADS1115_MUX_AIN2 if channel_mux == 2 else
              ADS1115_MUX_AIN3) | \
             ADS1115_PGA_6_144V | ADS1115_MODE_SINGLE | \
             ADS1115_DR_128SPS | ADS1115_COMP_QUE_DISABLE | 0x8000
    
    config_bytes = struct.pack('>H', config)
    i2c.writeto_mem(ADS1115_ADDR, ADS1115_REG_CONFIG, config_bytes)

def read_ads1115_channel(channel):
    try:
        write_ads1115_config(channel)
        utime.sleep(0.01)
        data = i2c.readfrom_mem(ADS1115_ADDR, ADS1115_REG_CONVERSION, 2)
        raw_adc = struct.unpack('>h', data)[0]
        return raw_adc + 32768
    except:
        return 32768

def get_joystick_positions():
    """Get normalized joystick positions for crosshair control"""
    # Read raw values
    left_x_raw = read_ads1115_channel(0)
    left_y_raw = read_ads1115_channel(1)
    right_x_raw = read_ads1115_channel(2)
    right_y_raw = read_ads1115_channel(3)
    
    # Apply inversions for left joystick
    left_x_inverted = (32777 + 65535) - left_x_raw
    left_y_inverted = (32777 + 65535) - left_y_raw
    
    # Center the values
    left_x = left_x_inverted - calibration['left_x_center']
    left_y = left_y_inverted - calibration['left_y_center']
    right_x = right_x_raw - calibration['right_x_center']
    right_y = right_y_raw - calibration['right_y_center']
    
    # Apply deadzone
    def apply_deadzone(value, deadzone):
        return 0 if abs(value) < deadzone else value
    
    left_x = apply_deadzone(left_x, calibration['deadzone'])
    left_y = apply_deadzone(-left_y, calibration['deadzone'])  # Invert Y
    right_x = apply_deadzone(right_x, calibration['deadzone'])
    right_y = apply_deadzone(-right_y, calibration['deadzone'])  # Invert Y
    
    # Map to screen coordinates (with some margin from edges)
    margin = 10
    # Normalize to 0-1 range first, then scale to display size
    left_norm_x = (left_x + 32000) / 64000
    left_norm_y = (left_y + 32000) / 64000
    right_norm_x = (right_x + 32000) / 64000
    right_norm_y = (right_y + 32000) / 64000
    
    left_screen_x = int(left_norm_x * (DISPLAY_WIDTH - 2*margin) + margin)
    left_screen_y = int(left_norm_y * (DISPLAY_HEIGHT - 2*margin) + margin)
    right_screen_x = int(right_norm_x * (DISPLAY_WIDTH - 2*margin) + margin)
    right_screen_y = int(right_norm_y * (DISPLAY_HEIGHT - 2*margin) + margin)
    
    # Clamp to screen bounds
    left_screen_x = max(margin, min(DISPLAY_WIDTH - margin, left_screen_x))
    left_screen_y = max(margin, min(DISPLAY_HEIGHT - margin, left_screen_y))
    right_screen_x = max(margin, min(DISPLAY_WIDTH - margin, right_screen_x))
    right_screen_y = max(margin, min(DISPLAY_HEIGHT - margin, right_screen_y))
    
    return (left_screen_x, left_screen_y, right_screen_x, right_screen_y)

# Vibration functions
def vibration_pulse(duration_ms=500, intensity=100):
    """Create a vibration pulse"""
    duty_cycle = int((intensity / 100) * 65535)
    vibration_motor.duty_u16(duty_cycle)
    utime.sleep(duration_ms / 1000)
    vibration_motor.duty_u16(0)

def check_intersection(x1, y1, x2, y2, threshold=15):
    """Check if two crosshairs intersect within threshold distance"""
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance <= threshold

def run_crosshair_test(debug_mode=False):
    """Main crosshair intersection test"""
    print("=== Crosshair Intersection Test ===")
    print("Left joystick = BLACK crosshair")
    print("Right joystick = RED crosshair")
    print("When crosshairs intersect, vibration triggers!")
    print("Press Ctrl+C to exit")
    
    # Check ADS1115 connection first
    try:
        i2c.readfrom_mem(ADS1115_ADDR, ADS1115_REG_CONFIG, 2)
        print("ADS1115 joystick controller found")
    except:
        print("ERROR: ADS1115 not found! Check I2C wiring.")
        return
    
    print(f"Display dimensions: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
    
    if debug_mode:
        print("DEBUG MODE: Skipping display, console output only")
        epd = None
    else:
        # Initialize display
        print("Initializing display...")
        epd = EPD_2in9_B_V4_Landscape()
        print("Display initialized successfully!")
        print(f"EPD dimensions: {epd.width}x{epd.height}")
        epd.clear()
    
    # Draw initial setup - just clear the display
    if epd:
        epd.Clear()  # Force clear the display first
        epd.display()  # Use full display update for initial clear
        utime.sleep(1)
    
    last_intersection = False
    intersection_start_time = 0
    update_counter = 0
    last_left_x, last_left_y = -1, -1
    last_right_x, last_right_y = -1, -1
    
    try:
        while True:
            # Get joystick positions
            left_x, left_y, right_x, right_y = get_joystick_positions()
            
            # Check for intersection
            is_intersecting = check_intersection(left_x, left_y, right_x, right_y, 20)
            
            # Console output for debug mode or regular mode
            status = "INTERSECT!" if is_intersecting else "Moving..."
            print(f"L:({left_x:3d},{left_y:3d}) R:({right_x:3d},{right_y:3d}) - {status} - Dims:{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}", end='\r')
            
            # Check if crosshair positions changed significantly
            left_moved = (abs(left_x - last_left_x) > 3 or abs(left_y - last_left_y) > 3)
            right_moved = (abs(right_x - last_right_x) > 3 or abs(right_y - last_right_y) > 3)
            intersection_changed = is_intersecting != last_intersection
            
            # Display operations (only if display is available)
            if epd:
                # Use partial updates for crosshair movement (much faster!)
                if left_moved:
                    epd.update_crosshair_partial(last_left_x, last_left_y, left_x, left_y, 6, 'black')
                    last_left_x, last_left_y = left_x, left_y
                
                if right_moved:
                    epd.update_crosshair_partial(last_right_x, last_right_y, right_x, right_y, 6, 'red')
                    last_right_x, last_right_y = right_x, right_y
                
                # Full display update only when intersection status changes
                if intersection_changed:
                    # Clear display buffers
                    epd.clear()
                    
                    # Draw crosshairs
                    epd.draw_crosshair(left_x, left_y, 6, 'black')
                    epd.draw_crosshair(right_x, right_y, 6, 'red')
                    
                    # Show INTERCEPT message only when intersecting
                    if is_intersecting:
                        epd.text("INTERCEPT!", 80, 60, 'red')  # Center it more
                    
                    # Use fast full display update
                    epd.display_Fast()
            
            # Trigger vibration on new intersection
            if is_intersecting and not last_intersection:
                print(f"\nINTERSECTION! Crosshairs at ({left_x},{left_y}) and ({right_x},{right_y})")
                vibration_pulse(500, 80)  # 0.5 second vibration at 80% intensity
                intersection_start_time = utime.ticks_ms()
            
            last_intersection = is_intersecting
            update_counter += 1
            utime.sleep(0.05)  # 20 FPS polling rate, but display updates are conditional
            
    except KeyboardInterrupt:
        print("\nCrosshair test stopped")
    finally:
        # Clean up
        vibration_motor.duty_u16(0)
        if epd:
            epd.clear()
            epd.imageblack.text("Test Complete", 20, 140, 0x00)
            epd.display_Fast()
        print("Crosshair intersection test complete!")

if __name__ == "__main__":
    print("Crosshair Intersection Test")
    print("1. Full test with display")
    print("2. Debug mode (console only)")
    
    try:
        choice = input("Select mode (1 or 2): ").strip()
        if choice == '2':
            print("Running in debug mode...")
            run_crosshair_test(debug_mode=True)
        else:
            print("Running full test with display...")
            run_crosshair_test(debug_mode=False)
    except:
        print("Running full test with display...")
        run_crosshair_test(debug_mode=False) 