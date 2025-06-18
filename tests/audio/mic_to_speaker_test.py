import sys
sys.path.insert(0, '../../hw')
from machine import Pin, ADC, I2S
import time
import uarray

def test_mic_to_speaker():
    """Records audio from the microphone and plays it back through the speaker."""

    # --- Configuration ---
    # Pins based on README.md
    MIC_ADC_PIN = 28
    AMP_SD_PIN = 21
    I2S_BCLK_PIN = 14
    I2S_LRC_PIN = 15
    I2S_DIN_PIN = 20
    
    # Audio settings
    SAMPLE_RATE = 8000  # 8kHz is common for voice
    RECORD_DURATION_S = 5
    BUFFER_SIZE_IN_SAMPLES = SAMPLE_RATE * RECORD_DURATION_S

    # --- Initialization ---
    print("Initializing components...")
    
    # 1. Initialize Microphone (ADC)
    try:
        adc = ADC(Pin(MIC_ADC_PIN))
        print(f"✓ ADC initialized on GP{MIC_ADC_PIN}")
    except Exception as e:
        print(f"✗ Failed to initialize ADC: {e}")
        return False

    # 2. Initialize Speaker (I2S) and Amplifier
    try:
        # Enable amplifier
        amp_sd = Pin(AMP_SD_PIN, Pin.OUT)
        amp_sd.value(1)
        print(f"✓ Amplifier enabled on GP{AMP_SD_PIN}")

        # Configure I2S
        i2s = I2S(0,
                  sck=Pin(I2S_BCLK_PIN),
                  ws=Pin(I2S_LRC_PIN),
                  sd=Pin(I2S_DIN_PIN),
                  mode=I2S.TX,
                  bits=16,
                  format=I2S.MONO,
                  rate=SAMPLE_RATE,
                  ibuf=BUFFER_SIZE_IN_SAMPLES * 2) # Buffer needs to hold all samples
        print("✓ I2S interface initialized for speaker")
    except Exception as e:
        print(f"✗ Failed to initialize I2S/Amplifier: {e}")
        return False
        
    # --- Recording ---
    print(f"\nPrepare to record for {RECORD_DURATION_S} seconds...")
    time.sleep(2)
    print("🔴 RECORDING NOW...")

    # Create a buffer to store the audio samples
    # 'h' specifies signed 16-bit integers, which is what I2S expects
    audio_buffer = uarray.array('h', [0] * BUFFER_SIZE_IN_SAMPLES)

    try:
        for i in range(BUFFER_SIZE_IN_SAMPLES):
            # Read a 16-bit unsigned value from the ADC (0-65535)
            adc_value = adc.read_u16()
            
            # Convert the unsigned ADC value to a signed 16-bit value (-32768 to 32767)
            # by subtracting the midpoint (32768).
            sample = adc_value - 32768
            audio_buffer[i] = sample
            
            # Small delay to match the sample rate approximately
            # In a real application, timers would be used for precision.
            time.sleep_us(1000000 // SAMPLE_RATE)

    except Exception as e:
        print(f"✗ An error occurred during recording: {e}")
        return False

    print("✅ Recording finished.")
    
    # --- Playback ---
    print("\nPlaying back audio...")

    try:
        # Write the entire buffer to the speaker. This call returns once the data
        # is in the I2S buffer, but playback happens in the background.
        num_bytes_written = i2s.write(audio_buffer)
        print(f"  - Wrote {num_bytes_written} bytes to the I2S buffer.")
        print(f"  - Waiting for {RECORD_DURATION_S} seconds for playback to complete...")

        # We must wait for the playback to finish before de-initializing.
        time.sleep(RECORD_DURATION_S)

        print("✅ Playback finished.")
    except Exception as e:
        print(f"✗ An error occurred during playback: {e}")
        return False
    finally:
        # --- Cleanup ---
        print("\nCleaning up resources...")
        i2s.deinit()
        amp_sd.value(0) # Shutdown amplifier
        print("✓ I2S deinitialized and amplifier shut down.")

    return True

if __name__ == '__main__':
    print("Microphone to Speaker Passthrough Test")
    print("=" * 40)
    
    if test_mic_to_speaker():
        print("\n🎉 Test completed!")
    else:
        print("\n❌ Test failed!") 