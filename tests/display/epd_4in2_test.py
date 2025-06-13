import sys
sys.path.insert(0, '../../hw')
from epd import EPD_4in2_B  # type: ignore

if __name__ == "__main__":
    epd = EPD_4in2_B()
    
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0xff)
    
    epd.imageblack.text("Waveshare", 5, 10, 0x00)
    epd.imagered.text("Pico_ePaper-4.2-B", 5, 40, 0x00)
    epd.imageblack.text("Raspberry Pico", 5, 70, 0x00)
    epd.EPD_4IN2B_Display(epd.buffer_black,epd.buffer_red)
    epd.delay_ms(5000)
    
    epd.imageblack.vline(10, 90, 60, 0x00)
    epd.imagered.vline(90, 90, 60, 0x00)
    epd.imageblack.hline(10, 90, 80, 0x00)
    epd.imagered.hline(10, 150, 80, 0x00)
    epd.imageblack.line(10, 90, 90, 150, 0x00)
    epd.imagered.line(90, 90, 10, 150, 0x00)
    epd.EPD_4IN2B_Display(epd.buffer_black,epd.buffer_red)
    epd.delay_ms(5000)
    
    epd.imageblack.rect(10, 180, 50, 80, 0x00)
    epd.imagered.fill_rect(70, 180, 50, 80, 0x00)
    epd.EPD_4IN2B_Display(epd.buffer_black,epd.buffer_red)
    epd.delay_ms(5000)

    epd.EPD_4IN2B_Clear()
    epd.Sleep()