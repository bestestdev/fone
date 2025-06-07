from machine import Pin, PWM
import time

# Vibration motor control pin (GP16)
vibration_motor = PWM(Pin(16))
vibration_motor.freq(1000)  # 1kHz PWM frequency

# Test functions
def vibration_off():
    """Turn off vibration motor"""
    vibration_motor.duty_u16(0)
    print("Vibration motor OFF")

def vibration_on(intensity=100):
    """Turn on vibration motor with specified intensity (0-100%)"""
    if intensity < 0:
        intensity = 0
    elif intensity > 100:
        intensity = 100
    
    duty_cycle = int((intensity / 100) * 65535)
    vibration_motor.duty_u16(duty_cycle)
    print(f"Vibration motor ON at {intensity}% intensity")

def vibration_pulse(duration_ms=200, intensity=100):
    """Create a single vibration pulse"""
    print(f"Vibration pulse: {duration_ms}ms at {intensity}% intensity")
    vibration_on(intensity)
    time.sleep(duration_ms / 1000)
    vibration_off()

def vibration_pattern(pattern, intensity=100):
    """
    Execute a vibration pattern
    Pattern format: list of (duration_ms, pause_ms) tuples
    Example: [(200, 100), (300, 200)] = 200ms on, 100ms off, 300ms on, 200ms off
    """
    print(f"Executing vibration pattern with {len(pattern)} pulses")
    
    for i, (duration, pause) in enumerate(pattern):
        print(f"  Pulse {i+1}: {duration}ms vibration, {pause}ms pause")
        vibration_pulse(duration, intensity)
        if pause > 0:
            time.sleep(pause / 1000)

def test_basic_vibration():
    """Test basic vibration on/off functionality"""
    print("\n=== Basic Vibration Test ===")
    
    print("Testing vibration motor...")
    print("Note: If motor vibration is weak or Pico gets warm, you may need transistor control")
    
    vibration_on(100)
    time.sleep(1)
    vibration_off()
    time.sleep(0.5)
    
    print("Basic vibration test complete")

def test_intensity_levels():
    """Test different vibration intensity levels"""
    print("\n=== Intensity Level Test ===")
    
    intensities = [25, 50, 75, 100]
    for intensity in intensities:
        print(f"Testing {intensity}% intensity...")
        vibration_on(intensity)
        time.sleep(0.8)
        vibration_off()
        time.sleep(0.5)
    
    print("Intensity test complete")

def test_vibration_patterns():
    """Test various vibration patterns for different notifications"""
    print("\n=== Vibration Pattern Test ===")
    
    # Single short pulse (button press feedback)
    print("1. Button press feedback:")
    vibration_pulse(50, 80)
    time.sleep(1)
    
    # Double pulse (incoming call)
    print("2. Incoming call pattern:")
    vibration_pattern([(300, 100), (300, 0)], 100)
    time.sleep(1)
    
    # Triple pulse (new message)
    print("3. New message pattern:")
    vibration_pattern([(150, 100), (150, 100), (150, 0)], 90)
    time.sleep(1)
    
    # Long pulse (alarm/timer)
    print("4. Alarm pattern:")
    vibration_pulse(800, 100)
    time.sleep(1)
    
    # Morse code pattern (SOS)
    print("5. SOS pattern (... --- ...):")
    sos_pattern = [
        # S (...)
        (100, 100), (100, 100), (100, 300),
        # O (---)
        (300, 100), (300, 100), (300, 300),
        # S (...)
        (100, 100), (100, 100), (100, 0)
    ]
    vibration_pattern(sos_pattern, 85)
    time.sleep(2)
    
    print("Pattern test complete")

def test_fade_in_out():
    """Test gradual fade in and fade out effect"""
    print("\n=== Fade In/Out Test ===")
    
    print("Fade in...")
    for intensity in range(0, 101, 5):
        vibration_on(intensity)
        time.sleep(0.05)
    
    time.sleep(0.5)
    
    print("Fade out...")
    for intensity in range(100, -1, -5):
        vibration_on(intensity)
        time.sleep(0.05)
    
    vibration_off()
    print("Fade test complete")

def test_interactive_control():
    """Interactive test allowing manual control"""
    print("\n=== Interactive Control Test ===")
    print("Commands:")
    print("  0-9: Set intensity (0=off, 9=100%)")
    print("  p: Single pulse")
    print("  c: Incoming call pattern")
    print("  m: New message pattern")
    print("  a: Alarm pattern")
    print("  s: SOS pattern")
    print("  f: Fade in/out")
    print("  q: Quit interactive mode")
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'q':
                vibration_off()
                print("Exiting interactive mode")
                break
            elif command.isdigit():
                intensity = int(command) * 10
                if intensity == 0:
                    vibration_off()
                else:
                    vibration_on(intensity)
                    print(f"Continuous vibration at {intensity}%")
            elif command == 'p':
                vibration_pulse(200, 80)
            elif command == 'c':
                vibration_pattern([(300, 100), (300, 0)], 100)
            elif command == 'm':
                vibration_pattern([(150, 100), (150, 100), (150, 0)], 90)
            elif command == 'a':
                vibration_pulse(800, 100)
            elif command == 's':
                sos_pattern = [
                    (100, 100), (100, 100), (100, 300),
                    (300, 100), (300, 100), (300, 300),
                    (100, 100), (100, 100), (100, 0)
                ]
                vibration_pattern(sos_pattern, 85)
            elif command == 'f':
                test_fade_in_out()
            else:
                print("Unknown command")
                
        except KeyboardInterrupt:
            vibration_off()
            print("\nExiting interactive mode")
            break
        except Exception as e:
            print(f"Error: {e}")

def test_power_consumption():
    """Test power consumption at different intensities"""
    print("\n=== Power Consumption Test ===")
    print("Running motor at different intensities for power measurement...")
    
    intensities = [25, 50, 75, 100]
    for intensity in intensities:
        print(f"Running at {intensity}% for 5 seconds...")
        vibration_on(intensity)
        time.sleep(5)
        vibration_off()
        time.sleep(2)
        print(f"  {intensity}% test complete")
    
    print("Power consumption test complete")

def run_comprehensive_test():
    """Run all vibration motor tests"""
    print("Starting comprehensive vibration motor test...")
    print("Motor connected to GP16 via NPN transistor")
    
    # Ensure motor is off at start
    vibration_off()
    time.sleep(0.5)
    
    # Run all tests
    test_basic_vibration()
    test_intensity_levels()
    test_vibration_patterns()
    test_fade_in_out()
    test_power_consumption()
    
    print("\n=== All Tests Complete ===")
    print("Vibration motor functionality verified!")
    
    # Ask if user wants interactive mode
    try:
        response = input("\nRun interactive test? (y/n): ").strip().lower()
        if response == 'y':
            test_interactive_control()
    except:
        pass
    
    # Ensure motor is off at end
    vibration_off()

# Usage
if __name__ == "__main__":
    print("3V Vibration Motor Test Suite")
    print("=============================")
    print("Hardware Requirements:")
    print("- 3V 12000rpm vibration motor")
    print("- Connect motor + to GP16 (Pin 21)")
    print("- Connect motor - to GND (Pin 38)")
    print()
    print("Optional (if direct control doesn't work well):")
    print("- NPN transistor (2N2222 or similar)")
    print("- 1kΩ resistor")
    print("- 1N4001 flyback diode")
    print("- See README.md for transistor wiring")
    print()
    
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        vibration_off()
        print("\nTest interrupted by user")
    except Exception as e:
        vibration_off()
        print(f"Test error: {e}") 