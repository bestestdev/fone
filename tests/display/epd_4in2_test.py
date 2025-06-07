import sys
sys.path.insert(0, '../../hw')
from epd import EPD_2in9_B_V4_Landscape  # type: ignore

if __name__=='__main__':
    epd = EPD_2in9_B_V4_Landscape()
    epd.Clear()
    
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0x00)
    epd.imageblack.text("Waveshare", 0, 10, 0x00)
    epd.imagered.text("ePaper-2.9-B-V4", 0, 25, 0xff)
    epd.imageblack.text("RPi Pico", 0, 40, 0x00)
    epd.imagered.text("Hello World", 0, 55, 0xff)
    epd.display()
    epd.delay_ms(2000)
    
    epd.imagered.vline(10, 90, 40, 0xff)
    epd.imagered.vline(90, 90, 40, 0xff)
    epd.imageblack.hline(10, 90, 80, 0x00)
    epd.imageblack.hline(10, 130, 80, 0x00)
    epd.imagered.line(10, 90, 90, 130, 0xff)
    epd.imageblack.line(90, 90, 10, 130, 0x00)
    epd.display()
    epd.delay_ms(2000)
    
    epd.init_Fast
    epd.imageblack.rect(10, 150, 40, 40, 0x00)
    epd.imagered.fill_rect(60, 150, 40, 40, 0xff)
    epd.display_Fast()
    epd.delay_ms(2000)
    
    # Test the new methods from the hw class
    epd.init()
    epd.clear()  # Use the new clear method
    
    # Test drawing crosshairs
    epd.draw_crosshair(64, 100, size=8, color='black')
    epd.draw_crosshair(64, 150, size=12, color='red')
    epd.display()
    epd.delay_ms(2000)
    
    epd.init()
    epd.Clear()
    epd.delay_ms(2000)
    print("sleep")
    epd.sleep()