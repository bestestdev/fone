import sys
sys.path.insert(0, '../../hw')
from machine import UART, Pin, ADC, I2S
import time
import uarray
import os

# Environment variables storage for MicroPython compatibility
_env_vars = {}

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from project root .env file"""
    global _env_vars
    try:
        # Path to .env file relative to this test file (../../.env)
        env_path = "../../.env"
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        _env_vars[key.strip()] = value.strip()
        print("Loaded environment variables from .env file")
        return True
    except OSError:
        print("No .env file found at project root")
        return False

# Get environment variable (MicroPython compatible)
def getenv(key, default=None):
    """Get environment variable, checking both os.getenv and our loaded vars"""
    # First try standard os.getenv if available
    try:
        value = os.getenv(key)
        if value is not None:
            return value
    except AttributeError:
        pass

    # Fall back to our loaded environment variables
    return _env_vars.get(key, default)

class PhoneCallManager:
    def __init__(self):
        # SIM7600G Configuration
        self.uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
        self.power_key = Pin(2, Pin.OUT)
        self.status_pin = Pin(3, Pin.IN)

        # Audio Configuration
        self.MIC_ADC_PIN = 28
        self.AMP_SD_PIN = 21
        self.I2S_BCLK_PIN = 14
        self.I2S_LRC_PIN = 15
        self.I2S_DIN_PIN = 20
        self.SAMPLE_RATE = 8000

        # Button Configuration (ANO Encoder)
        self.encoder_pins = {
            'ENCA': Pin(17, Pin.IN, Pin.PULL_UP),   # Rotary encoder A pin
            'ENCB': Pin(22, Pin.IN, Pin.PULL_UP),   # Rotary encoder B pin
            'SW1': Pin(6, Pin.IN, Pin.PULL_UP),     # Center button (answer/hangup)
            'SW2': Pin(5, Pin.IN, Pin.PULL_UP),     # Down button (hangup)
            'SW3': Pin(4, Pin.IN, Pin.PULL_UP),     # Right button (hangup)
            'SW4': Pin(19, Pin.IN, Pin.PULL_UP),    # Up button (hangup)
            'SW5': Pin(18, Pin.IN, Pin.PULL_UP),    # Left button (hangup)
        }

        # State tracking
        self.call_active = False
        self.audio_active = False
        self.last_button_states = {}

        # Initialize components
        self.adc = None
        self.i2s = None
        self.amp_sd = None

    def reset_and_power_on_sim7600g(self):
        """Power on the SIM7600G module"""
        print("Powering on SIM7600G...")
        self.power_key.value(1)
        time.sleep(0.5)
        self.power_key.value(0)
        time.sleep(1)
        self.power_key.value(1)
        print("SIM7600G power on sequence sent")
        time.sleep(5)  # Wait for module to boot

    def send_at_command(self, command, timeout=5):
        """Send AT command and get response"""
        print(f"Sending: {command}")
        self.uart.write(command + '\r\n')

        full_response_bytes = b""
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            if self.uart.any():
                chunk = self.uart.read()
                if chunk:
                    full_response_bytes += chunk
            time.sleep(0.1)

        response_str = ""
        if full_response_bytes:
            try:
                response_str = full_response_bytes.decode('utf-8')
                print(f"Response: {response_str.strip()}")
            except UnicodeDecodeError:
                response_str = str(full_response_bytes)
                print(f"Response (raw): {response_str}")
        else:
            print(f"No response from module for command '{command}' after {timeout}s")

        time.sleep(0.5)
        return response_str

    def test_sim_connection(self):
        """Test basic SIM communication"""
        print("\n=== Testing SIM Connection ===")
        for attempt in range(5):
            response = self.send_at_command("AT", timeout=2)
            if any(keyword in response for keyword in ["OK", "RDY", "READY", "+CPIN"]):
                print("✓ SIM module is responding")
                return True
            if attempt < 4:
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
        print("✗ SIM connection failed")
        return False

    def make_call(self, phone_number):
        """Initiate a phone call"""
        print(f"\n=== Making call to {phone_number} ===")

        # Check network registration first
        response = self.send_at_command("AT+CREG?")
        if "+CREG: 0,1" not in response and "+CREG: 0,5" not in response:
            print("Not registered to network, attempting automatic registration...")

            # Enable automatic network registration
            self.send_at_command("AT+COPS=0")

            # Wait and check registration again
            print("Waiting for network registration...")
            for attempt in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                response = self.send_at_command("AT+CREG?")
                if "+CREG: 0,1" in response or "+CREG: 0,5" in response:
                    print(f"✓ Successfully registered to network after {attempt + 1} seconds")
                    break
                print(f"Registration attempt {attempt + 1}/30...")
            else:
                print("✗ Failed to register to network after 30 seconds")
                return False

        # Make the call (voice call)
        response = self.send_at_command(f"ATD{phone_number};", timeout=15)

        if "OK" in response or "CONNECT" in response:
            print("✓ Call initiated successfully")
            self.call_active = True
            return True
        else:
            print("✗ Failed to initiate call")
            print(f"Response: {response}")
            return False

    def hangup_call(self):
        """Hang up the current call"""
        if not self.call_active:
            print("No active call to hang up")
            return

        print("\n=== Hanging up call ===")
        response = self.send_at_command("AT+CHUP", timeout=5)

        if "OK" in response:
            print("✓ Call hung up successfully")
            self.call_active = False
            self.stop_audio()
        else:
            print("✗ Failed to hang up call")

    def check_call_status(self):
        """Check current call status"""
        response = self.send_at_command("AT+CLCC", timeout=3)

        if "+CLCC:" in response:
            # Parse call status
            if "0,0" in response:  # Active call
                if not self.call_active:
                    print("✓ Call connected - starting audio")
                    self.call_active = True
                    self.start_audio()
            elif "0,3" in response:  # Incoming call
                print("📞 Incoming call detected")
            elif "0,2" in response:  # Dialing
                print("📞 Dialing...")
        else:
            # No active calls
            if self.call_active:
                print("📞 Call ended")
                self.call_active = False
                self.stop_audio()

    def init_audio(self):
        """Initialize audio components"""
        print("Initializing audio components...")

        try:
            # Initialize microphone (ADC)
            self.adc = ADC(Pin(self.MIC_ADC_PIN))
            print(f"✓ Microphone initialized on GP{self.MIC_ADC_PIN}")

            # Initialize amplifier
            self.amp_sd = Pin(self.AMP_SD_PIN, Pin.OUT)
            self.amp_sd.value(1)  # Enable amplifier
            print(f"✓ Amplifier enabled on GP{self.AMP_SD_PIN}")

            # Initialize I2S for speaker
            self.i2s = I2S(0,
                          sck=Pin(self.I2S_BCLK_PIN),
                          ws=Pin(self.I2S_LRC_PIN),
                          sd=Pin(self.I2S_DIN_PIN),
                          mode=I2S.TX,
                          bits=16,
                          format=I2S.MONO,
                          rate=self.SAMPLE_RATE,
                          ibuf=4096)
            print("✓ I2S speaker initialized")
            return True

        except Exception as e:
            print(f"✗ Audio initialization failed: {e}")
            return False

    def start_audio(self):
        """Start audio processing for call"""
        if self.audio_active:
            return

        if not self.init_audio():
            return

        print("🔊 Starting audio processing...")
        self.audio_active = True

    def stop_audio(self):
        """Stop audio processing"""
        if not self.audio_active:
            return

        print("🔇 Stopping audio processing...")
        self.audio_active = False

        if self.i2s:
            self.i2s.deinit()
            self.i2s = None

        if self.amp_sd:
            self.amp_sd.value(0)  # Disable amplifier

    def process_audio_chunk(self):
        """Process a small chunk of audio"""
        if not self.adc or not self.i2s:
            return

        try:
            # Process smaller chunks to avoid blocking
            chunk_size = 32
            audio_buffer = uarray.array('h', [0] * chunk_size)

            # Record audio from microphone
            for i in range(chunk_size):
                if not self.audio_active or not self.adc:
                    break
                adc_value = self.adc.read_u16()
                # Convert to signed 16-bit
                sample = adc_value - 32768
                audio_buffer[i] = sample

            # Play audio through speaker (for now just echo back)
            # In a real phone call, this would be audio from the remote party
            if self.audio_active and self.i2s:
                self.i2s.write(audio_buffer)

        except Exception as e:
            print(f"Audio processing error: {e}")
            self.stop_audio()

    def get_button_states(self):
        """Read current button states"""
        states = {}
        for name, pin in self.encoder_pins.items():
            if name.startswith('SW'):
                # Pins are active low
                states[name] = not pin.value()
        return states

    def check_hangup_buttons(self):
        """Check if any hangup button is pressed"""
        states = self.get_button_states()

        # Any button can hang up the call
        for button_name, pressed in states.items():
            if pressed and not self.last_button_states.get(button_name, False):
                print(f"🔴 Hangup button {button_name} pressed")
                self.hangup_call()
                break

        self.last_button_states = states.copy()

    def run_phone_test(self, phone_number):
        """Run the complete phone call test"""
        print("=== Phone Call Test ===")
        print(f"Target number: {phone_number}")
        print("Any button will hang up the call")
        print()

        # Initialize SIM
        self.reset_and_power_on_sim7600g()

        if not self.test_sim_connection():
            print("❌ SIM connection failed - cannot proceed")
            return False

        # Make the call
        if not self.make_call(phone_number):
            print("❌ Call failed")
            return False

        print("\n📞 Call in progress...")
        print("Press any button to hang up")
        print("Press Ctrl+C to exit")

        try:
            while self.call_active:
                # Check call status
                self.check_call_status()

                # Check for hangup button presses
                self.check_hangup_buttons()

                # Process audio if active
                if self.audio_active:
                    self.process_audio_chunk()

                time.sleep(0.01)  # Shorter delay for audio processing

        except KeyboardInterrupt:
            print("\n\n⏹️  Test interrupted")
            self.hangup_call()

        finally:
            self.stop_audio()
            print("✅ Phone call test completed")

        return True

def main():
    """Main function to run phone call test"""
    # Try to load environment variables from .env file
    load_env_file()

    # Get phone number from environment or user input
    phone_number = getenv("TEST_PHONE_NUMBER")

    if not phone_number:
        print("TEST_PHONE_NUMBER environment variable not set")
        phone_number = input("Enter phone number to call: ").strip()

    if not phone_number:
        print("❌ No phone number provided")
        return

    # Create phone call manager and run test
    phone_manager = PhoneCallManager()
    phone_manager.run_phone_test(phone_number)

if __name__ == "__main__":
    main()