from machine import Pin, I2C
import time

# I2C Configuration
I2C_SCL = Pin(21)  # I2C0 SCL
I2C_SDA = Pin(20)  # I2C0 SDA

def scan_i2c_bus(freq=100000):
    """Scan I2C bus at specified frequency"""
    print(f"\nScanning I2C bus at {freq//1000}kHz...")
    print("SDA: GP20 (Pin 26), SCL: GP21 (Pin 27)")
    
    try:
        i2c = I2C(0, scl=I2C_SCL, sda=I2C_SDA, freq=freq)
        devices = i2c.scan()
        
        print("     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F")
        for i in range(0, 128, 16):
            print(f"{i//16:02X}: ", end="")
            for j in range(16):
                addr = i + j
                if addr < 8 or addr > 119:  # Skip reserved addresses
                    print("   ", end="")
                elif addr in devices:
                    print(f"{addr:02X} ", end="")
                else:
                    print("-- ", end="")
            print()
        
        if devices:
            print(f"\nFound {len(devices)} device(s):")
            for addr in devices:
                device_name = "Unknown"
                if addr == 0x48:
                    device_name = "ADS1115 (ADDR=GND)"
                elif addr == 0x49:
                    device_name = "ADS1115 (ADDR=VDD)"
                elif addr == 0x4A:
                    device_name = "ADS1115 (ADDR=SDA)"
                elif addr == 0x4B:
                    device_name = "ADS1115 (ADDR=SCL)"
                elif addr in [0x3C, 0x3D]:
                    device_name = "OLED Display"
                elif addr in [0x68, 0x69]:
                    device_name = "RTC/MPU6050"
                elif addr == 0x76:
                    device_name = "BME280"
                
                print(f"  0x{addr:02X}: {device_name}")
        else:
            print("\nNo devices found!")
            print("Check:")
            print("- Wiring connections")
            print("- Power supply (5V for ADS1115)")
            print("- Pull-up resistors on SDA/SCL (4.7kΩ)")
            print("- Device power/enable pins")
        
        return devices
        
    except Exception as e:
        print(f"I2C scan failed: {e}")
        return []

def test_ads1115_specifically():
    """Test ADS1115 at all possible addresses"""
    print("\n=== ADS1115 Specific Test ===")
    
    # ADS1115 possible addresses based on ADDR pin
    ads_addresses = {
        0x48: "ADDR connected to GND",
        0x49: "ADDR connected to VDD", 
        0x4A: "ADDR connected to SDA",
        0x4B: "ADDR connected to SCL"
    }
    
    frequencies = [100000, 200000, 400000]
    
    for freq in frequencies:
        print(f"\nTesting at {freq//1000}kHz:")
        try:
            i2c = I2C(0, scl=I2C_SCL, sda=I2C_SDA, freq=freq)
            
            for addr, desc in ads_addresses.items():
                try:
                    # Try to read ADS1115 config register
                    data = i2c.readfrom_mem(addr, 0x01, 2)  # Config register
                    print(f"  0x{addr:02X}: ✓ FOUND - {desc}")
                    print(f"    Config: 0x{(data[0]<<8)|data[1]:04X}")
                    return addr, freq
                except:
                    print(f"  0x{addr:02X}: ✗ No response - {desc}")
        except Exception as e:
            print(f"  Error at {freq//1000}kHz: {e}")
    
    return None, None

def main():
    print("=== I2C Scanner and ADS1115 Diagnostic Tool ===")
    print("Hardware: Raspberry Pi Pico 2")
    print("I2C0: SDA=GP20 (Pin 26), SCL=GP21 (Pin 27)")
    print()
    
    # Test different frequencies
    frequencies = [100000, 200000, 400000]
    
    for freq in frequencies:
        devices = scan_i2c_bus(freq)
        if devices:
            break
        time.sleep(0.5)
    
    # Specific ADS1115 test
    addr, working_freq = test_ads1115_specifically()
    
    if addr and working_freq:
        print(f"\n✓ SUCCESS: ADS1115 found at 0x{addr:02X} using {working_freq//1000}kHz")
        print(f"Update your code:")
        print(f"  ADS1115_ADDR = 0x{addr:02X}")
        print(f"  i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq={working_freq})")
    else:
        print("\n✗ ADS1115 not found at any address or frequency")
        print("\nTroubleshooting steps:")
        print("1. Check power: VDD to 5V (Pin 40), GND to ground")
        print("2. Check I2C wires: SDA to GP20, SCL to GP21")
        print("3. Check ADDR pin: Connect to GND for address 0x48")
        print("4. Add pull-up resistors: 4.7kΩ on SDA and SCL to 3.3V")
        print("5. Verify ADS1115 module is working")
        print("6. Try lower frequency: 100kHz instead of 400kHz")

if __name__ == "__main__":
    main() 