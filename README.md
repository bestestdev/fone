# fone

A modern take on the classic Nokia cell phone experience, built with a Raspberry Pi Pico 2 running MicroPython. This project combines the simplicity and reliability of old-school Nokia phones with quality-of-life improvements for modern usability.

## Overview

**fone** is a DIY cellular phone that captures the essence of classic Nokia devices while incorporating modern components and conveniences. The device features a minimalist design focused on essential communication functions: calls, SMS, and basic navigation, all powered by MicroPython for easy customization and development.

## Hardware Components

### Core Processing
- **Raspberry Pi Pico 2** - Main microcontroller running MicroPython
- **W25Q128 SPI Flash** - 16MB flash storage for contacts, messages, and system data

### Cellular Communication
- **SIM7600G Module** - 4G/LTE cellular connectivity with GPS
- Connected via UART (TX/RX) to Pico 2

### Power Management
- **3700mAh Lithium Battery** - Long-lasting power source
- **TP4056 Charging Module** - Safe battery charging via USB-C
- **MT3608 Boost Converter** - Boost LiPo battery to 5v for use by the SIM module and Pico

### Audio System
- **MAX98357A I2S Amplifier** - Digital audio amplification
- **1W 8Ω Speaker** - Clear audio output for calls and notifications
- **GY-MAX4466 Electret Microphone** - Voice input with AGC
- **ADS1115 ADC** - High-resolution analog-to-digital conversion for microphone

### Display & Input
- **4.2" E-Paper Display (FPC-190)** - red/white/black, 400x300 resolution, SPI interface, low power consumption
- **5-Way Digital Navigation Joystick** - Navigation, selection, and menu control
- **3V Coin Vibration Motor** - Haptic feedback and notifications

## Features

### Core Functionality
- **Voice Calls** - Make and receive phone calls with clear audio
- **SMS Messaging** - Send and receive text messages
- **Contact Management** - Store and organize phone contacts
- **Call History** - Track incoming, outgoing, and missed calls

### Enhanced User Experience
- **Improved Text Input** - Modern T9-style predictive text with joystick navigation
- **Menu Navigation** - Intuitive interface designed for joystick control
- **Low Power Operation** - E-paper display and efficient power management
- **Haptic Feedback** - Vibration for notifications and user interactions

### Additional Features
- **GPS Location (Stretch Goal)** - Built-in positioning via SIM7600G
- **Battery Monitoring** - Real-time battery level and charging status
- **Silent/Vibrate Modes** - Customizable notification preferences
- **Basic Games** - Classic Nokia-style entertainment (Snake, etc.)

## Technical Specifications

### Connectivity
- **Cellular**: 4G LTE via SIM7600G
- **GPS (Stretch Goal)**: Built-in GNSS receiver
- **Storage**: 16MB SPI flash memory (W25Q128)

### Power
- **Battery Life**: All-day usage with 3700mAh capacity
- **Charging**: USB charging via TP4056 module
- **Standby**: Ultra-low power consumption with e-paper display

### Interface
- **Display**: 2.9" monochrome e-paper (296x128px)
- **Input**: 5-way digital joystick with SET/RST buttons
- **Audio**: Full-duplex voice communication
- **Feedback**: Vibration motor for alerts

## Software Architecture

- **Platform**: MicroPython on Raspberry Pi Pico 2
- **Modular Design**: Separate modules for cellular, audio, display, and input handling
- **Event-Driven**: Efficient power management through interrupt-based operation
- **Extensible**: Easy to add new features and customize behavior

## Wiring Guide

### SIM7600G to Raspberry Pi Pico 2

The SIM7600G module connects via UART and requires the following connections:

| SIM7600G Pin | Description | Connection | Notes |
|--------------|-------------|------------|-------|
| **V** | VCC | **5V from MT3608** | Requires stable 5V (up to 2A) |
| **G** | Ground | **Battery -** | Battery ground |
| **G** | Ground | **Pico GND** (Pin 38) | Shared ground with Pico |
| **T** | TX (Module transmit) | **GP1** (Pin 2) | UART0 RX |
| **R** | RX (Module receive) | **GP0** (Pin 1) | UART0 TX |
| **K** | Power Key | **GP2** (Pin 4) | GPIO for power control |
| **S** | Status | **GP3** (Pin 5) | GPIO for status monitoring |

#### Key Points:
- **Power**: SIM7600G requires 5V via MT3608 boost converter for proper RF operation
- **Current Draw**: Module can draw up to 2A during transmission bursts
- **UART**: Cross-connect TX/RX (module TX → Pico RX, module RX → Pico TX)
- **Power Key**: Pull HIGH briefly to turn module on/off
- **Status**: Monitor this pin to check if module is powered and ready
- **Dual Ground**: Connect both ground pins for stable operation

### 5-Way Digital Navigation Joystick

The primary input is a 5-way digital joystick module, providing directional control, a center-press button, and two additional buttons for 'SET' and 'RST'.

| Joystick Pin | Description | Connection | Notes |
|--------------|-------------|------------|-------|
| **UP** | Up Direction | **GP18** (Pin 24) | Digital input |
| **DOWN** | Down Direction | **GP19** (Pin 25) | Digital input |
| **LEFT** | Left Direction | **GP4** (Pin 6) | Digital input |
| **RIGHT**| Right Direction | **GP5** (Pin 7) | Digital input |
| **MID** | Center Button | **GP6** (Pin 9) | Digital input |
| **SET** | Set Button | **GP17** (Pin 22) | Digital input |
| **RST** | Reset Button | **GP22** (Pin 29) | Digital input |
| **COM** | Common | **GND** (Pin 38) | Common ground for all switches |

#### Key Points:
- **Digital Input**: All joystick pins are simple digital inputs.
- **Wiring**: Connect the COM pin to GND and configure each GPIO pin as an input with an internal pull-up resistor.
- **Active Low**: A button press will pull the corresponding GPIO pin to ground (LOW).
- **Pin Mapping**: Pins selected to avoid conflicts with other components and reserve ADC-capable pins for future use.

### Dual Analog Joysticks via ADS1115 ADC

> **Note:** This component has been deprecated and replaced by the 5-Way Digital Navigation Joystick.

The phone uses two analog joysticks for navigation and input, connected through an ADS1115 16-bit ADC for full 4-channel analog precision.

**ADS1115 ADC Module:**

| ADS1115 Pin | Description | Connection | Notes |
|-------------|-------------|------------|-------|
| **VDD** | Power | **5V** (Pin 40 - VBUS) | Module power supply |
| **GND** | Ground | **GND** (Pin 38) | Common ground |
| **SCL** | I2C Clock | **GP21** (Pin 27) | I2C0 SCL |
| **SDA** | I2C Data | **GP20** (Pin 26) | I2C0 SDA |
| **ADDR** | Address | **GND** | Sets I2C address to 0x48 |

**Left Joystick (mounted upside down):**

| Joystick Pin | Description | Connection | Notes |
|--------------|-------------|------------|-------|
| **VCC** | Power | **5V** (Pin 40 - VBUS) | Joystick power supply |
| **GND** | Ground | **GND** (Pin 38) | Common ground |
| **VRX** | X-axis analog | **ADS1115 AIN0** | Left joystick X |
| **VRY** | Y-axis analog | **ADS1115 AIN1** | Left joystick Y (inverted) |
| **SW** | Switch button | **GP19** (Pin 25) | Digital input with pull-up |

**Right Joystick:**

| Joystick Pin | Description | Connection | Notes |
|--------------|-------------|------------|-------|
| **VCC** | Power | **5V** (Pin 40 - VBUS) | Joystick power supply |
| **GND** | Ground | **GND** (Pin 38) | Common ground |
| **VRX** | X-axis analog | **ADS1115 AIN2** | Right joystick X |
| **VRY** | Y-axis analog | **ADS1115 AIN3** | Right joystick Y |
| **SW** | Switch button | **GP18** (Pin 24) | Digital input with pull-up |

#### Key Points:
- **Full Analog Control**: ADS1115 provides 4 channels of 16-bit ADC precision
- **I2C Address**: 0x48 (ADDR pin to GND), can be changed for multiple modules
- **Left Joystick**: Mounted upside down, so Y-axis values are inverted in software
- **ADC Resolution**: 16-bit (±32767) with ±4.096V input range matches 5V joysticks
- **Switches**: Active low with internal pull-up resistors on Pico pins (3.3V logic)
- **Update Rate**: ~128 SPS (samples per second) for smooth control

### 3V Vibration Motor

The vibration motor provides haptic feedback for notifications and user interactions.

#### Option 1: Direct GPIO Control (Recommended to try first)

**For Low Current Motors (< 40mA):**

| Motor Pin | Description | Connection | Notes |
|-----------|-------------|------------|-------|
| **+** | Positive | **GP16** (Pin 21) | Direct PWM control |
| **-** | Negative | **GND** (Pin 38) | Direct ground connection |

#### Option 2: Transistor-Protected Control

**For Higher Current Motors (> 40mA) or if direct control fails:**

| Motor Pin | Description | Connection | Notes |
|-----------|-------------|------------|-------|
| **+** | Positive | **GP16** (Pin 21) via NPN Transistor | PWM-controlled output |
| **-** | Negative | **GND** (Pin 38) | Direct ground connection |

**Transistor Circuit (NPN - 2N2222 or similar):**

| Transistor Pin | Description | Connection | Notes |
|----------------|-------------|------------|-------|
| **Base** | Control | **GP16** (Pin 21) via 1kΩ resistor | PWM signal from Pico |
| **Collector** | High side | **Motor +** | Connects to motor positive |
| **Emitter** | Ground | **GND** (Pin 38) | Common ground |

#### Key Points:
- **Motor Specs**: 3V, 12000 RPM, small coin-type vibration motor
- **Current Draw**: Small motors (17-35mA) can connect directly, larger motors (60-105mA) need transistor
- **Pico GPIO Limits**: ~16mA safe, ~50mA maximum per pin
- **Try Direct First**: Start with Option 1 - if motor doesn't work well or Pico gets warm, use Option 2
- **Flyback Diode**: Optional 1N4001 diode across motor (cathode to +, anode to -) for back-EMF protection
- **Control**: PWM control via GP16 allows variable vibration intensity
- **Frequency**: Typical vibration patterns: short bursts (100-300ms) for notifications

### 4.2" E-Paper Display (FPC-190)

The 4.2" tri-color e-paper display provides the main user interface with red/white/black output at 400x300 resolution using SPI communication.

**Display Module Connections:**

| Display Pin | Description | Connection | Notes |
|-------------|-------------|------------|-------|
| **VCC** | Power | **3V3** (Pin 36) | 3.3V power supply |
| **GND** | Ground | **GND** (Pin 38) | Common ground |
| **CLK** | SPI Clock | **GP10** (Pin 14) | SPI1 SCK |
| **DIN** | SPI Data In | **GP11** (Pin 15) | SPI1 MOSI (TX) |
| **CS** | Chip Select | **GP9** (Pin 12) | SPI chip select (active low) |
| **DC** | Data/Command | **GP12** (Pin 16) | Command mode control |
| **RST** | Reset | **GP13** (Pin 17) | Hardware reset (active low) |
| **BUSY** | Busy Status | **GP14** (Pin 19) | Display busy indicator |

#### Key Points:
- **SPI Interface**: Uses SPI1 on Pico 2 for high-speed communication
- **Tri-Color Support**: Red/white/black output with partial refresh capability
- **Resolution**: 400x300 pixels provides clear text and simple graphics
- **Update Time**: ~2-15 seconds for full refresh, <1 second for partial updates
- **Low Power**: Ultra-low power consumption when not updating (perfect for phone standby)
- **BUSY Pin**: Monitor this pin to know when display update is complete
- **Reset Control**: Hardware reset via RST pin for reliable initialization

### W25Q128 SPI Flash Memory Module

The W25Q128 provides 16MB (128Mbit) of non-volatile storage for contacts, messages, and system data, connected via SPI interface. This flash memory offers faster access times and lower power consumption compared to SD cards.

**W25Q128 Module Connections:**

| W25Q128 Pin | Description | Connection | Notes |
|-------------|-------------|------------|-------|
| **VCC** | Power | **3V3** (Pin 36) | 3.3V power supply |
| **GND** | Ground | **GND** (Pin 38) | Common ground |
| **DC** | SPI Data Out (MISO) | **GP8** (Pin 11) | SPI1 MISO (RX) |
| **D1** | SPI Data In (MOSI) | **GP11** (Pin 15) | SPI1 MOSI (TX) - **Shared with display** |
| **SLK** | SPI Clock | **GP10** (Pin 14) | SPI1 SCK - **Shared with display** |
| **CS** | Chip Select | **GP7** (Pin 10) | SPI chip select (active low) |

#### Key Points:
- **Shared SPI Bus**: Uses SPI1 shared with the e-paper display (SLK, D0 pins)
- **Separate MISO**: Flash memory has its own MISO line (D1/GP8) since display is write-only
- **Unique CS**: Each device has its own chip select (Flash: GP7, Display: GP9)
- **Power**: 3.3V operation, low power consumption (4mA active, <1µA standby)
- **Storage**: 16MB of flash memory with 100,000+ erase/program cycles
- **Performance**: Up to 104MHz SPI clock, much faster than SD card access
- **File System**: Can use LittleFS or FAT filesystem via MicroPython's VFS

### MAX98357A I2S Amplifier and Speaker

The MAX98357A is a digital I2S audio amplifier used to drive the speaker for calls, notifications, and other audio feedback.

**MAX98357A Module Connections:**

| MAX98357A Pin | Description | Connection | Notes |
|---------------|-------------|------------|-------|
| **Vin** | Power In | **5V** (Pin 40 - VBUS) | 3-5.5V input range |
| **GND** | Ground | **GND** (Pin 38) | Common ground |
| **DIN** | Data In | **GP20** (Pin 26) | I2S Serial Data |
| **BCLK** | Bit Clock | **GP15** (Pin 20) | I2S Bit Clock |
| **LRC** | Left-Right Clock | **GP27** (Pin 32) | I2S Word Select |
| **SD** | Shutdown | **GP21** (Pin 27) | Active-low shutdown control |
| **GAIN** | Gain Select | *(unconnected)* | Default 9dB gain. Connect to GND for 3dB, VCC for 15dB. |

**Speaker Connection:**

| Component | Connection |
|-----------|------------|
| **Speaker +** | **MAX98357A Left/Right +** |
| **Speaker -** | **MAX98357A Left/Right -** |

#### Key Points:
- **I2S Audio**: Digital audio provides clear, noise-free sound.
- **Power**: Connected to 5V for maximum speaker volume.
- **Shutdown Pin**: GP21 controls the amplifier's shutdown mode to conserve power.
- **Mono Output**: Although the module has L/R outputs, it's a mono amplifier. Connect speaker to either pair.
- **Gain Control**: The `GAIN` pin can be used to adjust the amplification level if needed. Default (unconnected) is 9dB.

### GY-MAX4466 Electret Microphone

The GY-MAX4466 microphone module with automatic gain control (AGC) is used for voice input. It's connected directly to one of the Pico's ADC pins.

**Microphone Module Connections:**

| Microphone Pin | Description | Connection | Notes |
|----------------|-------------|------------|-------|
| **VCC** | Power | **3V3** (Pin 36) | 2.4-5.5V input range |
| **GND** | Ground | **GND** (Pin 38) | Common ground |
| **OUT** | Analog Out | **GP28** (Pin 34) | Connects to ADC2 |

#### Key Points:
- **Direct ADC Connection**: Simplifies wiring and reduces component count.
- **Analog Pin**: Uses `GP28`, one of the Pico's three dedicated ADC pins.
- **Power**: Runs on 3.3V power provided by the Pico.
- **AGC**: The MAX4466's automatic gain control adjusts for varying sound levels.

### Battery Level Monitoring

To monitor the battery level, a voltage divider is used to scale the battery's voltage (3.0V-4.2V) down to a range the Pico's ADC can safely read (0-3.3V). The reading is taken on the now-available ADC pin.

**Voltage Divider Circuit:**

| Component | Connection | Notes |
|-----------|----------------------------------|---------------------------------------|
| **Battery +** | Resistor 1 (R1) - e.g., 100kΩ | Connects to the positive battery terminal |
| **R1 + R2** | **GP26** (Pin 31) & Resistor 2 (R2) | Center point connects to Pico's ADC pin |
| **R2** | **GND** (Pin 38) | Connects to ground |

*A 1:1 ratio (e.g., two 100kΩ resistors) is simple and effective.*

**Pin Connection:**

| Description | Connection | Notes |
|-------------------|------------|----------------------------|
| **Voltage Sense** | **GP26** (Pin 31) | ADC capable pin (ADC0) |

#### Key Points:
- **Voltage Divider**: Essential to prevent damage to the Pico's ADC.
- **Resistor Choice**: Using identical resistors (e.g., 100kΩ) creates a simple 1:2 divider. The actual voltage is `2 * adc_voltage`.
- **ADC Reading**: The software must read the analog value from `GP26` and multiply it by the divider ratio to calculate the true battery voltage.

*[Development in progress - setup instructions coming soon]*
