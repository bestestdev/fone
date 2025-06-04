# fone

A modern take on the classic Nokia cell phone experience, built with a Raspberry Pi Pico 2 running MicroPython. This project combines the simplicity and reliability of old-school Nokia phones with quality-of-life improvements for modern usability.

## Overview

**fone** is a DIY cellular phone that captures the essence of classic Nokia devices while incorporating modern components and conveniences. The device features a minimalist design focused on essential communication functions: calls, SMS, and basic navigation, all powered by MicroPython for easy customization and development.

## Hardware Components

### Core Processing
- **Raspberry Pi Pico 2** - Main microcontroller running MicroPython
- **32GB microSD card** - Storage for contacts, messages, and system data
- **microSD SDHC adapter** - Interface for storage expansion

### Power Management
- **3700mAh Lithium Battery** - Long-lasting power source
- **TP4056 Charging Module** - Safe battery charging via USB-C

### Cellular Communication
- **SIM7600G Module** - 4G/LTE cellular connectivity with GPS
- Connected via UART (TX/RX) to Pico 2

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
- **Battery Life**: Multi-day usage with 3700mAh capacity
- **Charging**: USB charging via TP4056 module
- **Standby**: Ultra-low power consumption with e-paper display

### Interface
- **Display**: 2.9" monochrome e-paper (296x128px)
- **Input**: Analog joystick with multi-directional control
- **Audio**: Full-duplex voice communication
- **Feedback**: Vibration motor for alerts

## Software Architecture

- **Platform**: MicroPython on Raspberry Pi Pico 2
- **Modular Design**: Separate modules for cellular, audio, display, and input handling
- **Event-Driven**: Efficient power management through interrupt-based operation
- **Extensible**: Easy to add new features and customize behavior

## Getting Started

*[Development in progress - setup instructions coming soon]*
