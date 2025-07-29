import sys
sys.path.insert(0, '../../hw')
from ssd1309 import SSD1309 # type: ignore
from machine import Pin, SPI
import time

# SPI configuration for SSD1309 OLED display
SPI_SCK = 10    # SPI1 SCK - GP10 (Pin 14)
SPI_MOSI = 11   # SPI1 MOSI - GP11 (Pin 15) 
SPI_CS = 9      # Chip Select - GP9 (Pin 12)
SPI_DC = 12     # Data/Command - GP12 (Pin 16)
SPI_RST = 13    # Reset - GP13 (Pin 17)

# 5-Way Digital Navigation Joystick Pin Configuration
# COM pin is connected to GND. All pins are active low with internal pull-up.
joystick_pins = {
    'UP': Pin(18, Pin.IN, Pin.PULL_UP),
    'DOWN': Pin(19, Pin.IN, Pin.PULL_UP),
    'LEFT': Pin(4, Pin.IN, Pin.PULL_UP),
    'RIGHT': Pin(5, Pin.IN, Pin.PULL_UP),
    'MID': Pin(6, Pin.IN, Pin.PULL_UP),
    'SET': Pin(17, Pin.IN, Pin.PULL_UP),
    'RST': Pin(22, Pin.IN, Pin.PULL_UP),
}

class NavigationGrid:
    def __init__(self, oled, rows=3, cols=3, box_size=16, padding=4):
        self.oled = oled
        self.rows = rows
        self.cols = cols
        self.box_size = box_size
        self.padding = padding
        
        # Current position in the grid
        self.current_row = 0
        self.current_col = 0
        self.prev_row = 0
        self.prev_col = 0
        
        # Selected boxes (row, col)
        self.selected = set()
        self.prev_selected = set()
        
        # Calculate grid position to center it on screen
        width, height = oled.get_effective_dimensions()
        grid_width = cols * box_size + (cols - 1) * padding
        grid_height = rows * box_size + (rows - 1) * padding
        
        self.start_x = (width - grid_width) // 2
        self.start_y = (height - grid_height) // 2
        
    def get_box_position(self, row, col):
        """Get the top-left coordinates of a box in the grid"""
        x = self.start_x + col * (self.box_size + self.padding)
        y = self.start_y + row * (self.box_size + self.padding)
        return x, y
    
    def draw_grid(self):
        """Draw the entire grid"""
        # Clear display
        self.oled.fill(0)  # Black background
        
        # Draw title
        self.oled.text("Joystick Demo", 0, 0, 1)
        
        # Draw all boxes
        for row in range(self.rows):
            for col in range(self.cols):
                self.draw_box(row, col)
        
        # Update display
        self.oled.show()
    
    def draw_box(self, row, col):
        """Draw a single box with appropriate highlighting"""
        x, y = self.get_box_position(row, col)
        
        # Draw box outline
        self.oled.rect(x, y, self.box_size, self.box_size, 1)
        
        # Draw box number
        box_num = row * self.cols + col + 1
        text_x = x + (self.box_size - 8) // 2  # Center text (assuming 8px width)
        text_y = y + (self.box_size - 8) // 2  # Center text (assuming 8px height)
        
        # Highlight current position with inverted colors
        if row == self.current_row and col == self.current_col:
            self.oled.fill_rect(x+1, y+1, self.box_size-2, self.box_size-2, 1)
            self.oled.text(str(box_num), text_x, text_y, 0)  # Black text on white background
        else:
            # Draw number in white on black background
            self.oled.text(str(box_num), text_x, text_y, 1)
        
        # Mark selected boxes with a dot in the corner
        if (row, col) in self.selected:
            dot_size = 3
            self.oled.fill_rect(x + self.box_size - dot_size - 1, 
                               y + 1, 
                               dot_size, dot_size, 
                               0 if (row == self.current_row and col == self.current_col) else 1)
    
    def move(self, direction):
        """Move the current position based on joystick direction"""
        self.prev_row, self.prev_col = self.current_row, self.current_col
        
        if direction == 'UP' and self.current_row > 0:
            self.current_row -= 1
        elif direction == 'DOWN' and self.current_row < self.rows - 1:
            self.current_row += 1
        elif direction == 'LEFT' and self.current_col > 0:
            self.current_col -= 1
        elif direction == 'RIGHT' and self.current_col < self.cols - 1:
            self.current_col += 1
    
    def toggle_selection(self):
        """Toggle selection of current box"""
        self.prev_selected = self.selected.copy()
        pos = (self.current_row, self.current_col)
        if pos in self.selected:
            self.selected.remove(pos)
        else:
            self.selected.add(pos)

def get_joystick_input():
    """Get joystick input with debouncing"""
    states = {}
    for name, pin in joystick_pins.items():
        # Pins are active low, so not pin.value() is True when pressed
        states[name] = not pin.value()
    
    # Return the first pressed direction or button
    if states['UP']:
        return 'UP'
    elif states['DOWN']:
        return 'DOWN'
    elif states['LEFT']:
        return 'LEFT'
    elif states['RIGHT']:
        return 'RIGHT'
    elif states['MID']:
        return 'MID'
    elif states['SET']:
        return 'SET'
    elif states['RST']:
        return 'RST'
    else:
        return None

def draw_status(oled, message):
    """Draw status message at the bottom of the screen"""
    width, height = oled.get_effective_dimensions()
    
    # Clear status area
    oled.fill_rect(0, height - 10, width, 10, 0)
    
    # Draw message
    oled.text(message, 0, height - 8, 1)
    oled.show()

def menu_demo(oled):
    """Simple menu navigation demo"""
    width, height = oled.get_effective_dimensions()
    menu_items = ["Option 1", "Option 2", "Option 3", "Settings", "About", "Exit"]
    selected_item = 0
    
    while True:
        # Clear display
        oled.fill(0)
        
        # Draw title
        oled.text("Menu Demo", 0, 0, 1)
        oled.hline(0, 9, width, 1)
        
        # Draw menu items
        visible_items = min(5, len(menu_items))
        start_idx = max(0, min(selected_item - 2, len(menu_items) - visible_items))
        
        for i in range(visible_items):
            idx = start_idx + i
            if idx < len(menu_items):
                y_pos = 12 + i * 10
                
                # Highlight selected item
                if idx == selected_item:
                    oled.fill_rect(0, y_pos - 1, width, 10, 1)
                    oled.text(menu_items[idx], 2, y_pos, 0)
                else:
                    oled.text(menu_items[idx], 2, y_pos, 1)
        
        # Draw scrollbar if needed
        if len(menu_items) > visible_items:
            sb_height = int((visible_items / len(menu_items)) * height)
            sb_pos = int((start_idx / len(menu_items)) * height)
            oled.fill_rect(width - 3, sb_pos, 3, sb_height, 1)
        
        # Draw status
        oled.text("MID:Select RST:Exit", 0, height - 8, 1)
        
        # Update display
        oled.show()
        
        # Wait for input
        input_value = None
        while input_value is None:
            input_value = get_joystick_input()
            time.sleep(0.05)
        
        # Process input
        if input_value == 'UP' and selected_item > 0:
            selected_item -= 1
        elif input_value == 'DOWN' and selected_item < len(menu_items) - 1:
            selected_item += 1
        elif input_value == 'MID':
            # Show selection
            oled.fill(0)
            oled.text(f"Selected:", 0, 0, 1)
            oled.text(menu_items[selected_item], 0, 16, 1)
            oled.text("Press any button", 0, 32, 1)
            oled.text("to continue", 0, 40, 1)
            oled.show()
            
            # Wait for any button press
            while get_joystick_input() is not None:
                time.sleep(0.05)  # Wait for release
            while get_joystick_input() is None:
                time.sleep(0.05)  # Wait for press
        elif input_value == 'RST':
            return
        
        # Debounce
        while get_joystick_input() is not None:
            time.sleep(0.05)

def drawing_demo(oled):
    """Simple drawing demo using joystick"""
    width, height = oled.get_effective_dimensions()
    x, y = width // 2, height // 2
    drawing = False
    
    # Clear display
    oled.fill(0)
    oled.text("Drawing Demo", 0, 0, 1)
    oled.text("MID: Toggle draw", 0, height - 16, 1)
    oled.text("RST: Exit", 0, height - 8, 1)
    oled.show()
    
    while True:
        input_value = get_joystick_input()
        
        if input_value:
            if input_value == 'UP' and y > 0:
                y -= 1
            elif input_value == 'DOWN' and y < height - 1:
                y += 1
            elif input_value == 'LEFT' and x > 0:
                x -= 1
            elif input_value == 'RIGHT' and x < width - 1:
                x += 1
            elif input_value == 'MID':
                drawing = not drawing
                status = "Drawing ON" if drawing else "Drawing OFF"
                draw_status(oled, status)
            elif input_value == 'RST':
                return
            
            # Draw pixel if drawing is enabled
            if drawing:
                oled.pixel(x, y, 1)
            
            # Always draw cursor
            # XOR the cursor to make it visible on any background
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= x+i < width and 0 <= y+j < height:
                        if i == 0 and j == 0:
                            continue  # Skip center pixel if drawing
                        pixel_val = oled.framebuf.pixel(x+i, y+j)
                        oled.pixel(x+i, y+j, not pixel_val)
            
            oled.show()
            
            # Restore cursor pixels on next iteration
            if not drawing:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= x+i < width and 0 <= y+j < height:
                            if i == 0 and j == 0:
                                continue
                            pixel_val = oled.framebuf.pixel(x+i, y+j)
                            oled.pixel(x+i, y+j, not pixel_val)
        
        time.sleep(0.05)

def main():
    """Main test function"""
    print("SSD1309 OLED + Joystick Test")
    print("---------------------------")
    
    # Initialize SPI
    spi = SPI(1, baudrate=10000000, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI))
    dc = Pin(SPI_DC, Pin.OUT)
    cs = Pin(SPI_CS, Pin.OUT)
    rst = Pin(SPI_RST, Pin.OUT)
    
    # Initialize display
    try:
        oled = SSD1309(spi, dc, cs, rst, rotation=0)
        width, height = oled.get_effective_dimensions()
        print(f"Display initialized with dimensions: {width}x{height}")
    except Exception as e:
        print(f"Failed to initialize display: {e}")
        return
    
    try:
        # Welcome screen
        oled.fill(0)
        oled.text("Joystick + OLED", 0, 0, 1)
        oled.text("Test Program", 0, 10, 1)
        oled.text("Press any button", 0, 30, 1)
        oled.text("to start", 0, 40, 1)
        oled.show()
        
        # Wait for any button press
        while get_joystick_input() is None:
            time.sleep(0.1)
        
        # Debounce
        while get_joystick_input() is not None:
            time.sleep(0.05)
        
        # Grid navigation demo
        print("Starting grid navigation demo...")
        grid = NavigationGrid(oled, rows=4, cols=4)
        grid.draw_grid()
        
        last_input = None
        last_input_time = 0
        debounce_time = 0.2  # 200ms debounce
        
        # Show instructions
        draw_status(oled, "Use joystick to navigate")
        
        try:
            while True:
                current_time = time.time()
                input_value = get_joystick_input()
                
                # Process input with debouncing
                if input_value and (input_value != last_input or current_time - last_input_time > debounce_time):
                    last_input = input_value
                    last_input_time = current_time
                    
                    if input_value in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                        grid.move(input_value)
                        grid.draw_grid()
                        print(f"Moved {input_value} to position ({grid.current_row}, {grid.current_col})")
                    
                    elif input_value == 'MID':
                        grid.toggle_selection()
                        grid.draw_grid()
                        pos = (grid.current_row, grid.current_col)
                        status = "Selected" if pos in grid.selected else "Deselected"
                        print(f"{status} position ({grid.current_row}, {grid.current_col})")
                        draw_status(oled, f"{status} {grid.current_row+1},{grid.current_col+1}")
                    
                    elif input_value == 'SET':
                        # Switch to menu demo
                        print("Switching to menu demo...")
                        menu_demo(oled)
                        # Return to grid after menu demo
                        grid.draw_grid()
                        draw_status(oled, "Back to grid demo")
                    
                    elif input_value == 'RST':
                        # Switch to drawing demo
                        print("Switching to drawing demo...")
                        drawing_demo(oled)
                        # Return to grid after drawing demo
                        grid.draw_grid()
                        draw_status(oled, "Back to grid demo")
                
                # Small delay to prevent CPU hogging
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\nTest stopped by user.")
    
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    finally:
        # Clear display and put to sleep
        oled.fill(0)
        oled.text("Test ended", 0, 0, 1)
        oled.text("Goodbye!", 0, 10, 1)
        oled.show()
        time.sleep(1)
        oled.fill(0)
        oled.show()
        oled.sleep()
        print("Display cleared and put to sleep")

if __name__ == "__main__":
    main()