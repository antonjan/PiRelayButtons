#
# WB1FJ Antenna Control
#
# This is a GUI to control relays that switch a software defined
# radio connected to a telemetry computer and a TS-2000 among an
# omni dual band satellite antenna, an LEO Pack 70cm and 2m beam, 
# and a dual-band J-pole for local work
#
#Relays:
#
#Preamp70:  Preamp on 70cm Beam
#Preamp2m:  Preamp on 2m Beam
#Beam70: Switch 70cm Beam to TS2K bus or SDR Bus
#Beam2m: Switch  2m  Beam to TS2K bus or SDR Bus
#TS2K: Switch TS-2000 to TS2K bus or dual band J-pole
#SDR: Switch SDR to SDR Bus or Lindenblad (Omni)
#
#   Button               Relay States
#
#U/v Satellite COM: Preamp70: off
#	            Preamp2m: on
#                   Beam70: TS2K Bus
#	            Beam2m: TS2K Bus
#		    TS2K: TS2K
#		    SDR: Omni
#
#V/u Satellite COM: Preamp70 on
#		    Preamp2m off
#		    Beam70: TS2K Bus
#		    Beam2m: TS2K Bus
#		    TS2K: TS2K
#		    SDR: Omni
#
#Local Repeater: 	  Preamp70 off
#		    Preamp2m off
#		    Beam70: TS2K Bus
#		    Beam2m: TS2K Bus
#		    TS2K: J-pole
#		    SDR: Omni
#
#UHF Beam Telem: 	  Preamp70: on
#		    Preamp2m: off
#		    Beam70: SDR Bus
#		    Beam2m: TS2K Bus
#		    TS2K: TS2K Bus
#		    SDR: SDR Bus
#
#VHF Beam Telem: 	  Preamp70 off
#		    Preamp2m on
#		    Beam70: TS2K Bus
#		    Beam2m: SDR Bus
#		    TS2K: TS2K
#		    SDR: SDR Bus



#import tkinter as tk

import tkinter as tk
import RPi.GPIO as GPIO
import time
import sys


class Relay: #This is for the Sunfounder/Huayao relay board where a high GPIO turns the relay coil off.
    
    # If you create a Relay instance with a checkbutton, that checkbutton is activated or deactivated
    # when the relay is turned on or off
    
    def __init__(self,gpioNum1,initialState,checkbutton=None):
        self.gpioNum = gpioNum1
        GPIO.setup(self.gpioNum,GPIO.OUT)
        self.fixButton=checkbutton
        self.set(initialState)
    def setAssociatedButton(self,button):
        #Associated Button's select or deselect method is called to match this
        #relay's state.  It also let's the button turn the relay on and off
        #rather than doing it here.
        self.fixButton=button

    def setOnly(self,state):
        #Set the relay without calling the button method.  Used by the button method itself
        self.state= state
        GPIO.output(self.gpioNum,not self.state) #High for off, low for on
        
    def set(self,state):
        self.setOnly(state)
        if self.fixButton is not None:
            if state:
                self.fixButton.select()
            else:
                self.fixButton.deselect()
        
    def get(self):
        return self.state
        

#Define values for the relays that name the purpose for the relay in that position

On=True #For Preamps (Default)
Off=False
TS2K=False #For Beam Bus TS2K End (Default)
SDR=True
Beam=True #For TS2k and SDR
JPole=False #For TS2K
Omni=False #For SDR


## GUI definitions

#Button Values
UvButtonNum=0
VuButtonNum=1
RepeaterButtonNum=2
UHFTlmButtonNum=3
VHFTlmButtonNum=4

#Callback routines for checkbuttons.  They set the relay to the value of the checkbox

def Switch2mPreamp():
    relayPreamp2m.setOnly(P2mValue.get()==1)
def Switch70Preamp():
    relayPreamp70.setOnly(P70Value.get()==1)

#Define the GPIOs for various relays
GPIO.setmode(GPIO.BOARD) #By board pin number
relayPreamp70 = Relay(21,Off)
relayPreamp2m = Relay(23,Off)
relay2mBeamTS2KorSDR = Relay(29,TS2K)
relay70BeamTS2KorSDR = Relay(31,TS2K)
relayTS2KbeamOrJPole = Relay(33,JPole)
relaySDRbeamOrOmni = Relay(35,Omni)
relaySpare1 = Relay(37,Off) #Broken on one relay board
relaySpare2 = Relay(19,Off)

RelayList = [relayPreamp70,relayPreamp2m,relay2mBeamTS2KorSDR,relay70BeamTS2KorSDR,relayTS2KbeamOrJPole,
             relaySDRbeamOrOmni]

#The following table tells what values to set each relay (columns) to for each configuration(row)
#Row numbers have to match the value passed to the variable in the radio buttons; column number
#must match the order of the relays in RelayList

RelayActionsForButton = [
    #70Pre 2mPre 2mBeam 70Beam TS2KAnt SDRAnt<-Relays
    [Off,  On,   TS2K,  TS2K,   Beam,  Omni], #UVButton
    [On,   Off,  TS2K,  TS2K,   Beam,  Omni], #VUButton
    [Off,  Off,  TS2K,  TS2K,   JPole, Omni], #Repeater
    [On,   Off,  TS2K,  SDR,    Beam,  Beam], #UTelemButton
    [Off,  On,   SDR,   TS2K,   Beam,  Beam], #VTelemButton
    ]


#Here are callback routines for all the buttons and checkboxes
DebugRelaySet = False
def Leave(): #This one is for the exit radio button
    GPIO.cleanup()
    sys.exit(1)

def RelayGroupSwitch(): #This is for all other radio buttons
    thisButtonIndex = CurrentButton.get()
    if(DebugRelaySet):
        print("Button number ",thisButtonIndex)
    RelaySettings = RelayActionsForButton[thisButtonIndex]
    for i in range(len(RelayList)):
        thisRelay = RelayList[i]
        thisRelay.set(RelaySettings[i])
        if(DebugRelaySet):
            print("Setting relay",i, "to", RelaySettings[i])



#Here is where we set up the layout for the screen

win = tk.Tk()
#win.geometry("200x200")
win.title("WB1FJ Antenna Switcher")
CurrentButton=tk.IntVar()
tk.Label(win,text="Configuration:").grid(row=0,columnspan=2,sticky=tk.W)

#Here are 2 checkboxes for preamps that are overrides of the standard values for a confiruration.
#For example, you can turn on the preamp while in the local repeater configuration.

tk.Label(win,text="Preamp Override:").grid(row=8,column=0,sticky=tk.E)
tk.Label(win,text="________________________________________________________________________________").grid(row=7,column=0,columnspan=2)

P70Value = tk.IntVar()
Preamp70Button = tk.Checkbutton(win,text="70Cm",variable=P70Value,command=Switch70Preamp)
Preamp70Button.grid(column=1,row=8)

P2mValue=tk.IntVar()
Preamp2mButton = tk.Checkbutton(win,text="2M",variable=P2mValue,command=Switch2mPreamp)
Preamp2mButton.grid(column=1,row=8,sticky=tk.W)

relayPreamp70.setAssociatedButton(Preamp70Button) #Make sure when a configuration sets one of these relays,---
relayPreamp2m.setAssociatedButton(Preamp2mButton) #...the checkbox matches


# Here are the radio buttons that let you choose the configuration--only one is active at a time.

SatComUvButton = tk.Radiobutton(win,text = "U/v Satcom",command=RelayGroupSwitch,selectcolor="Red")
SatComUvButton.config(variable=CurrentButton,value=UvButtonNum,indicatoron=False,width=30,pady=20)
SatComUvButton.grid(row=4,column=0)

SatComVuButton = tk.Radiobutton(win,text = "V/u Satcom",command=RelayGroupSwitch,selectcolor="Red")
SatComVuButton.grid(row=4,column=1,columnspan=1)
SatComVuButton.config(variable=CurrentButton,value=VuButtonNum,indicatoron=False,width=30,pady=20)

RepeaterButton = tk.Radiobutton(win,text = "Local Repeater",command=RelayGroupSwitch,selectcolor="Red")
RepeaterButton.grid(row=6,column=0,columnspan=2)
RepeaterButton.config(variable=CurrentButton,value=RepeaterButtonNum,indicatoron=False,width=30,pady=20)

SatTlmVButton = tk.Radiobutton(win,text = "VHF Telemetry",command=RelayGroupSwitch,selectcolor="Red")
SatTlmVButton.grid(row=5,column=0,columnspan=1)
SatTlmVButton.config(variable=CurrentButton,value=VHFTlmButtonNum,indicatoron=False,width=30,pady=20)

SatTlmUButton = tk.Radiobutton(win,text = "UHF Telemetry",command=RelayGroupSwitch,selectcolor="Red")
SatTlmUButton.grid(row=5,column=1,columnspan=1)
SatTlmUButton.config(variable=CurrentButton,value=UHFTlmButtonNum,indicatoron=False,width=30,pady=20)


ExitButton = tk.Radiobutton(win,text = "Exit",command=Leave,variable=CurrentButton,value=99,indicatoron=False)
ExitButton.grid(row=8,column=0,sticky=tk.W)

#Set the default button
CurrentButton.set(RepeaterButtonNum)
RelayGroupSwitch() #Set up everything for the above default button

DebugRelayID = False

#This is to make sure we know which relay is which
if DebugRelayID:
    for i in range(NumberOfRelays):
        thisRelay = RelayList[i]
        thisRelay.set(True)
        print("Setting relay",i, "to True")
        time.sleep(1)

    for i in range(NumberOfRelays):
        thisRelay = RelayList[i]
        thisRelay.set(False)
        print("Setting relay",i, "to False")
        time.sleep(1)

win.mainloop()


