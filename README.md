# fone

A modern take on the classic Nokia cell phone experience, built with a Raspberry Pi Pico 2 running MicroPython. This project combines the simplicity and reliability of old-school Nokia phones with quality-of-life improvements for modern usability.

## Overview

**fone** is a DIY cellular phone that captures the essence of classic Nokia devices while incorporating modern components and conveniences. The device features a minimalist design focused on essential communication functions: calls, SMS, and basic navigation, all powered by MicroPython for easy customization and development.

## Hardware Components

### Core Processing
- **Raspberry Pi Pico 2** - Main microcontroller running MicroPython
- **32GB microSD card** - Storage for contacts, messages, and system data
- **microSD SDHC adapter** - Interface for storage expansion

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
- **2.9" E-Paper Display** - 296x128 resolution, SPI interface, low power consumption
- **Dual-axis Analog Joystick** - Navigation and menu control
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
- **Storage**: MicroSD card support up to 32GB

### Power
- **Battery Life**: All-day usage with 3700mAh capacity
- **Charging**: USB charging via TP4056 module
- **Standby**: Ultra-low power consumption with e-paper display

### Interface
- **Display**: 2.9" monochrome e-paper (296x128px)
- **Input**: 2x Analog joysticks with multi-directional control
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

### Dual Analog Joysticks via ADS1115 ADC

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

*[Development in progress - setup instructions coming soon]*
