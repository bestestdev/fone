import sys
sys.path.insert(0, '../../hw')
from epd import EPD_4in2_B # type: ignore

def test_rotation(rotation_angle):
    """Test display with a specific rotation"""
    print(f"\n=== Testing {rotation_angle} degree rotation ===")
    
    # Ensure rotation_angle is an integer
    rotation_angle = int(rotation_angle)
    print(f"DEBUG: Using rotation angle: {rotation_angle}, type: {type(rotation_angle)}")
    
    # Initialize with rotation
    epd = EPD_4in2_B(rotation=rotation_angle)
    width, height = epd.get_effective_dimensions()
    print(f"Effective dimensions: {width}x{height}")
    
    # Clear buffers
    epd.imageblack.fill(0xff)  # White background
    epd.imagered.fill(0xff)    # White background
    
    # Draw simple test patterns
    # Draw a border
    epd.imageblack.rect(0, 0, width, height, 0x00)  # Black border around the edge
    
    # Draw text
    epd.imageblack.text(f"Rotation: {rotation_angle} deg", 20, 20, 0x00)
    epd.imageblack.text(f"Size: {width}x{height}", 20, 40, 0x00)
    
    # Draw orientation markers at corners
    marker_size = 10
    # Top-left (black)
    epd.imageblack.fill_rect(5, 5, marker_size, marker_size, 0x00)
    
    # Top-right (red)
    epd.imagered.fill_rect(width - marker_size - 5, 5, marker_size, marker_size, 0x00)
    
    # Bottom-left (red)
    epd.imagered.fill_rect(5, height - marker_size - 5, marker_size, marker_size, 0x00)
    
    # Bottom-right (black)
    epd.imageblack.fill_rect(width - marker_size - 5, height - marker_size - 5, marker_size, marker_size, 0x00)
    
    # Draw crossing lines
    line_thickness = 2
    # Vertical line (black)
    epd.imageblack.fill_rect(width // 2 - line_thickness // 2, 0, line_thickness, height, 0x00)
    
    # Horizontal line (red)
    epd.imagered.fill_rect(0, height // 2 - line_thickness // 2, width, line_thickness, 0x00)
    
    # Display the result
    epd.EPD_4IN2B_Display()
    epd.delay_ms(3000)  # Show for 3 seconds
    return epd

def test_dynamic_rotation():
    """Test changing rotation dynamically"""
    print("\n=== Testing dynamic rotation changes ===")
    
    # Start with 0° rotation
    epd = EPD_4in2_B(rotation=0)
    
    rotations = [0, 90, 180, 270]
    
    for rotation in rotations:
        print(f"Switching to {rotation} degree rotation...")
        epd.set_rotation(rotation)
        width, height = epd.get_effective_dimensions()
        
        # Clear and draw new content
        epd.imageblack.fill(0xff)
        epd.imagered.fill(0xff)
        
        epd.imageblack.text(f"Dynamic: {rotation} deg", 10, 10, 0x00)
        epd.imagered.text(f"{width}x{height}", 10, 30, 0x00)
        
        # Draw corner markers to show orientation
        epd.imageblack.rect(0, 0, 10, 10, 0x00)  # Top-left
        epd.imagered.rect(width-10, height-10, 10, 10, 0x00)  # Bottom-right
        
        epd.EPD_4IN2B_Display()
        epd.delay_ms(2000)
    
    return epd

def test_original_functionality():
    """Test that all original functionality still works"""
    print("\n=== Testing original functionality (0° rotation) ===")
    
    epd = EPD_4in2_B(rotation=0)  # Default landscape
    
    # Your original test code
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0xff)
    
    epd.imageblack.text("Waveshare", 5, 10, 0x00)
    epd.imagered.text("Pico_ePaper-4.2-B", 5, 40, 0x00)
    epd.imageblack.text("Raspberry Pico", 5, 70, 0x00)
    epd.EPD_4IN2B_Display()
    epd.delay_ms(3000)
    
    epd.imageblack.vline(10, 90, 60, 0x00)
    epd.imagered.vline(90, 90, 60, 0x00)
    epd.imageblack.hline(10, 90, 80, 0x00)
    epd.imagered.hline(10, 150, 80, 0x00)
    epd.imageblack.line(10, 90, 90, 150, 0x00)
    epd.imagered.line(90, 90, 10, 150, 0x00)
    epd.EPD_4IN2B_Display()
    epd.delay_ms(3000)
    
    epd.imageblack.rect(10, 180, 50, 80, 0x00)
    epd.imagered.fill_rect(70, 180, 50, 80, 0x00)
    epd.EPD_4IN2B_Display()
    epd.delay_ms(3000)
    
    return epd

def test_portrait_mode():
    """Test portrait mode (90° rotation) with content designed for portrait"""
    print("\n=== Testing portrait mode ===")
    
    epd = EPD_4in2_B(rotation=90)  # Portrait mode
    width, height = epd.get_effective_dimensions()  # Should be 300x400
    
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0xff)
    
    # Portrait-oriented content
    epd.imageblack.text("PORTRAIT MODE", 10, 10, 0x00)
    epd.imagered.text("300x400 pixels", 10, 30, 0x00)
    
    # Vertical menu-style layout
    menu_items = ["Option 1", "Option 2", "Option 3", "Option 4"]
    for i, item in enumerate(menu_items):
        y_pos = 60 + i * 25
        epd.imageblack.text(f"{i+1}. {item}", 20, y_pos, 0x00)
        epd.imageblack.hline(20, y_pos + 15, width - 40, 0x00)
    
    # Side border
    epd.imagered.vline(width - 20, 50, height - 100, 0x00)
    
    # Bottom status area
    epd.imagered.text("Status: Ready", 10, height - 30, 0x00)
    epd.imageblack.hline(10, height - 40, width - 20, 0x00)
    
    epd.EPD_4IN2B_Display()
    epd.delay_ms(5000)
    
    return epd

if __name__ == "__main__":
    print("Starting rotation tests...")
    
    try:
        # Debug rotation mapping
        print("\n=== Testing rotation mapping ===")
        epd = EPD_4in2_B(rotation=0)
        print("\nMapping for 90° rotation:")
        epd.debug_rotation_mapping(90)
        print("\nMapping for 270° rotation:")
        epd.debug_rotation_mapping(270)
        
        # Test 90-degree rotation
        print("\n=== Testing 90 degree rotation with simple pattern ===")
        epd = test_rotation(90)
        epd.EPD_4IN2B_Clear()
        
        # Test 270-degree rotation
        print("\n=== Testing 270 degree rotation with simple pattern ===")
        epd = test_rotation(270)
        epd.EPD_4IN2B_Clear()
        
        epd.Sleep()
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import sys
        sys.print_exception(e)  # Print full exception traceback

# Quick usage examples:
"""
# Example 1: Create display in portrait mode
epd = EPD_4in2_B(rotation=90)
epd.imageblack.text("Portrait!", 10, 10, 0x00)
epd.EPD_4IN2B_Display()

# Example 2: Change rotation dynamically
epd.set_rotation(180)  # Upside down
epd.imageblack.fill(0xff)
epd.imageblack.text("Upside down!", 10, 10, 0x00)
epd.EPD_4IN2B_Display()

# Example 3: Get current effective dimensions
width, height = epd.get_effective_dimensions()
print(f"Current canvas size: {width}x{height}")
"""