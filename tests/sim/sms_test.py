from machine import UART, Pin
import time
import os

# Initialize UART for SIM7600G
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# Power control pins
power_key = Pin(2, Pin.OUT)
status_pin = Pin(3, Pin.IN)

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

# Reset and power on the module
def reset_and_power_on_sim7600g():
    # Simple power on sequence
    power_key.value(1)  # Ensure off first
    time.sleep(0.5)
    power_key.value(0)  # Pull low to power on
    time.sleep(1)       # Hold for 1 second
    power_key.value(1)  # Release
    print("SIM7600G power on sequence sent")

# Send AT command and get response
def send_at_command(command, timeout=5):
    print(f"Sending: {command}")

    uart.write(command + '\r\n')
    
    full_response_bytes = b""
    start_time = time.time()
    
    # Continuously try to read for the 'timeout' duration
    while (time.time() - start_time) < timeout:
        if uart.any():
            chunk = uart.read()
            if chunk:
                full_response_bytes += chunk
        time.sleep(0.1) # Slightly longer delay for stability

    response_str = ""
    if full_response_bytes:
        try:
            response_str = full_response_bytes.decode('utf-8')
            print(f"Response: {response_str.strip()}")
        except UnicodeDecodeError:
            # Handle decode errors by converting to string representation
            response_str = str(full_response_bytes) 
            print(f"Response (raw): {response_str}")
    else:
        print(f"No response from module for command '{command}' after {timeout}s")

    # Add delay between commands for stability
    time.sleep(0.5)
    return response_str

# Basic AT test to ensure communication
def test_basic_at():
    print("\n=== Basic AT Test ===")
    
    # Try a few times in case module is still sending boot messages
    for attempt in range(5):
        response = send_at_command("AT", timeout=2)
        
        # Accept various valid responses from the module
        if any(keyword in response for keyword in ["OK", "RDY", "READY", "+CPIN"]):
            print("Module is responding - AT communication successful!")
            return True
            
        if attempt < 4:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2)  # Longer delay between attempts
    
    print("AT test failed after 5 attempts")
    return False

# Set SMS text mode
def set_sms_text_mode():
    print("\n=== Setting SMS Text Mode ===")
    response = send_at_command("AT+CMGF=1")
    
    if "OK" in response:
        print("SMS text mode set successfully")
        return True
    else:
        print("Failed to set SMS text mode")
        return False

# Send SMS message
def send_sms(phone_number, message):
    print(f"\n=== Sending SMS to {phone_number} ===")
    print(f"Message: {message}")
    
    # Start SMS command
    response = send_at_command(f'AT+CMGS="{phone_number}"', timeout=3)
    
    if ">" in response:
        print("SMS prompt received, sending message...")
        
        # Send the message text followed by Ctrl+Z (ASCII 26)
        uart.write(message)
        uart.write(bytes([26]))  # Ctrl+Z to end message
        
        # Wait for response (SMS sending can take a while)
        full_response_bytes = b""
        start_time = time.time()
        timeout = 30  # Extended timeout for SMS sending
        
        while (time.time() - start_time) < timeout:
            if uart.any():
                chunk = uart.read()
                if chunk:
                    full_response_bytes += chunk
            time.sleep(0.1)
        
        if full_response_bytes:
            try:
                response_str = full_response_bytes.decode('utf-8')
                print(f"SMS Response: {response_str.strip()}")
                
                if "+CMGS:" in response_str and "OK" in response_str:
                    print("SMS sent successfully!")
                    return True
                else:
                    print("SMS sending failed")
                    return False
            except UnicodeDecodeError:
                response_str = str(full_response_bytes)
                print(f"SMS Response (raw): {response_str}")
                return False
        else:
            print("No response received for SMS sending")
            return False
    else:
        print("Failed to get SMS prompt")
        return False

# Main SMS test function
def run_sms_test(phone_number, message):
    print("=== Starting SMS Test ===")
    
    # Basic connectivity test
    if not test_basic_at():
        print("ERROR: Basic AT communication failed!")
        return False
    
    # Set SMS text mode
    if not set_sms_text_mode():
        print("ERROR: Failed to set SMS text mode!")
        return False
    
    # Send the SMS
    if send_sms(phone_number, message):
        print("=== SMS Test Completed Successfully ===")
        return True
    else:
        print("=== SMS Test Failed ===")
        return False

# Usage example
if __name__ == "__main__":
    # Try to load environment variables from .env file
    load_env_file()
    
    print("Resetting and powering on SIM7600G...")
    reset_and_power_on_sim7600g()
    print("Waiting for module to boot...")
    time.sleep(5)
    
    # Get phone number from environment variable
    target_phone = getenv("TEST_PHONE_NUMBER")
    if not target_phone:
        print("ERROR: TEST_PHONE_NUMBER environment variable not set!")
        exit(1)
    
    test_message = "Hello from some random electronics on my desk!"
    
    print(f"Preparing to send SMS to: {target_phone}")
    print(f"Message: {test_message}")
    
    # Run the SMS test
    success = run_sms_test(target_phone, test_message)
    
    if success:
        print("\n✅ SMS test completed successfully!")
    else:
        print("\n❌ SMS test failed!") 