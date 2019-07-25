import serial
import serial.tools.list_ports
import guizero
import threading

killComFlag = False
radioOptions = ["FT-817ND",""]
comPorts = []
for i in range(1,13):
    comPorts.append("COM{}".format(str(i)))

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
        "Baud":["4800","9600","38400"],
        "stopBits":serial.STOPBITS_TWO,
        "parity":serial.PARITY_NONE,
        "byteSize":serial.EIGHTBITS
        }
    }

root = guizero.App(title="rts2cat",layout="grid",width=219,height=166)
radioLabel = guizero.Text(root,text="Radio: ",grid=[0,0],align="left")
radioSelection = guizero.Combo(root,options=radioOptions,grid=[1,0],align="left")

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

def maintainWindowSize(width=219,height=166):

    if root.width != width:

        root.width = width
    
    if root.height != height:

        root.height = height

def comCheck(baudArg,radioPortArg,loopbackPortArg,stopBitsArg,parityArg,byteSizeArg,TX,RX):

    global root

    try:

        cat = serial.Serial(port=radioPortArg,baudrate=baudArg,stopbits=stopBitsArg,parity=parityArg,bytesize=byteSizeArg)
        tnc = serial.Serial(port=loopbackPortArg,rtscts=True)

        while True:

            if killComFlag:

                cat.write(RX)

                break

            if tnc.cts:

                cat.write(TX)

                while tnc.cts:

                    if killComFlag:

                        cat.write(RX)

                        break

                cat.write(RX)
    
    except serial.SerialException:

        guizero.error("Error","Cannot open COM port!")

        try:

            cat.write(RX)

        except:

            pass

        StartTxButton.enable()
        EndTxButton.disable()

radioBaudSelection = guizero.Combo(root,options=radioCommands[radioSelection.value]["Baud"],grid=[1,1],align="left")
radioBaudLabel = guizero.Text(root,text="Radio Baud: ",grid=[0,1],align="left")

catComSelection = guizero.Combo(root, options=comPorts,grid=[1,2],align="left")
guizero.Text(root,text="Radio Port: ",grid=[0,2],align="left")
tncComSelection = guizero.Combo(root, options=comPorts,grid=[1,3],align="left")
guizero.Text(root,text="Loopback Port: ",grid=[0,3],align="left")

def startCom():

    global killComFlag
    TxRxLoopThread = threading.Thread(target=comCheck,args=(int(radioBaudSelection.value),catComSelection.value,tncComSelection.value,radioCommands[radioSelection.value]["stopBits"],radioCommands[radioSelection.value]["parity"],radioCommands[radioSelection.value]["byteSize"],radioCommands[radioSelection.value]["TX"],radioCommands[radioSelection.value]["RX"]))
    StartTxButton.disable()
    EndTxButton.enable()
    killComFlagFalse = False
    TxRxLoopThread.run()

def stopCom():

    global killComFlag

    StartTxButton.enable()
    EndTxButton.disable()
    killComFlag = True

StartTxButton = guizero.PushButton(root, text="Enable TX", command=startCom,grid=[0,4])
EndTxButton = guizero.PushButton(root, text="Disable TX", command=stopCom,grid=[1,4])
EndTxButton.disable()

root.repeat(100,updateTick)
root.repeat(25, maintainWindowSize)
root.display()