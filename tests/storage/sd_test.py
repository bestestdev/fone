import sys
sys.path.insert(0, '../../hw')
from machine import Pin, SPI, SDCard
import os
import vfs

def test_sd_card():
    # Initialize SD card using machine.SDCard
    # For Raspberry Pi Pico, we use SPI mode with custom pins
    sd = SDCard(
        slot=2,           # SPI mode slot
        sck=Pin(10),      # GP10 - shared with display
        mosi=Pin(11),     # GP11 - shared with display  
        miso=Pin(8),      # GP8 - SD card only
        cs=Pin(7)         # GP7 - SD card CS
    )
    
    # Mount filesystem using vfs
    vfs.mount(sd, '/sd')
    
    # Test file operations
    test_file = '/sd/test.txt'
    test_data = 'Hello from fone!\n'
    
    try:
        # Try to read existing file
        try:
            with open(test_file, 'r') as f:
                content = f.read()
                print('Existing content:', content)
        except:
            print('File does not exist, will create it')
            content = ''
        
        # Append new data
        with open(test_file, 'a') as f:
            f.write(test_data)
        
        # Read back the file
        with open(test_file, 'r') as f:
            final_content = f.read()
            print('Final content:', final_content)
            
    finally:
        # Unmount filesystem
        vfs.umount('/sd')

if __name__ == '__main__':
    test_sd_card() 