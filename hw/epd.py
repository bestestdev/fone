from machine import Pin, SPI
import utime
import framebuf

# 2.9" E-Paper Display Configuration - Landscape Mode (software rotated)
DISPLAY_WIDTH = 296  # Logical width (rotated)
DISPLAY_HEIGHT = 128  # Logical height (rotated)
PHYSICAL_WIDTH = 128   # Physical display width  
PHYSICAL_HEIGHT = 296  # Physical display height

# SPI1 Configuration for E-Paper Display
SPI_SCK = Pin(10)    # SPI1 SCK - GP10 (Pin 14)
SPI_MOSI = Pin(11)   # SPI1 MOSI - GP11 (Pin 15) 
SPI_CS = Pin(9)      # Chip Select - GP9 (Pin 12)
SPI_DC = Pin(12)     # Data/Command - GP12 (Pin 16)
SPI_RST = Pin(13)    # Reset - GP13 (Pin 17)
SPI_BUSY = Pin(14)   # Busy status - GP14 (Pin 19)

class EPD_2in9_B_V4_Landscape:
    def __init__(self):
        self.reset_pin = Pin(SPI_RST, Pin.OUT)
        
        self.busy_pin = Pin(SPI_BUSY, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(SPI_CS, Pin.OUT)
        # Use physical dimensions for the actual e-paper display
        if PHYSICAL_WIDTH % 8 == 0:
            self.width = PHYSICAL_WIDTH
        else :
            self.width = (PHYSICAL_WIDTH // 8) * 8 + 8
        self.height = PHYSICAL_HEIGHT
        
        # Logical dimensions for user applications
        self.logical_width = DISPLAY_WIDTH
        self.logical_height = DISPLAY_HEIGHT
        
        self.spi = SPI(1,baudrate=4000_000,sck=Pin(SPI_SCK),mosi=Pin(SPI_MOSI))
        self.dc_pin = Pin(SPI_DC, Pin.OUT)
        
        
        self.buffer_balck = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = framebuf.FrameBuffer(self.buffer_balck, self.width, self.height, framebuf.MONO_HLSB)
        self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)


    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        print('busy')
        while(self.digital_read(self.busy_pin) == 1): 
            self.delay_ms(10) 
        print('busy release')
        self.delay_ms(20)
        
    def TurnOnDisplay(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xF7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplay_Base(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xF4)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
        
    def TurnOnDisplay_Fast(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
        
    def TurnOnDisplay_Partial(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0x1C)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()


    def init(self):
        # EPD hardware init start
        self.reset()

        self.ReadBusy()   
        self.send_command(0x12)  #SWRESET
        self.ReadBusy()   

        self.send_command(0x01) #Driver output control      
        self.send_data((self.height-1)%256)    
        self.send_data((self.height-1)//256)
        self.send_data(0x00)

        self.send_command(0x11) #data entry mode       
        self.send_data(0x03)  # Portrait mode (hardware native)

        self.send_command(0x44) #set Ram-X address start/end position   
        self.send_data(0x00)
        self.send_data(self.width//8-1)   

        self.send_command(0x45) #set Ram-Y address start/end position          
        self.send_data(0x00)
        self.send_data(0x00) 
        self.send_data((self.height-1)%256)    
        self.send_data((self.height-1)//256)

        self.send_command(0x3C) #BorderWavefrom
        self.send_data(0x05)	

        self.send_command(0x21) #  Display update control
        self.send_data(0x00)		
        self.send_data(0x80)	

        self.send_command(0x18) #Read built-in temperature sensor
        self.send_data(0x80)	

        self.send_command(0x4E)   # set RAM x address count to 0
        self.send_data(0x00)
        self.send_command(0x4F)   # set RAM y address count to 0X199    
        self.send_data(0x00)    
        self.send_data(0x00)
        self.ReadBusy()
        
        return 0
    
    def init_Fast(self):
        # EPD hardware init start
        self.reset()

        self.ReadBusy()   
        self.send_command(0x12)  #SWRESET
        self.ReadBusy()   	

        self.send_command(0x18) #Read built-in temperature sensor
        self.send_data(0x80)

        self.send_command(0x22) # Load temperature value
        self.send_data(0xB1)		
        self.send_command(0x20)	
        self.ReadBusy()   

        self.send_command(0x1A) # Write to temperature register
        self.send_data(0x5a)		# 90		
        self.send_data(0x00)	
                    
        self.send_command(0x22) # Load temperature value
        self.send_data(0x91)		
        self.send_command(0x20)	
        self.ReadBusy()  

        self.send_command(0x01) #Driver output control      
        self.send_data((self.height-1)%256)    
        self.send_data((self.height-1)//256)
        self.send_data(0x00)

        self.send_command(0x11) #data entry mode       
        self.send_data(0x03)  # Portrait mode (hardware native)

        self.send_command(0x44) #set Ram-X address start/end position   
        self.send_data(0x00)
        self.send_data(self.width//8-1)   

        self.send_command(0x45) #set Ram-Y address start/end position          
        self.send_data(0x00)
        self.send_data(0x00) 
        self.send_data((self.height-1)%256)    
        self.send_data((self.height-1)//256)	

        self.send_command(0x4E)   # set RAM x address count to 0
        self.send_data(0x00)
        self.send_command(0x4F)   # set RAM y address count to 0X199    
        self.send_data(0x00)    
        self.send_data(0x00)
        self.ReadBusy()	
        
        return 0
    
    def display(self): # ryimage: red or yellow image
        self.send_command(0x24)
        self.send_data1(self.buffer_balck)

        self.send_command(0x26)
        self.send_data1(self.buffer_red)

        self.TurnOnDisplay()

    def display_Fast(self): # ryimage: red or yellow image
        self.send_command(0x24)
        self.send_data1(self.buffer_balck)

        self.send_command(0x26)
        self.send_data1(self.buffer_red)

        self.TurnOnDisplay_Fast()

    def Clear(self):
        self.send_command(0x24)
        self.send_data1([0xFF] * self.height * int(self.width / 8))
        
        self.send_command(0x26)
        self.send_data1([0x00] * self.height * int(self.width / 8))
                                
        self.TurnOnDisplay()

    def clear(self):
        """Clear both buffers (white background, no red)"""
        self.imageblack.fill(0xff)  # White background
        self.imagered.fill(0x00)    # No red
    
    def _rotate_coords(self, x, y):
        """Convert logical landscape coordinates to physical portrait coordinates"""
        # Rotate 90 degrees counterclockwise: (x,y) -> (y, width-1-x)
        physical_x = y
        physical_y = self.logical_width - 1 - x
        return physical_x, physical_y
    
    def text(self, string, x, y, color='black'):
        """Draw text in landscape orientation"""
        buffer = self.imageblack if color == 'black' else self.imagered
        pixel_color = 0x00 if color == 'black' else 0xff
        
        # For now, draw text rotated character by character
        # This is a simple approach - for better results you'd need font rotation
        char_width = 8
        char_height = 8
        
        for i, char in enumerate(string):
            char_x = x + i * char_width
            if char_x >= self.logical_width:
                break
                
            # Draw each character pixel by pixel (rotated)
            # For simplicity, let's use the original text method on rotated coords
            # Note: This will make text appear rotated, but readable in landscape
            px, py = self._rotate_coords(char_x, y)
            if 0 <= px < self.width and 0 <= py < self.height:
                # Use a simple approach: draw the character normally but in rotated position
                buffer.text(char, px - 4, py - 4, pixel_color)

    def draw_crosshair(self, x, y, size=6, color='black'):
        """Draw a crosshair at the specified position (using logical landscape coordinates)"""
        buffer = self.imageblack if color == 'black' else self.imagered
        pixel_color = 0x00 if color == 'black' else 0xff
        
        # Ensure coordinates are within logical bounds
        x = max(size, min(self.logical_width - size - 1, x))
        y = max(size, min(self.logical_height - size - 1, y))
        
        # Simplified crosshair - just draw the essential parts for speed
        # Center point
        px, py = self._rotate_coords(x, y)
        if 0 <= px < self.width and 0 <= py < self.height:
            buffer.pixel(px, py, pixel_color)
        
        # Horizontal line (reduced size for speed)
        for i in range(-size//2, size//2 + 1, 2):  # Step by 2 for speed
            px, py = self._rotate_coords(x + i, y)
            if 0 <= px < self.width and 0 <= py < self.height:
                buffer.pixel(px, py, pixel_color)
        
        # Vertical line (reduced size for speed)
        for i in range(-size//2, size//2 + 1, 2):  # Step by 2 for speed
            px, py = self._rotate_coords(x, y + i)
            if 0 <= px < self.width and 0 <= py < self.height:
                buffer.pixel(px, py, pixel_color)

    def clear_crosshair_area(self, x, y, size=6):
        """Clear the area where a crosshair was drawn"""
        # Clear both buffers in the crosshair area
        for dx in range(-size//2-1, size//2+2):
            for dy in range(-size//2-1, size//2+2):
                px, py = self._rotate_coords(x + dx, y + dy)
                if 0 <= px < self.width and 0 <= py < self.height:
                    self.imageblack.pixel(px, py, 0xff)  # White
                    self.imagered.pixel(px, py, 0x00)    # No red

    def update_crosshair_partial(self, old_x, old_y, new_x, new_y, size=6, color='black'):
        """Update crosshair position using partial display updates"""
        margin = 5
        
        if old_x >= 0 and old_y >= 0:  # Clear old position if valid
            # Calculate physical coordinates for old position
            old_px, old_py = self._rotate_coords(old_x, old_y)
            
            # Clear old crosshair area
            self.clear_crosshair_area(old_x, old_y, size)
            
            # Partial update for old area (clear it)
            x_start = max(0, old_px - size - margin)
            x_end = min(self.width - 1, old_px + size + margin)
            y_start = max(0, old_py - size - margin)
            y_end = min(self.height - 1, old_py + size + margin)
            
            self._partial_update_area(x_start, y_start, x_end, y_end)
        
        # Draw new crosshair
        self.draw_crosshair(new_x, new_y, size, color)
        
        # Calculate physical coordinates for new position
        new_px, new_py = self._rotate_coords(new_x, new_y)
        
        # Partial update for new area
        x_start = max(0, new_px - size - margin)
        x_end = min(self.width - 1, new_px + size + margin)
        y_start = max(0, new_py - size - margin) 
        y_end = min(self.height - 1, new_py + size + margin)
        
        self._partial_update_area(x_start, y_start, x_end, y_end)

    def _partial_update_area(self, x_start, y_start, x_end, y_end):
        """Perform a partial update on a specific area of the display"""
        # Ensure coordinates are byte-aligned for the display
        x_start_byte = x_start // 8
        x_end_byte = (x_end + 7) // 8
        
        # Set up partial update window
        self.send_command(0x44)  # Set RAM X start/end
        self.send_data(x_start_byte & 0xff)
        self.send_data((x_end_byte - 1) & 0xff)
        
        self.send_command(0x45)  # Set RAM Y start/end  
        self.send_data(y_start & 0xff)
        self.send_data((y_start >> 8) & 0x01)
        self.send_data(y_end & 0xff)
        self.send_data((y_end >> 8) & 0x01)
        
        self.send_command(0x4E)  # Set RAM X counter
        self.send_data(x_start_byte & 0xff)
        self.send_command(0x4F)  # Set RAM Y counter
        self.send_data(y_start & 0xff)
        self.send_data((y_start >> 8) & 0x01)
        
        # Send partial image data
        self.send_command(0x24)  # Write black data
        for y in range(y_start, y_end + 1):
            for x_byte in range(x_start_byte, x_end_byte):
                if x_byte < len(self.buffer_balck) // self.height:
                    idx = y * (self.width // 8) + x_byte
                    if idx < len(self.buffer_balck):
                        self.send_data(self.buffer_balck[idx])
        
        self.send_command(0x26)  # Write red data
        for y in range(y_start, y_end + 1):
            for x_byte in range(x_start_byte, x_end_byte):
                if x_byte < len(self.buffer_red) // self.height:
                    idx = y * (self.width // 8) + x_byte
                    if idx < len(self.buffer_red):
                        self.send_data(self.buffer_red[idx])
        
        # Trigger partial update
        self.TurnOnDisplay_Partial()

    def display_partial(self, Image, Xstart, Ystart, Xend, Yend):
        if((Xstart % 8 + Xend % 8 == 8 & Xstart % 8 > Xend % 8) | Xstart % 8 + Xend % 8 == 0 | (Xend - Xstart)%8 == 0):
            Xstart = Xstart // 8
            Xend = Xend // 8
        else:
            Xstart = Xstart // 8 
            if Xend % 8 == 0:
                Xend = Xend // 8
            else:
                Xend = Xend // 8 + 1
                
        if(self.width % 8 == 0):
            Width = self.width // 8
        else:
            Width = self.width // 8 +1
        Height = self.height

        Xend -= 1
        Yend -= 1
	
        self.send_command(0x44)       # set RAM x address start/end, in page 35
        self.send_data(Xstart & 0xff)    # RAM x address start at 00h
        self.send_data(Xend & 0xff)    # RAM x address end at 0fh(15+1)*8->128 
        self.send_command(0x45)       # set RAM y address start/end, in page 35
        self.send_data(Ystart & 0xff)    # RAM y address start at 0127h
        self.send_data((Ystart>>8) & 0x01)    # RAM y address start at 0127h
        self.send_data(Yend & 0xff)    # RAM y address end at 00h
        self.send_data((Yend>>8) & 0x01)   

        self.send_command(0x4E)   # set RAM x address count to 0
        self.send_data(Xstart & 0xff)
        self.send_command(0x4F)   # set RAM y address count to 0X127    
        self.send_data(Ystart & 0xff)
        self.send_data((Ystart>>8) & 0x01)

        self.send_command(0x24)   #Write Black and White image to RAM
        for j in range(Height):
            for i in range(Width):
                if((j > Ystart-1) & (j < (Yend + 1)) & (i > Xstart-1) & (i < (Xend + 1))):
                    self.send_data(Image[i + j * Width])
        self.TurnOnDisplay_Partial()

    def sleep(self):
        self.send_command(0x10) 
        self.send_data(0x01)
        
        self.delay_ms(2000)
        self.module_exit() 