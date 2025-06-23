# *****************************************************************************
# * | File        :	  Pico_ePaper-4.2-B-Rotated.py
# * | Author      :   Enhanced with rotation support
# * | Function    :   Electronic paper driver with rotation capabilities
# * | Info        :
# *----------------
# * | This version:   V1.1 - Added rotation support
# * | Date        :   2023-06-23
# # | Info        :   Enhanced python demo with rotation
# *
# * Features:
# * - Support for 0°, 90°, 180°, and 270° rotation
# * - Automatic buffer handling for different orientations
# * - Maintains compatibility with original driver
# * - Efficient memory usage with proper buffer alignment
# * - Portrait and landscape modes
# *
# * Usage:
# * - Initialize with rotation: epd = EPD_4in2_B(rotation=90)
# * - Change rotation dynamically: epd.set_rotation(180)
# * - Get current dimensions: width, height = epd.get_effective_dimensions()
# *
# * Note: When using 90° or 270° rotation, width and height are swapped
# -----------------------------------------------------------------------------

from machine import Pin, SPI
import framebuf
import utime

# Display resolution
EPD_WIDTH       = 400
EPD_HEIGHT      = 300

# pins
SPI_SCK = Pin(10)    # SPI1 SCK - GP10 (Pin 14)
SPI_MOSI = Pin(11)   # SPI1 MOSI - GP11 (Pin 15) 
SPI_CS = Pin(9)      # Chip Select - GP9 (Pin 12)
SPI_DC = Pin(12)     # Data/Command - GP12 (Pin 16)
SPI_RST = Pin(13)    # Reset - GP13 (Pin 17)
SPI_BUSY = Pin(27)   # Busy status - GP27 (Pin 32)


class EPD_4in2_B:
    def __init__(self, rotation=0):
        """
        Initialize EPD with optional rotation
        rotation: 0, 90, 180, or 270 degrees
        """
        self.reset_pin = Pin(SPI_RST, Pin.OUT)
        self.busy_pin = Pin(SPI_BUSY, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(SPI_CS, Pin.OUT)
        self.sck_pin = 1
        self.din_pin = 1
        
        # Hardware dimensions (always 400x300)
        self.hw_width = EPD_WIDTH
        self.hw_height = EPD_HEIGHT
        
        # Set rotation and calculate effective dimensions
        # Ensure rotation is an integer
        try:
            rotation = int(rotation)
        except (ValueError, TypeError):
            rotation = 0  # Default to 0 if conversion fails
            
        self.rotation = rotation % 360
        
        # Check if rotation is one of the valid values
        valid_rotations = [0, 90, 180, 270]
        if self.rotation not in valid_rotations:
            # Round to nearest valid rotation instead of raising an error
            closest = min(valid_rotations, key=lambda x: abs(x - self.rotation))
            self.rotation = closest
        
        # Effective dimensions after rotation
        if self.rotation % 180 == 0:
            self.width = self.hw_width   # 400
            self.height = self.hw_height # 300
        else:
            self.width = self.hw_height  # 300 
            self.height = self.hw_width  # 400
        
        self.flag = 0
        
        self.spi = SPI(1,baudrate=4000_000,sck=Pin(SPI_SCK),mosi=Pin(SPI_MOSI))
        self.dc_pin = Pin(SPI_DC, Pin.OUT)
        
        # Create working framebuffers based on effective dimensions
        # Calculate buffer size - ensure it's a multiple of 8 bytes for proper alignment
        stride = (self.width + 7) // 8  # Bytes per row, rounded up
        buffer_size = stride * self.height
        
        try:
            # Create bytearrays
            self.buffer_black = bytearray(buffer_size)
            self.buffer_red = bytearray(buffer_size)
            
            # Create framebuffers - use MONO_HLSB format (1 bit per pixel, horizontal)
            try:
                self.imageblack = framebuf.FrameBuffer(self.buffer_black, self.width, self.height, framebuf.MONO_HLSB)
            except Exception:
                # Try alternate constructor format
                self.imageblack = framebuf.FrameBuffer(self.buffer_black, self.width, self.height, framebuf.MONO_HLSB, stride)
                
            try:
                self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
            except Exception:
                # Try alternate constructor format
                self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB, stride)
                
        except Exception as e:
            import sys
            sys.print_exception(e)
            raise ValueError(f"Failed to allocate memory for display buffers: {e}")
        
        # Hardware buffers for actual display (always 400x300)
        hw_stride = (self.hw_width + 7) // 8  # Bytes per row, rounded up
        hw_buffer_size = hw_stride * self.hw_height
        
        try:
            self.hw_buffer_black = bytearray(hw_buffer_size)
            self.hw_buffer_red = bytearray(hw_buffer_size)
        except Exception as e:
            import sys
            sys.print_exception(e)
            raise ValueError(f"Failed to allocate memory for hardware buffers: {e}")
        
        try:
            self.EPD_4IN2B_Init()
            self.EPD_4IN2B_Clear()
            utime.sleep_ms(500)
        except Exception as e:
            import sys
            sys.print_exception(e)
            raise ValueError(f"Failed to initialize display: {e}")

    def _rotate_buffer(self, source_buffer, target_buffer):
        """Rotate source buffer into target buffer based on self.rotation"""
        if self.rotation == 0:
            # No rotation needed
            for i in range(len(source_buffer)):
                target_buffer[i] = source_buffer[i]
            return
        
        # Clear target buffer
        for i in range(len(target_buffer)):
            target_buffer[i] = 0xFF  # White background
        
        if self.rotation == 90:
            self._rotate_90(source_buffer, target_buffer)
        elif self.rotation == 180:
            self._rotate_180(source_buffer, target_buffer)
        elif self.rotation == 270:
            self._rotate_270(source_buffer, target_buffer)
    
    def _rotate_90(self, source, target):
        """Rotate 90 degrees clockwise"""
        try:
            # For 90° rotation, the key issue is that we need to map from logical to hardware coordinates
            # In 90° rotation, we need to consider that the stride changes
            source_stride = (self.width + 7) // 8
            target_stride = (self.hw_width + 7) // 8
            
            # Clear target buffer first (all white)
            for i in range(len(target)):
                target[i] = 0xFF
            
            # Process each pixel individually to ensure correct mapping
            for y in range(self.height):
                for x in range(self.width):
                    # Get pixel from source buffer at logical coordinates
                    source_byte_idx = (y * source_stride) + (x // 8)
                    source_bit_idx = 7 - (x % 8)  # HLSB format, bit 7 is leftmost
                    
                    if source_byte_idx < len(source):
                        # Check if the bit is set (black) or not (white)
                        pixel = 1 if (source[source_byte_idx] & (1 << source_bit_idx)) else 0
                        
                        # For 90° rotation in hardware coordinates:
                        # The hardware is in landscape, so we're rotating to portrait
                        # (x,y) -> (y, width-1-x) in logical coordinates
                        # But we need to map this to hardware coordinates
                        new_x = y  # y becomes x
                        new_y = self.width - 1 - x  # width-1-x becomes y
                        
                        # Map to hardware coordinates
                        target_byte_idx = (new_y * target_stride) + (new_x // 8)
                        target_bit_idx = 7 - (new_x % 8)  # HLSB format
                        
                        if target_byte_idx < len(target):
                            if pixel == 0:  # Black pixel
                                target[target_byte_idx] &= ~(1 << target_bit_idx)
                            # White pixels are already set by the initial buffer clear
        except Exception as e:
            import sys
            sys.print_exception(e)
            raise
    
    def _rotate_180(self, source, target):
        """Rotate 180 degrees"""
        try:
            # For 180° rotation, the stride remains the same
            stride = (self.width + 7) // 8
            
            # Clear target buffer first (all white)
            for i in range(len(target)):
                target[i] = 0xFF
            
            # Process each pixel individually to ensure correct mapping
            for y in range(self.height):
                for x in range(self.width):
                    # Get pixel from source buffer at logical coordinates
                    source_byte_idx = (y * stride) + (x // 8)
                    source_bit_idx = 7 - (x % 8)  # HLSB format, bit 7 is leftmost
                    
                    if source_byte_idx < len(source):
                        # Check if the bit is set (black) or not (white)
                        pixel = 1 if (source[source_byte_idx] & (1 << source_bit_idx)) else 0
                        
                        # For 180° rotation in hardware coordinates:
                        # The hardware is in landscape, so we're rotating within landscape
                        # (x,y) -> (width-1-x, height-1-y) in logical coordinates
                        new_x = self.width - 1 - x
                        new_y = self.height - 1 - y
                        
                        # Map to hardware coordinates
                        target_byte_idx = (new_y * stride) + (new_x // 8)
                        target_bit_idx = 7 - (new_x % 8)  # HLSB format
                        
                        if target_byte_idx < len(target):
                            if pixel == 0:  # Black pixel
                                target[target_byte_idx] &= ~(1 << target_bit_idx)
                            # White pixels are already set by the initial buffer clear
        except Exception as e:
            import sys
            sys.print_exception(e)
            raise
    
    def _rotate_270(self, source, target):
        """Rotate 270 degrees clockwise (90 degrees counter-clockwise)"""
        try:
            # For 270° rotation, the key issue is that we need to map from logical to hardware coordinates
            # In 270° rotation, we need to consider that the stride changes
            source_stride = (self.width + 7) // 8
            target_stride = (self.hw_width + 7) // 8
            
            # Clear target buffer first (all white)
            for i in range(len(target)):
                target[i] = 0xFF
            
            # Process each pixel individually to ensure correct mapping
            for y in range(self.height):
                for x in range(self.width):
                    # Get pixel from source buffer at logical coordinates
                    source_byte_idx = (y * source_stride) + (x // 8)
                    source_bit_idx = 7 - (x % 8)  # HLSB format, bit 7 is leftmost
                    
                    if source_byte_idx < len(source):
                        # Check if the bit is set (black) or not (white)
                        pixel = 1 if (source[source_byte_idx] & (1 << source_bit_idx)) else 0
                        
                        # For 270° rotation in hardware coordinates:
                        # The hardware is in landscape, so we're rotating to portrait
                        # (x,y) -> (height-1-y, x) in logical coordinates
                        # But we need to map this to hardware coordinates
                        new_x = self.height - 1 - y  # height-1-y becomes x
                        new_y = x  # x becomes y
                        
                        # Map to hardware coordinates
                        target_byte_idx = (new_y * target_stride) + (new_x // 8)
                        target_bit_idx = 7 - (new_x % 8)  # HLSB format
                        
                        if target_byte_idx < len(target):
                            if pixel == 0:  # Black pixel
                                target[target_byte_idx] &= ~(1 << target_bit_idx)
                            # White pixels are already set by the initial buffer clear
        except Exception as e:
            import sys
            sys.print_exception(e)
            raise
    
    def _get_pixel(self, buffer, x, y, width):
        """Get pixel value from buffer at (x,y)"""
        byte_idx = (y * width + x) // 8
        bit_idx = (y * width + x) % 8
        
        if byte_idx >= len(buffer):
            # print(f"DEBUG: Out of bounds in _get_pixel: ({x},{y}) -> idx={byte_idx}, len={len(buffer)}")
            return 1  # White pixel if out of bounds
            
        return (buffer[byte_idx] >> (7 - bit_idx)) & 1
    
    def _set_pixel(self, buffer, x, y, width, pixel):
        """Set pixel value in buffer at (x,y)"""
        byte_idx = (y * width + x) // 8
        bit_idx = (y * width + x) % 8
        
        if byte_idx >= len(buffer):
            # print(f"DEBUG: Out of bounds in _set_pixel: ({x},{y}) -> idx={byte_idx}, len={len(buffer)}")
            return  # Ignore if out of bounds
        
        if pixel == 0:  # Black pixel
            buffer[byte_idx] &= ~(1 << (7 - bit_idx))
        else:  # White pixel
            buffer[byte_idx] |= (1 << (7 - bit_idx))

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

    def gpio_init(self):
        self.spi.deinit()
    
    def spi_init(self):
        self.spi = SPI(1,baudrate=4000_000,sck=Pin(SPI_SCK),mosi=Pin(SPI_MOSI))
        self.dc_pin = Pin(SPI_DC, Pin.OUT)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)

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

    def send_read(self):
        j = 0x00
        self.sck_pin = Pin(SPI_SCK, Pin.OUT)
        self.din_pin = Pin(SPI_MOSI, Pin.IN, Pin.PULL_UP)
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        for i in range(0, 8):
            self.digital_write(self.sck_pin, 0)
            j = j << 1
            if(self.digital_read(self.din_pin) == 1):
                j = j | 0x01
            else:
                j = j & 0xfe
            self.digital_write(self.sck_pin, 1)
        self.digital_write(self.cs_pin, 1)
        return j
        
    def ReadBusy(self):
        print("e-Paper busy")
        if(self.flag == 1):
            while(self.digital_read(self.busy_pin) == 1): 
                self.delay_ms(100) 
        
        else:
            while(self.digital_read(self.busy_pin) == 0): 
                self.delay_ms(100) 
        print("e-Paper busy release")
        
    def TurnOnDisplay(self):
        if(self.flag == 1):
            self.send_command(0x22)
            self.send_data(0xF7)	
            self.send_command(0x20)
            self.ReadBusy()
        
        else:
            self.send_command(0x12)
            self.delay_ms(100) 
            self.ReadBusy()
            
    def EPD_4IN2B_Init(self):
        i = 0x00
        self.reset()
        self.send_command(0x2F)
        
        self.delay_ms(100) 
        self.gpio_init()
        i = self.send_read()
        print(i)
        self.spi_init()

        if(i == 0x01):
            self.flag = 1
            self.ReadBusy()
            self.send_command(0x12)
            self.ReadBusy()

            self.send_command(0x3C)
            self.send_data(0x05)	

            self.send_command(0x18)
            self.send_data(0x80)	

            self.send_command(0x11)      
            self.send_data(0x03)

            self.send_command(0x44) 
            self.send_data(0x00)
            self.send_data(self.hw_width//8-1)

            self.send_command(0x45)        
            self.send_data(0x00)
            self.send_data(0x00) 
            self.send_data((self.hw_height-1)%256)    
            self.send_data((self.hw_height-1)//256)

            self.send_command(0x4E)
            self.send_data(0x00)
            self.send_command(0x4F)  
            self.send_data(0x00)    
            self.send_data(0x00)
            self.ReadBusy()

        else:
            self.flag = 0
            self.send_command(0x04)  # POWER_ON
            self.ReadBusy()

            self.send_command(0x00)  # panel setting
            self.send_data(0x0f)

    def EPD_4IN2B_Clear(self):
        high = self.hw_height
        if( self.hw_width % 8 == 0) :
            wide =  self.hw_width // 8
        else :
            wide =  self.hw_width // 8 + 1

        if(self.flag == 1):
            self.send_command(0x24)
            self.send_data1([0xff] * high * wide)
                    
            self.send_command(0x26)
            self.send_data1([0x00] * high * wide)
        
        else:
            self.send_command(0x10)
            self.send_data1([0xff] * high * wide)
                    
            self.send_command(0x13)
            self.send_data1([0x00] * high * wide)

        self.TurnOnDisplay()
        
    def EPD_4IN2B_Display(self, blackImage=None, redImage=None):
        """
        Enhanced display method with automatic rotation
        If no images provided, uses internal framebuffers
        """
        if blackImage is None:
            blackImage = self.buffer_black
        if redImage is None:
            redImage = self.buffer_red
            
        # Apply rotation if needed
        if self.rotation == 0:
            # No rotation needed, use buffers directly
            rotated_black = blackImage
            rotated_red = redImage
        else:
            # Rotate buffers to hardware orientation
            # Make sure we're starting with clean buffers
            for i in range(len(self.hw_buffer_black)):
                self.hw_buffer_black[i] = 0xFF
                self.hw_buffer_red[i] = 0xFF
                
            self._rotate_buffer(blackImage, self.hw_buffer_black)
            self._rotate_buffer(redImage, self.hw_buffer_red)
            rotated_black = self.hw_buffer_black
            rotated_red = self.hw_buffer_red
        
        # Calculate correct buffer dimensions for the hardware
        high = self.hw_height
        wide = (self.hw_width + 7) // 8  # Ensure proper width calculation
        
        # Send display data efficiently
        if self.flag == 1:
            # Send black buffer
            self.send_command(0x24)
            self.send_data1(rotated_black)
                    
            # Send red buffer (inverted)
            self.send_command(0x26)
            
            # For e-paper, red color requires inverted bits
            # Create a new buffer for the inverted data to avoid modifying the original
            inverted_red = bytearray(len(rotated_red))
            for i in range(len(rotated_red)):
                inverted_red[i] = ~rotated_red[i] & 0xFF
                
            self.send_data1(inverted_red)
        
        else:
            # Send black buffer
            self.send_command(0x10)
            self.send_data1(rotated_black)
                    
            # Send red buffer (inverted)
            self.send_command(0x13)
            
            # For e-paper, red color requires inverted bits
            # Create a new buffer for the inverted data to avoid modifying the original
            inverted_red = bytearray(len(rotated_red))
            for i in range(len(rotated_red)):
                inverted_red[i] = ~rotated_red[i] & 0xFF
                
            self.send_data1(inverted_red)

        self.TurnOnDisplay()
        
    def Sleep(self):
        if(self.flag == 1):
            self.send_command(0X10) 
            self.send_data(0x03)
        
        else:
            self.send_command(0X50) 
            self.send_data(0xf7)             
            self.send_command(0X02)
            self.ReadBusy() 
            self.send_command(0X07) 
            self.send_data(0xA5)
    
    def get_effective_dimensions(self):
        """Return the effective drawing dimensions based on rotation"""
        return self.width, self.height
    
    def set_rotation(self, rotation):
        """Change rotation and reinitialize framebuffers"""
        old_rotation = self.rotation
        self.rotation = rotation % 360
        if self.rotation not in [0, 90, 180, 270]:
            raise ValueError("Rotation must be 0, 90, 180, or 270 degrees")
        
        # Only reinitialize if rotation actually changed
        if old_rotation != self.rotation:
            # Update effective dimensions
            if self.rotation % 180 == 0:
                self.width = self.hw_width   # 400
                self.height = self.hw_height # 300
            else:
                self.width = self.hw_height  # 300 
                self.height = self.hw_width  # 400
            
            # Recreate framebuffers with new dimensions
            self.buffer_black = bytearray(self.height * self.width // 8)
            self.buffer_red = bytearray(self.height * self.width // 8)
            self.imageblack = framebuf.FrameBuffer(self.buffer_black, self.width, self.height, framebuf.MONO_HLSB)
            self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
            
            # Clear new buffers
            self.imageblack.fill(0xff)
            self.imagered.fill(0xff)

    def debug_rotation_mapping(self, rotation_angle):
        """
        Debug method to print out pixel mapping for a specific rotation
        """
        print(f"DEBUG: Pixel mapping for {rotation_angle}° rotation")
        print(f"Logical dimensions: {self.width}x{self.height}")
        print(f"Hardware dimensions: {self.hw_width}x{self.hw_height}")
        
        # Calculate strides
        source_stride = (self.width + 7) // 8
        target_stride = (self.hw_width + 7) // 8
        
        print(f"Source stride: {source_stride}, Target stride: {target_stride}")
        
        # Check mapping for key pixels
        test_points = [
            (0, 0),                      # Top-left
            (self.width - 1, 0),         # Top-right
            (0, self.height - 1),        # Bottom-left
            (self.width - 1, self.height - 1)  # Bottom-right
        ]
        
        for x, y in test_points:
            if rotation_angle == 90:
                new_x = y
                new_y = self.width - 1 - x
            elif rotation_angle == 180:
                new_x = self.width - 1 - x
                new_y = self.height - 1 - y
            elif rotation_angle == 270:
                new_x = self.height - 1 - y
                new_y = x
            else:  # 0 degrees
                new_x = x
                new_y = y
                
            source_byte_idx = (y * source_stride) + (x // 8)
            source_bit_idx = 7 - (x % 8)
            
            target_byte_idx = (new_y * target_stride) + (new_x // 8)
            target_bit_idx = 7 - (new_x % 8)
            
            print(f"({x},{y}) -> ({new_x},{new_y}): src_idx={source_byte_idx}.{source_bit_idx}, tgt_idx={target_byte_idx}.{target_bit_idx}")
            
        return True

    def set_partial_window(self, x, y, w, h):
        """Set the partial window for refresh"""
        # Ensure x and w are multiples of 8 for proper partial refresh
        x = (x // 8) * 8
        w = ((w + 7) // 8) * 8
        self.partial_x = x
        self.partial_y = y
        self.partial_w = w
        self.partial_h = h
    
    def display_partial(self):
        """Perform a partial refresh of the display"""
        if not hasattr(self, 'partial_x'):
            print("Error: Partial window not set")
            return
        
        # Calculate buffer indices for the partial area
        x = self.partial_x
        y = self.partial_y
        w = self.partial_w
        h = self.partial_h
        
        # Send command to set partial window
        self.send_command(0x91)  # Partial in command
        self.send_command(0x00)  # Partial window X start
        self.send_data(x & 0xFF)
        self.send_data((x >> 8) & 0xFF)
        self.send_command(0x01)  # Partial window Y start
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        self.send_command(0x02)  # Partial window X end
        self.send_data((x + w - 1) & 0xFF)
        self.send_data(((x + w - 1) >> 8) & 0xFF)
        self.send_command(0x03)  # Partial window Y end
        self.send_data((y + h - 1) & 0xFF)
        self.send_data(((y + h - 1) >> 8) & 0xFF)
        
        # Send partial LUT (faster refresh)
        self.send_command(0x20)  # Set LUT register
        for i in range(42):
            self.send_data(self.lut_partial[i])
        
        # Send display data for partial window
        stride = (self.hw_width + 7) // 8
        
        # Send black buffer for partial area
        self.send_command(0x24)
        for j in range(y, y + h):
            for i in range(x // 8, (x + w) // 8):
                idx = j * stride + i
                if idx < len(self.buffer_black):
                    self.send_data(self.buffer_black[idx])
        
        # Send red buffer for partial area
        self.send_command(0x26)
        for j in range(y, y + h):
            for i in range(x // 8, (x + w) // 8):
                idx = j * stride + i
                if idx < len(self.buffer_red):
                    # For e-paper, red color requires inverted bits
                    self.send_data(~self.buffer_red[idx] & 0xFF)
        
        # Refresh display
        self.send_command(0x22)
        self.send_data(0x0F)  # Display update control 2
        self.send_command(0x20)  # Activate display update sequence
        self.ReadBusy()
        
        # Exit partial mode
        self.send_command(0x92)  # Partial out command
    
    # Define partial refresh LUT (Look-Up Table) for faster updates
    lut_partial = [
        0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x80, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x40, 0x40, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00,
        0x00, 0x00
    ]