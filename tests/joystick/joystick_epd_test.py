import sys
sys.path.insert(0, '../../hw')
from epd import EPD_4in2_B # type: ignore
from machine import Pin
import time

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
    def __init__(self, epd, rows=3, cols=3, box_size=60, padding=20):
        self.epd = epd
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
        width, height = epd.get_effective_dimensions()
        grid_width = cols * box_size + (cols - 1) * padding
        grid_height = rows * box_size + (rows - 1) * padding
        
        self.start_x = (width - grid_width) // 2
        self.start_y = (height - grid_height) // 2
        
        # Track full refresh counter for ghosting prevention
        self.partial_refresh_count = 0
        self.max_partial_refreshes = 10  # Do a full refresh after this many partial refreshes
    
    def get_box_position(self, row, col):
        """Get the top-left coordinates of a box in the grid"""
        x = self.start_x + col * (self.box_size + self.padding)
        y = self.start_y + row * (self.box_size + self.padding)
        return x, y
    
    def draw_grid(self, force_full_refresh=False):
        """Draw the entire grid"""
        # Determine if we need a full refresh
        need_full_refresh = force_full_refresh or self.partial_refresh_count >= self.max_partial_refreshes
        
        if need_full_refresh:
            # Clear display buffers
            self.epd.imageblack.fill(0xff)  # White background
            self.epd.imagered.fill(0xff)    # White background
            
            # Draw title
            self.epd.imageblack.text("Joystick Navigation Demo", 10, 10, 0x00)
            self.epd.imageblack.text("Use joystick to navigate", 10, 30, 0x00)
            self.epd.imageblack.text("Press MID to select/deselect", 10, 50, 0x00)
            
            # Draw all boxes
            for row in range(self.rows):
                for col in range(self.cols):
                    self.draw_box(row, col)
            
            # Update display with full refresh
            self.epd.EPD_4IN2B_Display()
            self.partial_refresh_count = 0
            print("Full refresh performed")
        else:
            # Only update the boxes that changed
            self.update_changed_boxes()
            self.partial_refresh_count += 1
    
    def update_changed_boxes(self):
        """Update only the boxes that have changed state"""
        # Update previous position if it changed
        if self.prev_row != self.current_row or self.prev_col != self.current_col:
            self.draw_box_partial(self.prev_row, self.prev_col)
            self.draw_box_partial(self.current_row, self.current_col)
            self.prev_row, self.prev_col = self.current_row, self.current_col
        
        # Update any boxes whose selection state changed
        changed_boxes = self.selected.symmetric_difference(self.prev_selected)
        for row, col in changed_boxes:
            self.draw_box_partial(row, col)
        
        self.prev_selected = self.selected.copy()
    
    def draw_box(self, row, col):
        """Draw a single box with appropriate highlighting (for full refresh)"""
        x, y = self.get_box_position(row, col)
        
        # Draw box outline
        self.epd.imageblack.rect(x, y, self.box_size, self.box_size, 0x00)
        
        # Draw box number
        box_num = row * self.cols + col + 1
        text_x = x + (self.box_size - 8) // 2  # Center text (assuming 8px width)
        text_y = y + (self.box_size - 8) // 2  # Center text (assuming 8px height)
        self.epd.imageblack.text(str(box_num), text_x, text_y, 0x00)
        
        # Highlight current position
        if row == self.current_row and col == self.current_col:
            # Highlight with black background
            self.epd.imageblack.fill_rect(x+2, y+2, self.box_size-4, self.box_size-4, 0x00)
            # Draw number in white
            self.epd.imageblack.text(str(box_num), text_x, text_y, 0xff)
        
        # Highlight selected boxes with red
        if (row, col) in self.selected:
            self.epd.imagered.fill_rect(x+2, y+2, self.box_size-4, self.box_size-4, 0x00)
            # Draw number in white (need to clear it in black layer)
            self.epd.imageblack.text(str(box_num), text_x, text_y, 0xff)
    
    def draw_box_partial(self, row, col):
        """Draw a single box with partial refresh"""
        x, y = self.get_box_position(row, col)
        
        # Create temporary buffers for this box area
        # Make sure dimensions are aligned to 8 pixels for partial refresh
        box_width = ((self.box_size + 7) // 8) * 8
        box_height = ((self.box_size + 7) // 8) * 8
        
        # Clear the box area in both buffers
        self.epd.imageblack.fill_rect(x, y, box_width, box_height, 0xff)  # White background
        self.epd.imagered.fill_rect(x, y, box_width, box_height, 0xff)    # White background
        
        # Draw box outline
        self.epd.imageblack.rect(x, y, self.box_size, self.box_size, 0x00)
        
        # Draw box number
        box_num = row * self.cols + col + 1
        text_x = x + (self.box_size - 8) // 2
        text_y = y + (self.box_size - 8) // 2
        self.epd.imageblack.text(str(box_num), text_x, text_y, 0x00)
        
        # Highlight current position
        if row == self.current_row and col == self.current_col:
            self.epd.imageblack.fill_rect(x+2, y+2, self.box_size-4, self.box_size-4, 0x00)
            self.epd.imageblack.text(str(box_num), text_x, text_y, 0xff)
        
        # Highlight selected boxes with red
        if (row, col) in self.selected:
            self.epd.imagered.fill_rect(x+2, y+2, self.box_size-4, self.box_size-4, 0x00)
            self.epd.imageblack.text(str(box_num), text_x, text_y, 0xff)
        
        # Perform partial refresh for just this box
        # Ensure x and width are multiples of 8 for proper partial refresh
        aligned_x = (x // 8) * 8
        aligned_width = ((box_width + 7) // 8) * 8
        
        # Create a partial window and display
        self.epd.set_partial_window(aligned_x, y, aligned_width, box_height)
        self.epd.display_partial()
    
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

def main():
    print("Initializing E-Paper Display...")
    # Initialize display in portrait mode (90 degree rotation)
    epd = EPD_4in2_B(rotation=90)
    
    print("Creating navigation grid...")
    grid = NavigationGrid(epd, rows=3, cols=3)
    
    print("Drawing initial grid...")
    grid.draw_grid(force_full_refresh=True)  # Initial draw is always a full refresh
    
    print("Ready for joystick input!")
    print("Use joystick to navigate, press MID to select/deselect")
    
    last_input = None
    last_input_time = 0
    debounce_time = 0.2  # 200ms debounce
    last_full_refresh_time = time.time()
    full_refresh_interval = 60  # Do a full refresh every 60 seconds to prevent ghosting
    
    try:
        while True:
            current_time = time.time()
            input_value = get_joystick_input()
            
            # Check if we need a periodic full refresh
            force_full = (current_time - last_full_refresh_time) > full_refresh_interval
            if force_full:
                print("Performing periodic full refresh to prevent ghosting")
                grid.draw_grid(force_full_refresh=True)
                last_full_refresh_time = current_time
            
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
                
                elif input_value == 'RST':
                    print("Resetting selections...")
                    grid.selected.clear()
                    grid.draw_grid(force_full_refresh=True)
                    last_full_refresh_time = current_time
            
            # Small delay to prevent CPU hogging
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        epd.EPD_4IN2B_Clear()
        epd.Sleep()
        print("Display cleared and put to sleep.")

if __name__ == "__main__":
    main() 