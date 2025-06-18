import sys
sys.path.insert(0, '../../hw')
from machine import Pin, I2S
import math
import uarray

def test_max98357a_speaker():
    """Test MAX98357A I2S Amplifier and Speaker"""

    # Pin definitions
    I2S_BCLK_PIN = 14  # I2S Bit Clock (BCLK)
    I2S_LRC_PIN = 15   # I2S Left/Right Clock (LRC/WS)
    I2S_DIN_PIN = 20   # I2S Data In (DIN)
    AMP_SD_PIN = 21    # Amplifier Shutdown pin (active-low)

    print("Initializing MAX98357A I2S Amplifier...")

    # Configure amplifier shutdown pin and enable amplifier
    amp_sd = Pin(AMP_SD_PIN, Pin.OUT)
    amp_sd.value(1) # Bring out of shutdown mode
    print("✓ Amplifier enabled (SD pin set to HIGH)")

    # Configure I2S
    SAMPLE_RATE = 16000
    SAMPLE_BITS = 16
    BUFFER_LENGTH_IN_BYTES = 4096

    try:
        i2s = I2S(0,
                  sck=Pin(I2S_BCLK_PIN),
                  ws=Pin(I2S_LRC_PIN),
                  sd=Pin(I2S_DIN_PIN),
                  mode=I2S.TX,
                  bits=SAMPLE_BITS,
                  format=I2S.MONO,
                  rate=SAMPLE_RATE,
                  ibuf=BUFFER_LENGTH_IN_BYTES)
        
        print("✓ I2S interface initialized successfully")
        print(f"  - Sample Rate: {SAMPLE_RATE} Hz")
        print(f"  - Sample Bits: {SAMPLE_BITS}")
        print(f"  - Mode: MONO")
        
    except Exception as e:
        print(f"✗ Failed to initialize I2S: {e}")
        return False

    # Generate a sine wave tone
    print("\nGenerating 440Hz sine wave tone...")
    TONE_FREQUENCY = 440
    
    # Number of samples in one period of the sine wave
    SAMPLES_PER_PERIOD = SAMPLE_RATE // TONE_FREQUENCY
    
    # Create a buffer to store one period of the sine wave
    sine_wave = uarray.array('h', [0] * SAMPLES_PER_PERIOD) # 'h' for signed 16-bit

    for i in range(SAMPLES_PER_PERIOD):
        # Generate sine wave value and scale to 16-bit integer range
        sine_value = math.sin(2 * math.pi * i / SAMPLES_PER_PERIOD)
        amplitude = 32767 # Max amplitude for 16-bit signed audio
        sine_wave[i] = int(sine_value * amplitude)

    print("✓ Tone generated. Playing sound through speaker...")
    print("  A 440Hz (A4) tone should be audible.")
    print("  Press Ctrl+C to stop the test.")

    try:
        # Continuously write the sine wave to the I2S bus
        while True:
            i2s.write(sine_wave)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    except Exception as e:
        print(f"\n✗ An error occurred during playback: {e}")
        return False
    finally:
        # Cleanup
        i2s.deinit()
        amp_sd.value(0) # Shutdown amplifier to save power
        print("I2S interface deinitialized and amplifier has been shut down.")

    print("\n✓ MAX98357A test completed successfully!")
    return True

if __name__ == '__main__':
    print("MAX98357A I2S Amplifier and Speaker Test")
    print("=" * 40)
    
    try:
        if not test_max98357a_speaker():
            print("\n❌ Test failed!")
        else:
            print("\n🎉 Test finished!")
            
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}") 