from machine import UART, Pin
import time

# Initialize UART for SIM7600G
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# Power control pins
power_key = Pin(2, Pin.OUT)
status_pin = Pin(3, Pin.IN)

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

# Basic AT test
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

# Get signal strength
def get_signal_strength():
    print("\n=== Signal Strength ===")
    response = send_at_command("AT+CSQ")
    return response

# Check network registration status
def check_network_registration():
    print("\n=== Network Registration Status ===")
    # Check 2G/3G registration
    response1 = send_at_command("AT+CREG?")
    # Check LTE registration
    response2 = send_at_command("AT+CEREG?")
    return response1, response2

# Get current network operator
def get_network_operator():
    print("\n=== Network Operator ===")
    response = send_at_command("AT+COPS?")
    return response

# Get serving cell information (LTE info)
def get_serving_cell_info():
    print("\n=== Serving Cell Info (LTE) ===")
    response = send_at_command("AT+CPSI?", timeout=3)
    return response

# Get SIM card IMSI (International Mobile Subscriber Identity)
def get_imsi():
    print("\n=== SIM Card IMSI ===")
    response = send_at_command("AT+CIMI")
    return response

# Get SIM card ICCID (SIM card serial number)
def get_iccid():
    print("\n=== SIM Card ICCID ===")
    response = send_at_command("AT+CCID")
    return response

# Get device IMEI
def get_imei():
    print("\n=== Device IMEI ===")
    response = send_at_command("AT+CGSN")
    return response

# Check SIM card status
def check_sim_status():
    print("\n=== SIM Card Status ===")
    response = send_at_command("AT+CPIN?")
    return response

# Get network attach status
def get_network_attach_status():
    print("\n=== Network Attach Status ===")
    response = send_at_command("AT+CGATT?")
    return response

# Comprehensive test function
def run_comprehensive_test():
    print("Starting comprehensive SIM7600G test...")

    # Basic connectivity test
    if not test_basic_at():
        print("ERROR: Basic AT communication failed!")
        return False
    
    # Check SIM card status
    check_sim_status()
    
    # Get identity information
    get_imsi()
    get_iccid()
    get_imei()
    
    # Check network connectivity
    get_signal_strength()
    check_network_registration()
    get_network_operator()
    get_network_attach_status()
    get_serving_cell_info()
    
    print("\n=== Test Complete ===")
    return True

# Usage
print("Resetting and powering on SIM7600G...")
reset_and_power_on_sim7600g()
print("Waiting for module to boot...")
time.sleep(5)

run_comprehensive_test()