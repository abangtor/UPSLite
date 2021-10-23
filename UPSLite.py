#!/usr/bin/env python
import struct
import os
import smbus
import time
import RPi.GPIO as GPIO

#########
# CLASS #
class UPSLite:
  def __init__(self, f_uiBusID, f_uiAddress, f_uiGpioId):
    self.objBus      = smbus.SMBus(f_uiBusID)
    self.uiAddress   = f_uiAddress
    self.uiGpioId    = f_uiGpioId
    self.flVoltage   = 0
    self.flCapacity  = 0
    self.boIsOnPower = False
    self.boInitBus   = True
    
    # Init GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(self.uiGpioId, GPIO.IN)
    
  def Update(self):
    # Read power suppy state
    self.boIsOnPower = (GPIO.input(self.uiGpioId) == GPIO.HIGH)
    
    if( self.boIsOnPower ):
      # Enforce initialisation of bus un next run
      if( not self.boInitBus ):
        self.boInitBus = True
    else:
      # Init bus if necesarry
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
objUpsLite = UPSLite(1, 0x36, 4)

while True:
  objUpsLite.Update();
  
  if( objUpsLite.IsOnPower() ):
    print "<7> On external Powersupply..."
  else:
    print "<7> On Battery: %5.2fV" % objUpsLite.GetVoltage() \
        + " %5i%%" % objUpsLite.GetCapacity()
  
  if( not objUpsLite.IsOnPower() and \
      objUpsLite.GetCapacity() <= 30 ):
    print "<4> low power, initiating system shutdown..."
    os.system('shutdown now -H')
  
  time.sleep(5)
