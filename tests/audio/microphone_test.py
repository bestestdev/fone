import sys
sys.path.insert(0, '../../hw')
from machine import Pin, ADC
import time

def test_microphone():
    """Test GY-MAX4466 Electret Microphone"""

    # Pin definition from README
    MIC_ADC_PIN = 28 # GP28, ADC(2)

    print("Initializing GY-MAX4466 Microphone...")

    try:
        # Initialize ADC on the microphone pin
        adc = ADC(Pin(MIC_ADC_PIN))
        print(f"✓ ADC initialized on GP{MIC_ADC_PIN}")
    except Exception as e:
        print(f"✗ Failed to initialize ADC: {e}")
        return False

    print("\nReading microphone level...")
    print("Speak or make noise near the microphone.")
    print("You should see the ADC value change.")
    print("The value is a 16-bit number (0-65535).")
    print("Press Ctrl+C to stop the test.\n")

    try:
        while True:
            # Read the analog value from the microphone
            adc_value = adc.read_u16()
            
            # Print the value. Using \r to print on the same line.
            print(f"ADC Value: {adc_value:5d}", end='\r')
            
            # A small delay to make the output readable
            time.sleep_ms(50)

    except KeyboardInterrupt:
        print("\n\nTest stopped by user.")
    except Exception as e:
        print(f"\n✗ An error occurred during reading: {e}")
        return False

    print("\n✓ Microphone test completed successfully!")
    return True

if __name__ == '__main__':
    print("GY-MAX4466 Microphone Test")
    print("=" * 40)
    
    try:
        if not test_microphone():
            print("\n❌ Test failed!")
        else:
            print("\n🎉 Test finished!")
            
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}") 