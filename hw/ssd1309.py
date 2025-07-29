from machine import Pin, SPI
import framebuf
import time

# SSD1309 2.42" OLED Display Constants
OLED_WIDTH = 128
OLED_HEIGHT = 64

class SSD1309:
    def __init__(self, spi, dc, cs, rst, width=OLED_WIDTH, height=OLED_HEIGHT, rotation=0):
        """
        Initialize the SSD1309 OLED display with SPI interface
        
        Args:
            spi: SPI interface
            dc: Data/Command pin
            cs: Chip Select pin
            rst: Reset pin
            width: Display width in pixels
            height: Display height in pixels
            rotation: Display rotation (0, 90, 180, or 270 degrees)
        """
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.width = width
        self.height = height
        self.buffer = bytearray(self.width * self.height // 8)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        
        # Set rotation
        self.set_rotation(rotation)
        
        # Initialize display
        self.reset()
        self.init_display()
        
    def reset(self):
        """Reset the display"""
        self.rst.value(1)
        time.sleep(0.1)
        self.rst.value(0)
        time.sleep(0.1)
        self.rst.value(1)
        time.sleep(0.1)
        
    def set_rotation(self, rotation):
        """Set display rotation (0, 90, 180, or 270 degrees)"""
        self.rotation = rotation % 360
        
        # Validate rotation
        if self.rotation not in [0, 90, 180, 270]:
            self.rotation = 0  # Default to no rotation
            
        # Update effective dimensions based on rotation
        if self.rotation in [0, 180]:
            self.effective_width = self.width
            self.effective_height = self.height
        else:
            self.effective_width = self.height
            self.effective_height = self.width
            
    def get_effective_dimensions(self):
        """Return the effective drawing dimensions based on rotation"""
        return self.effective_width, self.effective_height
            
    def init_display(self):
        """Initialize the OLED display with required commands"""
        # Initialization commands for SSD1309
        init_commands = [
            0xAE,       # Display off
            0xD5, 0x80, # Set display clock divide ratio/oscillator frequency
            0xA8, 0x3F, # Set multiplex ratio (1/64)
            0xD3, 0x00, # Set display offset
            0x40,       # Set start line at line 0
            0x8D, 0x14, # Enable charge pump
            0x20, 0x00, # Set memory addressing mode (horizontal)
            0xA1,       # Set segment re-map (A0/A1)
            0xC8,       # Set COM output scan direction (C0/C8)
            0xDA, 0x12, # Set COM pins hardware configuration
            0x81, 0xCF, # Set contrast control
            0xD9, 0xF1, # Set pre-charge period
            0xDB, 0x40, # Set VCOMH deselect level
            0xA4,       # Display ON with RAM content
            0xA6,       # Normal display (not inverted)
            0xAF        # Display on
        ]
        
        # Send all initialization commands
        for cmd in init_commands:
            self.write_cmd(cmd)
            
        # Clear the display
        self.clear()
        
    def write_cmd(self, cmd):
        """Write a command to the display"""
        self.dc.value(0)  # Command mode
        self.cs.value(0)  # Select chip
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)  # Deselect chip
        
    def write_data(self, data):
        """Write data to the display"""
        self.dc.value(1)  # Data mode
        self.cs.value(0)  # Select chip
        self.spi.write(data)
        self.cs.value(1)  # Deselect chip
        
    def clear(self):
        """Clear the display buffer"""
        self.framebuf.fill(0)
        self.show()
        
    def show(self):
        """Update the display with current buffer contents"""
        # Set column and page address for the whole display
        self.write_cmd(0x21)  # Set column address
        self.write_cmd(0)     # Start column
        self.write_cmd(127)   # End column
        
        self.write_cmd(0x22)  # Set page address
        self.write_cmd(0)     # Start page
        self.write_cmd(7)     # End page
        
        # Apply rotation if needed
        if self.rotation == 0:
            # No rotation, send buffer directly
            self.write_data(self.buffer)
        else:
            # Apply rotation to buffer
            rotated_buffer = self._get_rotated_buffer()
            self.write_data(rotated_buffer)
            
    def _get_rotated_buffer(self):
        """Get a rotated copy of the buffer based on current rotation setting"""
        if self.rotation == 0:
            return self.buffer
            
        # Create a new buffer for the rotated content
        rotated_buffer = bytearray(self.width * self.height // 8)
        temp_framebuf = framebuf.FrameBuffer(rotated_buffer, self.width, self.height, framebuf.MONO_VLSB)
        
        # Copy pixel by pixel with rotation
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.framebuf.pixel(x, y)
                
                if self.rotation == 90:
                    # 90 degrees clockwise: (x,y) -> (y, width-1-x)
                    temp_framebuf.pixel(y, self.width - 1 - x, pixel)
                elif self.rotation == 180:
                    # 180 degrees: (x,y) -> (width-1-x, height-1-y)
                    temp_framebuf.pixel(self.width - 1 - x, self.height - 1 - y, pixel)
                elif self.rotation == 270:
                    # 270 degrees clockwise: (x,y) -> (height-1-y, x)
                    temp_framebuf.pixel(self.height - 1 - y, x, pixel)
                    
        return rotated_buffer
        
    def fill(self, color):
        """Fill the entire display with a color (0=black, 1=white)"""
        self.framebuf.fill(color)
        
    def pixel(self, x, y, color):
        """Set a pixel at (x,y) to the given color"""
        self.framebuf.pixel(x, y, color)
        
    def text(self, text, x, y, color):
        """Draw text at position (x,y) with the given color"""
        self.framebuf.text(text, x, y, color)
        
    def hline(self, x, y, width, color):
        """Draw a horizontal line"""
        self.framebuf.hline(x, y, width, color)
        
    def vline(self, x, y, height, color):
        """Draw a vertical line"""
        self.framebuf.vline(x, y, height, color)
        
    def line(self, x1, y1, x2, y2, color):
        """Draw a line from (x1,y1) to (x2,y2)"""
        self.framebuf.line(x1, y1, x2, y2, color)
        
    def rect(self, x, y, width, height, color):
        """Draw a rectangle outline"""
        self.framebuf.rect(x, y, width, height, color)
        
    def fill_rect(self, x, y, width, height, color):
        """Draw a filled rectangle"""
        self.framebuf.fill_rect(x, y, width, height, color)
        
    def scroll(self, dx, dy):
        """Scroll the display content by (dx,dy) pixels"""
        self.framebuf.scroll(dx, dy)
        
    def blit(self, fbuf, x, y, key=-1):
        """Copy another framebuffer to this display at position (x,y)"""
        self.framebuf.blit(fbuf, x, y, key)
        
    def invert(self, invert):
        """Invert the display (True=inverted, False=normal)"""
        self.write_cmd(0xA7 if invert else 0xA6)
        
    def contrast(self, level):
        """Set display contrast (0-255)"""
        self.write_cmd(0x81)
        self.write_cmd(level & 0xFF)
        
    def power_off(self):
        """Turn off the display"""
        self.write_cmd(0xAE)
        
    def power_on(self):
        """Turn on the display"""
        self.write_cmd(0xAF)
        
    def sleep(self):
        """Put display in sleep mode to save power"""
        self.power_off()
        
    def wake(self):
        """Wake display from sleep mode"""
        self.power_on()