import serial
import serial.tools.list_ports
import guizero
import threading
# Import required modules

killComFlag = False
# killComFlag is the flag that the comCheck will check

radioOptions = ["FT-817ND",""]
# Options for the Radio drop-down menu

comPorts = []
for i in range(1,13):
    comPorts.append("COM{}".format(str(i)))
# Generates a list of COM ports from 1-12 (inclusive)

radioCommands = {
    "":{
        "TX":bytes([10,10,10,10]),
        "RX":bytes([10,10,10,10]),
        "Baud":[""],
        "stopBits":serial.STOPBITS_TWO,
        "parity":serial.PARITY_NONE,
        "byteSize":serial.EIGHTBITS
        },

    "FT-817ND":{
        "TX":bytes([10,10,10,10,8]),
        "RX":bytes([10,10,10,10,136]),
        "Baud":[4800,9600,38400],
        "stopBits":serial.STOPBITS_TWO,
        "parity":serial.PARITY_NONE,
        "byteSize":serial.EIGHTBITS
        }
    }
# The dictionary that acts as a lookup table for each radio
# TX is the bytes needed to activate the transmitter
# RX is the bytes needed to deactivate the transmitter
# Baud gives a list of baud rates the radio can support
# stopBits is the number of stop bits the radio needs
# parity is the parity the radio needs (even, odd or no parity)
# byteSize is how big each byte is

root = guizero.App(title="rts2cat",layout="grid",width=219,height=166)
radioLabel = guizero.Text(root,text="Radio: ",grid=[0,0],align="left")
radioSelection = guizero.Combo(root,options=radioOptions,grid=[1,0],align="left")
# Initialises the root window, the drop down menu and the label next to the drop down menu

def updateTick():

    if radioBaudSelection._options != radioCommands[radioSelection.value]["Baud"]:
    
        radioBaudSelection._options = radioCommands[radioSelection.value]["Baud"]
    
        radioBaudSelection._refresh_options()

    if radioSelection.value == "":

        StartTxButton.disable()

    elif radioBaudSelection != "":

        StartTxButton.enable()

    else:

        StartTxButton.enable()
# updateTick updates the baud drop-down menu when a new radio is selected
# It also disables StartTxButton if a blank option is selected in the radio
# drop-down menu

def maintainWindowSize(width=219,height=166):

    if root.width != width:

        root.width = width
    
    if root.height != height:

        root.height = height
# maintainWindowSize resizes root to width and height which default to 219 and 166
# respectively should no argument be provided

def comCheck(baudArg,radioPortArg,loopbackPortArg,stopBitsArg,parityArg,byteSizeArg,TX,RX):

    global root
    # Use the global variable root

    try:

        cat = serial.Serial(port=radioPortArg,baudrate=baudArg,stopbits=stopBitsArg,parity=parityArg,bytesize=byteSizeArg)
        tnc = serial.Serial(port=loopbackPortArg,rtscts=True)
        # Makes two serial.Serial objects with the arguments supplied

        while True:

            if killComFlag:

                cat.write(RX)

                break
            # Sends the RX signal and breaks from loop if killComFlag is True

            if tnc.cts:

                cat.write(TX)

                while tnc.cts:

                    if killComFlag:

                        cat.write(RX)

                        break

                cat.write(RX)
            # Should tnc.cts be True, TX the radio until tnc.cts is False
            # Then send the RX signal
    
    except serial.SerialException:

        guizero.error("Error","Cannot open COM port!")

        try:

            cat.write(RX)

        except:

            pass

        StartTxButton.enable()
        EndTxButton.disable()

    # If serial.SerialException is raised, send the RX signal,
    # enable StartTxButton and disable EndTxButton

radioBaudSelection = guizero.Combo(root,options=radioCommands[radioSelection.value]["Baud"],grid=[1,1],align="left")
radioBaudLabel = guizero.Text(root,text="Radio Baud: ",grid=[0,1],align="left")
# Initialises the radioBaudSelection drop-down menu and the corrisponding label

catComSelection = guizero.Combo(root, options=comPorts,grid=[1,2],align="left")
guizero.Text(root,text="Radio Port: ",grid=[0,2],align="left")
tncComSelection = guizero.Combo(root, options=comPorts,grid=[1,3],align="left")
guizero.Text(root,text="Loopback Port: ",grid=[0,3],align="left")
# Initialises the two COM port drop-down menus and their labels

def startCom():

    global killComFlag
    TxRxLoopThread = threading.Thread(target=comCheck,args=(int(radioBaudSelection.value),catComSelection.value,tncComSelection.value,radioCommands[radioSelection.value]["stopBits"],radioCommands[radioSelection.value]["parity"],radioCommands[radioSelection.value]["byteSize"],radioCommands[radioSelection.value]["TX"],radioCommands[radioSelection.value]["RX"]),daemon=True)
    StartTxButton.disable()
    EndTxButton.enable()
    killComFlagFalse = False
    TxRxLoopThread.run()
# Starts TxRxLoopThread calling comCheck, enables EndTxButton and disables StartTxButton

def stopCom():

    global killComFlag

    StartTxButton.enable()
    EndTxButton.disable()
    killComFlag = True
# Sets killComFlag to True, thus killing TxRxLoopThread
# Also enables StartTxButton and disables EndTxButton

StartTxButton = guizero.PushButton(root, text="Enable TX", command=startCom,grid=[0,4])
EndTxButton = guizero.PushButton(root, text="Disable TX", command=stopCom,grid=[1,4])
EndTxButton.disable()
# Initialises StartTxButton and EndTxButton
# Disables EndTxButton

root.repeat(100,updateTick)
root.repeat(25, maintainWindowSize)
# Calls updateTick every 100ms & calls maintainWindowSize every 25ms

root.display()
# Displays root