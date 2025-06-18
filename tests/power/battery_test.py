import sys
sys.path.insert(0, '../../hw')
from machine import Pin, ADC
import time

def get_battery_level():
    """Reads the battery voltage and calculates the percentage."""

    # --- Configuration ---
    # Pin based on README.md
    BATT_ADC_PIN = 26

    # ADC reference voltage for Pico (usually 3.3V)
    ADC_REF_VOLTAGE = 3.3
    # The ADC returns a 16-bit value (0-65535)
    ADC_MAX_VALUE = 65535
    # Voltage divider ratio (R2 / (R1 + R2)). For 1:1 (e.g., 100k/100k), this is 0.5
    # The real voltage is adc_voltage / DIVIDER_RATIO, so we multiply by 2.
    VOLTAGE_MULTIPLIER = 2.0

    # LiPo battery voltage range
    V_FULL = 4.2  # Fully charged
    V_EMPTY = 3.0 # Fully discharged

    # --- ADC Initialization ---
    try:
        adc = ADC(Pin(BATT_ADC_PIN))
    except Exception as e:
        print(f"✗ Failed to initialize ADC on GP{BATT_ADC_PIN}: {e}")
        return None, None

    # --- Voltage Reading and Calculation ---
    # Read raw ADC value
    raw_value = adc.read_u16()

    # Convert raw value to voltage at the ADC pin
    adc_voltage = (raw_value / ADC_MAX_VALUE) * ADC_REF_VOLTAGE

    # Calculate the actual battery voltage using the multiplier
    battery_voltage = adc_voltage * VOLTAGE_MULTIPLIER

    # --- Percentage Calculation ---
    # Ensure voltage is within the expected range
    if battery_voltage > V_FULL:
        percentage = 100.0
    elif battery_voltage < V_EMPTY:
        percentage = 0.0
    else:
        # Calculate percentage based on the linear voltage range
        percentage = ((battery_voltage - V_EMPTY) / (V_FULL - V_EMPTY)) * 100

    return battery_voltage, percentage

def test_battery_monitor():
    """Continuously displays the battery voltage and percentage."""
    
    print("Starting battery monitor test...")
    print("This will display the voltage and estimated charge percentage.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            voltage, percent = get_battery_level()
            if voltage is not None and percent is not None:
                # Format the output string to be clean and aligned
                voltage_str = f"Voltage: {voltage:.2f}V"
                percent_str = f"Charge: {percent:.1f}%"
                # Use a simple visual bar for percentage
                bar_length = 20
                filled_length = int(bar_length * percent / 100)
                bar = '█' * filled_length + '─' * (bar_length - filled_length)
                
                print(f"{voltage_str: <15} | {percent_str: <15} | [{bar}]", end='\r')
            
            time.sleep(1) # Update every second

    except KeyboardInterrupt:
        print("\n\nTest stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return False

    print("\n✓ Battery monitor test finished.")
    return True

if __name__ == '__main__':
    print("Battery Level Monitor Test")
    print("=" * 40)
    
    if not test_battery_monitor():
        print("\n❌ Test failed!")
    else:
        print("\n🎉 Test completed!") 