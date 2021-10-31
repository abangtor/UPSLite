#!/usr/bin/env python
import struct
import os
import smbus
import time
import RPi.GPIO as GPIO

#########
# CLASS #
class UPSLite:
  def __init__(self, f_uiBusID, f_uiAddress, f_uiExPwrGpio, f_uiSelectGpio):
    self.objBus       = smbus.SMBus(f_uiBusID)
    self.uiAddress    = f_uiAddress
    self.uiExPwrGpio  = f_uiExPwrGpio
    self.uiSelectGpio = f_uiSelectGpio
    self.flVoltage    = 0
    self.flCapacity   = 0
    self.boIsOnPower  = False
    self.boInitBus    = True
    
    # Init GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(self.uiSelectGpio, GPIO.IN)
    GPIO.setup(self.uiExPwrGpio, GPIO.IN)
    
  def Update(self):
    # Read power suppy state
    self.boIsOnPower = (GPIO.input(self.uiExPwrGpio) == GPIO.HIGH)
    
    # Enable I2C line
    if( self.boIsOnPower ):
      GPIO.setup(self.uiSelectGpio, GPIO.OUT)
      GPIO.output(self.uiSelectGpio, GPIO.LOW)

    if( self.boInitBus ):
      self.InitBus()
  
    # Read voltage from i2c
    ui16BusReading   = self.objBus.read_word_data(self.uiAddress, 0X02)
    flVoltageRaw     = struct.unpack("<H", struct.pack(">H", ui16BusReading))[0]
    self.flVoltage   = flVoltageRaw * 1.25 /1000/16
    
    # Read capacity from i2c
    ui16BusReading   = self.objBus.read_word_data(self.uiAddress, 0X04)
    flCapacityRaw    = struct.unpack("<H", struct.pack(">H", ui16BusReading))[0]
    self.flCapacity  = flCapacityRaw/256
    
    # Disable I2C Line
    if( self.boIsOnPower ):
      GPIO.setup(self.uiSelectGpio, GPIO.IN)
    
  def InitBus(self):
    # Init i2c Bus
    self.objBus.write_word_data(self.uiAddress, 0xfe,0x0054)
    self.objBus.write_word_data(self.uiAddress, 0x06,0x4000)
    time.sleep(1)
    # Set bus as initialized
    self.boInitBus = False
    
  def IsOnPower(self):
    return self.boIsOnPower
    
  def GetVoltage(self):
    return self.flVoltage
    
  def GetCapacity(self):
    return self.flCapacity
  

########
# MAIN #

print "<6>Initialize UPSLite..."
objUpsLite = UPSLite(1, 0x36, 4, 17)
boTriggerShutdown = False
uiOnBatteryTime = 0
boResetTimer = True

### MainLoop
while True:
  objUpsLite.Update();
  
### Log UPS status
  if( objUpsLite.IsOnPower() ):
    print "<7> On external Powersupply: %.2fV" % objUpsLite.GetVoltage() \
        + " %i%%" % objUpsLite.GetCapacity()
  else:
    print "<7> On Battery: %.2fV" % objUpsLite.GetVoltage() \
        + " %i%%" % objUpsLite.GetCapacity()
        
### Write in temp file
  objFile = open('/tmp/UPSLiteStatus.txt', 'wt')
  objFile.write("%i" % objUpsLite.IsOnPower() + "\n" \
              + "%.3f" % objUpsLite.GetVoltage() + "\n" \
              + "%i" % objUpsLite.GetCapacity() +"\n")
  objFile.close()

### Shutdown on low power
  if( not objUpsLite.IsOnPower() and \
      objUpsLite.GetCapacity() <= 30 ):
    print "<4> low battery, initiating system shutdown..."
    boTriggerShutdown = True

### Shutdown if battery voltage drops below 3.8V
  if( not objUpsLite.IsOnPower() and \
      objUpsLite.GetVoltage() <= 3.8 ):
    print "<4> low power, initiating system shutdown..."
    boTriggerShutdown = True

### Shutdown if after 10 min on battery
  if( objUpsLite.IsOnPower() ):
    if( not boResetTimer ):
      boResetTimer = True
  else:
    if( boResetTimer ):
      boResetTimer = False
      uiOnBatteryTime = time.time()
    uiElapsedTime = time.time() - uiOnBatteryTime
    if( uiElapsedTime >= (60*10) ):
      print "<7> On Battery since %is, initiating system shutdown..." % uiElapsedTime
      boTriggerShutdown = True
  
### Send shutdown signal to system
  if( boTriggerShutdown ):
    boTriggerShutdown = False
    print "<4> Send Shutdown Signal..."
    os.system('shutdown now -H')

### Sleep
  time.sleep(5)
