import sys
sys.path.insert(0, '../../hw')
from ssd1309 import SSD1309 # type: ignore
from machine import Pin, SPI
import time
import math

# SPI configuration for SSD1309 OLED display
SPI_SCK = 10    # SPI1 SCK - GP10 (Pin 14)
SPI_MOSI = 11   # SPI1 MOSI - GP11 (Pin 15) 
SPI_CS = 9      # Chip Select - GP9 (Pin 12)
SPI_DC = 12     # Data/Command - GP12 (Pin 16)
SPI_RST = 13    # Reset - GP13 (Pin 17)

def init_display(rotation=0):
    """Initialize the OLED display with specified rotation"""
    print(f"Initializing SSD1309 OLED display with {rotation}° rotation...")
    
    # Initialize SPI
    spi = SPI(1, baudrate=10000000, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI))
    dc = Pin(SPI_DC, Pin.OUT)
    cs = Pin(SPI_CS, Pin.OUT)
    rst = Pin(SPI_RST, Pin.OUT)
    
    # Initialize display
    try:
        oled = SSD1309(spi, dc, cs, rst, rotation=rotation)
        width, height = oled.get_effective_dimensions()
        print(f"Display initialized with dimensions: {width}x{height}")
        return oled
    except Exception as e:
        print(f"Failed to initialize display: {e}")
        return None

def test_basic_drawing(oled):
    """Test basic drawing functions"""
    print("Testing basic drawing functions...")
    
    # Get dimensions
    width, height = oled.get_effective_dimensions()
    
    # Clear display
    oled.clear()
    
    # Draw text
    oled.text("SSD1309 Test", 0, 0, 1)
    oled.text("2.42\" OLED", 0, 10, 1)
    oled.text(f"{width}x{height}", 0, 20, 1)
    
    # Draw rectangle
    oled.rect(0, 30, width, height-30, 1)
    
    # Draw horizontal and vertical lines
    oled.hline(10, 40, width-20, 1)
    oled.vline(width//2, 30, height-30, 1)
    
    # Update display
    oled.show()
    time.sleep(2)

def test_rotation(oled):
    """Test display rotation"""
    for rotation in [0, 90, 180, 270]:
        print(f"Testing {rotation}° rotation...")
        
        # Set rotation
        oled.set_rotation(rotation)
        width, height = oled.get_effective_dimensions()
        
        # Clear display
        oled.fill(0)
        
        # Draw orientation indicators
        oled.text(f"Rot: {rotation}", 0, 0, 1)
        
        # Draw corner markers
        marker_size = 5
        # Top-left
        oled.fill_rect(0, 0, marker_size, marker_size, 1)
        # Top-right
        oled.fill_rect(width-marker_size, 0, marker_size, marker_size, 1)
        # Bottom-left
        oled.fill_rect(0, height-marker_size, marker_size, marker_size, 1)
        # Bottom-right
        oled.fill_rect(width-marker_size, height-marker_size, marker_size, marker_size, 1)
        
        # Draw arrows indicating orientation
        mid_x = width // 2
        mid_y = height // 2
        arrow_size = min(width, height) // 4
        
        # Draw arrow pointing right
        oled.line(mid_x - arrow_size//2, mid_y, mid_x + arrow_size//2, mid_y, 1)
        oled.line(mid_x + arrow_size//2 - 3, mid_y - 3, mid_x + arrow_size//2, mid_y, 1)
        oled.line(mid_x + arrow_size//2 - 3, mid_y + 3, mid_x + arrow_size//2, mid_y, 1)
        
        # Update display
        oled.show()
        time.sleep(2)

def test_graphics(oled):
    """Test more advanced graphics"""
    print("Testing graphics capabilities...")
    
    width, height = oled.get_effective_dimensions()
    
    # Clear display
    oled.fill(0)
    
    # Draw diagonal lines
    oled.line(0, 0, width-1, height-1, 1)
    oled.line(0, height-1, width-1, 0, 1)
    
    # Draw a circle (approximation using lines)
    center_x = width // 2
    center_y = height // 2
    radius = min(width, height) // 4
    
    for i in range(0, 360, 15):  # Draw a point every 15 degrees
        angle_rad = i * 3.14159 / 180
        x = center_x + int(radius * math.cos(angle_rad))
        y = center_y + int(radius * math.sin(angle_rad))
        oled.line(center_x, center_y, x, y, 1)
    
    oled.show()
    time.sleep(2)
    
    # Bouncing ball animation
    oled.fill(0)
    x, y = width // 2, height // 2
    dx, dy = 1, 1
    ball_size = 5
    
    print("Running bouncing ball animation (press Ctrl+C to stop)...")
    try:
        for _ in range(100):  # Run for 100 frames
            # Clear previous ball position
            oled.fill(0)
            
            # Draw border
            oled.rect(0, 0, width, height, 1)
            
            # Update ball position
            x += dx
            y += dy
            
            # Bounce off edges
            if x <= 0 or x >= width - ball_size:
                dx = -dx
            if y <= 0 or y >= height - ball_size:
                dy = -dy
            
            # Draw ball
            oled.fill_rect(x, y, ball_size, ball_size, 1)
            
            # Update display
            oled.show()
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Animation stopped")

def test_text_scrolling(oled):
    """Test text scrolling"""
    print("Testing text scrolling...")
    
    width, height = oled.get_effective_dimensions()
    oled.fill(0)
    
    # Create a long message
    message = "SSD1309 OLED Display - Scrolling Text Demo"
    
    # Calculate total width of message
    msg_width = len(message) * 8  # Assuming 8 pixels per character
    
    # Scroll the text from right to left
    for i in range(width, -msg_width, -1):
        oled.fill(0)
        oled.text(message, i, height // 2 - 4, 1)
        oled.show()
        time.sleep(0.05)
    
    time.sleep(1)

def main():
    """Main test function"""
    print("SSD1309 OLED Display Test")
    print("------------------------")
    
    # Initialize with default rotation (0 degrees)
    oled = init_display(rotation=0)
    if not oled:
        print("Failed to initialize display. Exiting.")
        return
    
    try:
        # Run tests
        test_basic_drawing(oled)
        test_rotation(oled)
        test_graphics(oled)
        test_text_scrolling(oled)
        
        # Final message
        oled.fill(0)
        oled.text("Test Complete", 0, 0, 1)
        oled.text("Press Ctrl+C", 0, 20, 1)
        oled.text("to exit", 0, 30, 1)
        oled.show()
        
        # Keep display on until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    finally:
        # Clear display and put to sleep
        oled.fill(0)
        oled.show()
        oled.sleep()
        print("Display cleared and put to sleep")

if __name__ == "__main__":
    main()