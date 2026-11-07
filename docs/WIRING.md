# Pokémon Sorter MVP — wiring and power

## Scope and assumptions

This wiring plan assumes a **Linux Raspberry Pi with a 40-pin GPIO header** (Pi 3/4/5 or a suitable Pi Zero) and a **CSI or USB camera**. A **Raspberry Pi Pico is not a substitute** for a Linux Pi in the software package. Confirm the model with `cat /proc/device-tree/model` after booting. A Pi 5 or 4 is easiest for local image recognition; Pi 3 or Zero 2 W may require lower image resolution or sending identification to another computer.

## Required electronics, V1

- Raspberry Pi + proper official/reliable PSU, microSD, network access.
- CSI Camera Module 3 **standard lens** (not wide) *or* USB webcam with 1080p/4K and close focusing. **Check compatibility with your actual Pi before purchase.**
- PCA9685 16-channel I2C servo driver (optional for one servo, recommended for reliable scaling).
- One **metal-gear MG90S-type** servo (tray tilt). Check travel, torque and horn fit of actual unit.
- Separate, regulated **5V 2–3A** supply for servo motors; suitably fused, good-quality wiring and connector.
- **Normally closed emergency switch** in series with servo V+ to cut motor power. Power Pi independently. Optional microswitch to detect mechanical center position.
- Two diffused LED strips at 30–45 degrees, powered separately/safely through their rated power supply.
- 1 Raspberry Pi-compatible camera ribbon, appropriate to Pi's CSI connector and cable size, or USB cable if webcam.

## PCA9685 — GPIO mapping (40-pin Raspberry Pi)

| From Raspberry Pi | To PCA9685 | Notes |
|---|---|---|
| Physical pin 1 (3V3) | `VCC` | Powers driver logic **ONLY** |
| Physical pin 3 (GPIO2 / SDA1) | `SDA` | I2C data |
| Physical pin 5 (GPIO3 / SCL1) | `SCL` | I2C clock |
| Physical pin 6 (GND) | `GND` | Common ground |
| Separate 5V supply + | `V+` terminal via NC emergency switch | Servo motor supply; **not Pi 5V** |
| Separate 5V supply − | `GND` terminal | Common with Pi GND |
| PCA9685 servo channel 0 | Tilt servo red / brown / signal | Red to V+, brown/black to GND, orange/yellow to PWM |
| PCA9685 servo channel 1 | Future gate/feed servo | Unused initially |

I2C address normally `0x40`; verify with `sudo i2cdetect -y 1`. Install `i2c-tools`, enable I2C using `sudo raspi-config`, then Interfaces → I2C. A **5V output from a sensor is not safe on a GPIO input**. Use a 3.3V-output sensor, a proper level shifter, or a dry contact (with Pi's 3.3V pull-up).

## Optional position switch, V1.1

Use a normally-open dry-contact limit switch on the center position:

| Signal | Connection |
|---|---|
| One switch terminal | Physical GPIO pin 11 (GPIO17) |
| Other switch terminal | GND |

Configure GPIO17 as input with a 3.3V internal pull-up. **Never put the external 5V motor supply into a GPIO.** Debounce in software and require the switch to confirm home before accepting the next card.

## Motor safety

1. Before first power-up, disconnect servo horn, center servo at software angle 90°, and attach it *only after* that.
2. Keep the first tests on DRY_RUN=1; call `/api/sort` to simulate motion.
3. Test travel first at ±10°, then ±20°, then increase until a card releases reliably; do **not** force ±55° if the horn hits the bracket.
4. Place the electronics out of the card drop zone. Add mechanical end-stops and cable strain relief.
5. Fuse/size the motor feed appropriately. Never power servos from Raspberry Pi GPIO or Pi 5V header rails.
6. Put a physical stop switch on the servo power line. A software stop is not a substitute.

References: https://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi/hooking-it-up and https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
