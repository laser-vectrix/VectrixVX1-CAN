import binascii
import xml.dom.minidom
import datetime
import argparse
import time
import curses

### global section
CSVLINE="" # buffer to store each field to be printed, until a single line is completed
SAs={} # list of used Source Addresses
PGNdict={} # list of PGNs from XML file
UnlistedPGN={} # list unknown PGNs

def printCSVline(count,TIME,ID,SA,HEXDATA,Verbose):
    global CSVLINE
    if Verbose ==100 :
        print(count,'|',TIME,'|',ID,'|'," ".join('{} |'.format(x) for x in HEXDATA.split(' ')),CSVLINE)
        CSVLINE=""
    elif Verbose==200 and len(CSVLINE)==0:
        print(count,'|',TIME,'|',ID,'|'," ".join('{} |'.format(x) for x in HEXDATA.split(' ')))
    else:
        CSVLINE=""

def printUsedPGN(used):
    if used:
        print('UsedPGNs:')
    else:
        print('UnusedPGNs:')
    for id in PGNdict:
        for byte in PGNdict[id]:
            for bit in PGNdict[id][byte]:
                if used: # we are priting the PGNs which have been used
                    if len(PGNdict[id][byte][bit]['values']) > 0:
                        strValues=''
                        min=999999
                        max=-1
                        for value in PGNdict[id][byte][bit]['values']:
                            if type(value) == int:
                                if int(value)<min:
                                    min=value
                                if int(value)>max:
                                    max=value                           
                            if type(value) == float:
                                if float(value)<min:
                                    min=value
                                if float(value)>max:
                                    max=value
                            strValues=strValues + str(value)+' ['+str(PGNdict[id][byte][bit]['values'][value]['c'])+'], '
                        if max!=-1:
                            print(PGNdict[id][byte][bit]['label'],'=',strValues,'min=',min,'max=',max)
                        else:
                            print(PGNdict[id][byte][bit]['label'],'=',strValues)


                else: # we are priting the PGNs which have not been used
                    if len(PGNdict[id][byte][bit]['values']) == 0:
                        print(id,'::',PGNdict[id][byte][bit]['label'])
#
# check if an Source Address is already in the list of used ones, if not add it
#
def addSA(ID,val,element):
    label=element['label']
    if not val in element['values']: # if we have not seen this value before, lets store it in the list of seen values for the <ID,byte>
        element['values'][val]={'c':1}
        if ID[6:8] in SAs:
            if not label in SAs[ID[6:8]]['labels']:
                SAs[ID[6:8]]['labels'].append(label)
        else:
            SAs[ID[6:8]]={'idList':[],'labels':[label]}
    else:
        element['values'][val]['c']=element['values'][val]['c']+1

x_labels={}
x_n_labels=0
x_output={}
BMS_nr=0
#
# for every field parsed, print it
#
def printParsedField(countLinePF,TIME,ID,label,value,scale,hex,Verbose,):
    global x_labels,x_n_labels,x_output,stdscr
    if countLinePF<16: # header of the PEAK file
        return ""
    global CSVLINE
    if args.service:
        printService(label, value, scale)                                                                                                                                                                                                                                                                                                                     
    else:
        if Verbose==1:
            if scale != None:
                print(countLinePF,TIME,ID,label,'=',round(value*scale,3))
            else:
                print(countLinePF,TIME,ID,label,'=',value)
        if Verbose==2:
            if scale != None:
                print(countLinePF,TIME,ID,label,'=',round(value*scale,3),hex)
            else:
                print(countLinePF,TIME,ID,label,'=',value,hex)
        if Verbose==3:
            binary=''
            for byte in hex.split(' '):
                binary=binary+' '+bin(int(byte, 16))[2:].zfill(8)
            if scale != None:
                print(countLinePF,TIME,ID,label,'=',round(value*scale,3),binary)
            else:
                print(countLinePF,TIME,ID,label,'=',value,binary)
        if Verbose==300 and label!='data':
            if type(value) == int or type(value) == float:
                value = round(value*scale,3)
            if not label in x_labels:
                x_n_labels=x_n_labels+1
                x_labels[label]=x_n_labels          
            if not countLinePF in x_output: 
                x_output[countLinePF]={x_labels[label]:value}
                #print(countLinePF,label,value)
            else:
                x_output[countLinePF][x_labels[label]]=value
                #print(countLinePF,label,value,x_output[countLinePF],x_labels[label],x_output[countLinePF][x_labels[label]])
        if (Verbose==100 or Verbose==200 ): # Override verbose, print CSV Line
            if type(value) == int or type(value) == float:
                value = round(value*scale,3)
            CSVLINE=CSVLINE+label+' = '+str(value)+'; ' 

def printService(label, value, scale):
    global BMS_nr
    if label=='Time':
        stdscr.addstr(2,80,'Time: '+str(value))
    if label=='Plug icon':
        stdscr.addstr(2,2,'Pluged  : '+str(value))
    if label=='Charge icon':
        stdscr.addstr(3,2,'Charging: '+str(value))    
    if label=='Battery Voltage':
        stdscr.addstr(5,2,'Battery Volts. : '+str(int(round(value*scale,0)))+' V') 
    if label=='Charger Current':
        stdscr.addstr(6,2,'Charger Current: '+str(round(value*scale,2))+' A')   
    if label=='Vehicle Speed':            
        stdscr.addstr(6,28,'Speed indicator: '+str(round(value*scale,2))) 
    if label=='Gauge level':
        stdscr.addstr(8,2,'Gauge level    : '+str(round(value*scale*100,2))+' %')   
    if label=='Li Board number': # for this to work this field needs to be first than others Board fields in the XML
        BMS_nr=value           
    if label=='Li Board Temperature Low':
        v=int(value*scale)
        if v<40:
            attr=curses.A_NORMAL
        else:
            attr=curses.A_STANDOUT        
        if BMS_nr==0:
            stdscr.addstr(12,4,'Board 0: '+str(v)+' C',attr)      
        if BMS_nr==1:
            stdscr.addstr(13,4,'Board 1: '+str(v)+' C',attr)
        if BMS_nr==2:
            stdscr.addstr(14,4,'Board 2: '+str(v)+' C',attr)  
    if label=='Li Board Temperature High':
        v=int(value*scale)
        if v<40:
            attr=curses.A_NORMAL
        else:
            attr=curses.A_STANDOUT
        if BMS_nr==0:
            stdscr.addstr(12,19,str(v)+' C',attr)      
        if BMS_nr==1:
            stdscr.addstr(13,19,str(v)+' C',attr)
        if BMS_nr==2:
            stdscr.addstr(14,19,str(v)+' C',attr)         
    if label=='Li Board Temperature Amb':
        if BMS_nr==0:
            stdscr.addstr(12,25,str(int(value*scale))+' C')      
        if BMS_nr==1:
            stdscr.addstr(13,25,str(int(value*scale))+' C')
        if BMS_nr==2:
            stdscr.addstr(14,25,str(int(value*scale))+' C')  
    if label=='Li Board Low Cell Voltage':
        if BMS_nr==0:
            stdscr.addstr(12,31,str(round(value*scale,3)))
        if BMS_nr==1:
            stdscr.addstr(13,31,str(round(value*scale,3)))
        if BMS_nr==2:
            stdscr.addstr(14,31,str(round(value*scale,3)))
    if label=='Li Board Low Cell':
        if BMS_nr==0:
            stdscr.addstr(12,37,str(int(value*scale))+' ')
        if BMS_nr==1:
            stdscr.addstr(13,37,str(int(value*scale))+' ')
        if BMS_nr==2:
            stdscr.addstr(14,37,str(int(value*scale))+' ')  
    if label=='Li Board Hi Cell Voltage':
        v=value*scale
        if v<=4.13:
            attr=curses.A_NORMAL
        else:
            attr=curses.A_STANDOUT
        if BMS_nr==0:
            stdscr.addstr(12,43,str(round(v,3)),attr)
        if BMS_nr==1:
            stdscr.addstr(13,43,str(round(v,3)),attr)
        if BMS_nr==2:
            stdscr.addstr(14,43,str(round(v,3)),attr)
    if label=='Li Board Hi Cell':
        if BMS_nr==0:
            stdscr.addstr(12,49,str(int(value*scale))+' ')
        if BMS_nr==1:
            stdscr.addstr(13,49,str(int(value*scale))+' ')
        if BMS_nr==2:
            stdscr.addstr(14,49,str(int(value*scale))+' ')
    if label=='Motor Controller Temp':
        stdscr.addstr(17,4,'Temp: '+str(int(value*scale))+' C')
    if label=='Cap1 Temperature':
        stdscr.addstr(17,16,str(int(value*scale))+' C')        
    if label=='Cap2 Temperature':
        stdscr.addstr(17,22,str(int(value*scale))+' C')  
    if label=='Cap3 Temperature':
        stdscr.addstr(17,28,str(int(value*scale))+' C')    
    if label=='Cell 5 Voltage[0]':          
        stdscr.addstr(7,61,'Cell  1: '+str(round(value*scale,3)))
    if label=='Cell 5 Voltage[1]':
        stdscr.addstr(8,61,'Cell  2: '+str(round(value*scale,3)))
    if label=='Cell 5 Voltage[2]':
        stdscr.addstr(9,61,'Cell  3: '+str(round(value*scale,3)))
    if label=='Cell 5 Voltage[3]':
        stdscr.addstr(10,61,'Cell  4: '+str(round(value*scale,3)))
    if label=='Cell 5 Voltage[4]':
        stdscr.addstr(11,61,'Cell  5: '+str(round(value*scale,3))) 
    if label=='Cell 10 Voltage[0]':
        stdscr.addstr(12,61,'Cell  6: '+str(round(value*scale,3)))
    if label=='Cell 10 Voltage[1]':
        stdscr.addstr(13,61,'Cell  7: '+str(round(value*scale,3)))
    if label=='Cell 10 Voltage[2]':
        stdscr.addstr(14,61,'Cell  8: '+str(round(value*scale,3)))
    if label=='Cell 10 Voltage[3]':
        stdscr.addstr(15,61,'Cell  9: '+str(round(value*scale,3)))
    if label=='Cell 10 Voltage[4]':
        stdscr.addstr(16,61,'Cell 10: '+str(round(value*scale,3)))
    if label=='Cell 15 Voltage[0]':           
        stdscr.addstr(7,77,str(round(value*scale,3)))
    if label=='Cell 15 Voltage[1]':
        stdscr.addstr(8,77,str(round(value*scale,3)))
    if label=='Cell 15 Voltage[2]':
        stdscr.addstr(9,77,str(round(value*scale,3)))
    if label=='Cell 15 Voltage[3]':
        stdscr.addstr(10,77,str(round(value*scale,3)))
    if label=='Cell 15 Voltage[4]':
        stdscr.addstr(11,77,str(round(value*scale,3))) 
    if label=='Cell 20 Voltage[0]':
        stdscr.addstr(12,77,str(round(value*scale,3)))
    if label=='Cell 20 Voltage[1]':
        stdscr.addstr(13,77,str(round(value*scale,3)))
    if label=='Cell 20 Voltage[2]':
        stdscr.addstr(14,77,str(round(value*scale,3)))
    if label=='Cell 20 Voltage[3]':
        stdscr.addstr(15,77,str(round(value*scale,3)))
    if label=='Cell 20 Voltage[4]':
        stdscr.addstr(16,77,str(round(value*scale,3)))
    if label=='Cell 25 Voltage[0]':
        stdscr.addstr(7,84,str(round(value*scale,3)))
    if label=='Cell 25 Voltage[1]':
        stdscr.addstr(8,84,str(round(value*scale,3)))
    if label=='Cell 25 Voltage[2]':
        stdscr.addstr(9,84,str(round(value*scale,3)))
    if label=='Cell 25 Voltage[3]':
        stdscr.addstr(10,84,str(round(value*scale,3)))
    if label=='Cell 25 Voltage[4]':
        stdscr.addstr(11,84,str(round(value*scale,3))) 
    if label=='Cell 30 Voltage[0]':
        stdscr.addstr(12,84,str(round(value*scale,3)))
    if label=='Cell 30 Voltage[1]':
        stdscr.addstr(13,84,str(round(value*scale,3)))
    if label=='Cell 30 Voltage[2]':
        stdscr.addstr(14,84,str(round(value*scale,3)))
    if label=='Cell 30 Voltage[3]':
        stdscr.addstr(15,84,str(round(value*scale,3)))
    if label=='Cell 30 Voltage[4]':
        stdscr.addstr(16,84,str(round(value*scale,3)))# instead of printing, add to the print buffer until a full line is completed

#
# Parses a line of log recorded by the record.py script
#
def parse(count,line,lastTIME,Elapsed,Verbose,FilterSA,FilterID):
    t1=line.split("|")
    if len(t1)!=5:
        return ""
    TIME=t1[0].strip()
    ID=t1[1].strip()
    if len(ID)==6: # this is to be compatible with previous captures I made only with 3 bytes
        ID='00'+ID
    SA=ID[6:8]
    LEN=t1[2].strip()
    HEXDATA=t1[3].strip()
    return interpret(count,lastTIME,Elapsed,Verbose,FilterSA,FilterID,TIME,ID,SA,LEN,HEXDATA)

#
# Parses a line of log recorded by the PEAK PCAN View tracer
#
def parsePEAKTrace(count,line,lastTIME,Elapsed,Verbose,FilterSA,FilterID):
    t0=line.split(")")
    if len(t0)!=2:
        return ""
    t1=t0[1].strip().split("  ")
    if len(t1)!=6:
            return ""
    if t1[1].strip() == 'Warng': # skip warning lines
        return ""
    TIME=datetime.datetime.fromtimestamp(float(t1[0].strip()),tz=datetime.timezone.utc).time()
    ID=t1[3].strip()
    SA=ID[6:8]
    LEN=t1[4].strip()
    HEXDATA=t1[5].strip()
    return interpret(count,lastTIME,Elapsed,Verbose,FilterSA,FilterID,TIME,ID,SA,LEN,HEXDATA)

#
# Parses a line of log recorded by the PEAK PCAN View tracer newewr version
#
def parsePEAKTrace2(count,line,lastTIME,Elapsed,Verbose,FilterSA,FilterID):
    if count<16:
        return ""
    t0=line.split("  ")
    if len(t0)==5:    
        t1=t0[3].strip().split(" ")
        TIME=datetime.datetime.fromtimestamp(float(t1[0].strip()),tz=datetime.timezone.utc).time()
        ID=t1[2].strip()
        SA=ID[6:8]
        LEN=t1[4].strip()
        HEXDATA=t0[4].strip()
        return interpret(count,lastTIME,Elapsed,Verbose,FilterSA,FilterID,TIME,ID,SA,LEN,HEXDATA)
    elif len(t0)==4:
        t1=t0[2].strip().split(" ")
        TIME=datetime.datetime.fromtimestamp(float(t1[0].strip()),tz=datetime.timezone.utc).time()
        ID=t1[2].strip()
        SA=ID[6:8]
        LEN=t1[4].strip()
        HEXDATA=t0[3].strip()
        return interpret(count,lastTIME,Elapsed,Verbose,FilterSA,FilterID,TIME,ID,SA,LEN,HEXDATA)
    else:
        # print('t0',len(t0),' COUNT=',count,'line=',line,'t0=',t0)
        return ""

skip=0
def interpret(c,lastTIME,Elapsed,Verbose,FilterSA,FilterID,TIME,ID,SA,LEN,HEXDATA):
    global skip
    count=int(c)
    if not LEN.isnumeric():
        print('LEN: expected a number, but none found. Incorrect format: ',LEN)
        exit(1)

    if FilterID != None and (not ID in FilterID):
        return ""
    if FilterSA != None and (not SA in FilterSA):
        return ""

    if args.sample:
        if skip<int(args.sample[0]):
            skip=skip+1
            count=count-skip
        else:
            skip=0

    # check if there is more than 1 second inactivity and print that (if Elapsed option)
    if Elapsed and lastTIME != "":
        parsedtime=datetime.datetime.strptime(TIME, '%H:%M:%S.%f')
        parserdLastTIME=datetime.datetime.strptime(lastTIME, '%H:%M:%S.%f')
        diffTime=parsedtime-parserdLastTIME
        if diffTime.total_seconds() > 1 or diffTime.total_seconds() < 0:
            print(count,parserdLastTIME,'Diff:',diffTime)

    # convert hex pdu to ASCII for possible print
    hex=''
    ascii=''
    for i in range(int(LEN)):
        car= HEXDATA.split(" ")[i]
        hex = hex + car
        iCar=chr(int(car,16))
        if iCar.isprintable():
            ascii = ascii + iCar
        else:
            ascii = ascii + '.'

    # convert hex pdu string to binnary data
    DATA=binascii.unhexlify(hex)

    if args.m:
        time.sleep(0.02)
        print(chr(27) + "[2J")

    if ID in PGNdict:
        PGNbytes=PGNdict[ID] # get our data (bytes) about this ID
        for byte in PGNbytes: # for each byte already seen in this ID
            if byte=='ALL': # this ID uses all 8 bytes (according with the PGN)
                element=PGNbytes[byte]['ALL']
                printParsedField(count,TIME,ID,element['label'],ascii,None,HEXDATA,Verbose) # print its ASCII representation
                addSA(ID,ascii,element)
            else: # this ID only uses a subset of the 8 bytes (according with the PGN)
                if len(byte)==1: # this ID only uses 1 byte (according with the PGN)
                    for bits in PGNbytes[byte]:
                        if bits=='ALL': # This ID uses all bits in the above byte -> the value is the full byte (according with the PGN)
                            element=PGNbytes[byte][bits]
                            if element['units'] == 'BMS': # its a BMS message decode accordingly
                                c0=float(DATA[0]<<4 | DATA[5]&0x0F)
                                c0=round((c0*1.5)/1000,3)
                                printParsedField(count,TIME,ID,element['label']+'[0]',c0,float(element['scale']),HEXDATA,Verbose)
                                c1=float(DATA[1]<<4 | (DATA[5]&0xF0>>4))
                                c1=round((c1*1.5)/1000,3)                                
                                printParsedField(count,TIME,ID,element['label']+'[1]',c1,float(element['scale']),HEXDATA,Verbose)
                                c2=float(DATA[2]<<4 | (DATA[6]&0x0F))
                                c2=round((c2*1.5)/1000,3)    
                                printParsedField(count,TIME,ID,element['label']+'[2]',c2,float(element['scale']),HEXDATA,Verbose)
                                c3=float(DATA[3]<<4 | (DATA[6]&0xF0>>4))
                                c3=round((c3*1.5)/1000,3)                                 
                                printParsedField(count,TIME,ID,element['label']+'[3]',c3,float(element['scale']),HEXDATA,Verbose)
                                c4=float(DATA[4]<<4 | (DATA[7]&0x0F))
                                c4=round((c4*1.5)/1000,3)                                  
                                printParsedField(count,TIME,ID,element['label']+'[4]',c4,float(element['scale']),HEXDATA,Verbose)
                                addSA(ID,str(c0)+';'+str(c1)+';'+str(c2)+';'+str(c3)+';'+str(c4),element)
                                #printParsedField(count,TIME,ID,element['label'],str(c0)+';'+str(c1)+';'+str(c2)+';'+str(c3)+';'+str(c4),None,HEXDATA,Verbose)
                            else: 
                                printParsedField(count,TIME,ID,element['label'],int(DATA[int(byte)]),float(element['scale']),HEXDATA,Verbose)
                                scalledval=round(int(DATA[int(byte)])*float(element['scale']),2)
                                addSA(ID,scalledval,element)
                        else: # This ID  uses only one bit of the corresponding byte (according with the PGN)
                            if len(bits)==1:
                                element=PGNbytes[byte][bits]
                                val=int(DATA[int(byte)])&2**int(bits)>0
                                printParsedField(count,TIME,ID,element['label'],val,None,HEXDATA,Verbose)
                                addSA(ID,val,element )
                            else: # This ID  uses more than one bit of the corresponding byte (according with the PGN)
                                element=PGNbytes[byte][bits]
                                val=0
                                nbit=0
                                for bit in bits.split(' '):
                                    val=val+(int(DATA[int(byte)]&(2**int(bit)))>>int(bit))*2**nbit
                                    nbit=nbit+1
                                printParsedField(count,TIME,ID,element['label'],val,float(element['scale']),HEXDATA,Verbose)
                                addSA(ID,val, element )
                   
                else: # this ID only uses more than one byte (according with the PGN)
                    element=PGNbytes[byte]['ALL'] # not supporting partial bits of multiple bytes
                    val=0
                    base=0
                    list=byte.split(' ')
                    if element['units'] == 'HH:MM:SS' and len(list) == 3: # its a TimeDate
                        val='{:02d}:{:02d}:{:02d}'.format(DATA[int(list[0])],DATA[int(list[1])],DATA[int(list[2])])
                        printParsedField(count,TIME,ID,element['label'],val,None,HEXDATA,Verbose)
                        addSA(ID,val,element)
                    elif element['units'] == 'BMS': # its a BMS message  decode accordingly
                        # High cell voltage
                        val=((DATA[int(list[1])]&0x0F)<<8)|DATA[int(list[0])] #Bits 11-8 are the lowest 4 bits of 4, bits 7-0 are in byte 3
                        printParsedField(count,TIME,ID,element['label'],val,float(element['scale']),HEXDATA,Verbose)
                        scalledval=round(val*float(element['scale']),3)
                        addSA(ID,scalledval,element)                      
                    else: # regular number
                        list.reverse()
                        for byteX in list:
                            val=val+int(DATA[int(byteX)])*256**base
                            base=base+1
                        printParsedField(count,TIME,ID,element['label'],val,float(element['scale']),HEXDATA,Verbose)
                        scalledval=round(val*float(element['scale']),2)
                        addSA(ID,scalledval,element)

    else: # this ID is not in the PGNDict
        printParsedField(count,TIME,ID,'data',"{} txt={}".format(' '.join('{:02X}'.format(x) for x in DATA),ascii),None,HEXDATA,Verbose)
        if ID in UnlistedPGN:
            UnlistedPGN[ID]['count']=UnlistedPGN[ID]['count']+1
            UnlistedPGN[ID]['lastSeen']=TIME
        else:
            UnlistedPGN[ID]={'count':1,'firstSeen:':TIME,'lastSeen':TIME}

        if ID[6:8] in SAs:
            if not ID in SAs[ID[6:8]]['idList']:
                SAs[ID[6:8]]['idList'].append(ID)
        else:
            SAs[ID[6:8]]={'idList':[ID],'labels':[]}


    printCSVline(count,TIME,ID,SA,HEXDATA,Verbose)
    return TIME


def readPGN(doc):
    pgndict={}
    for node in doc.getElementsByTagName("PGN"):
        id=node.getElementsByTagName('ID')[0].firstChild.data+node.getElementsByTagName('SA')[0].firstChild.data
        if len(id)==6:
            id='00'+id
        element={}
        if id in pgndict:
            element=pgndict[id]
        Bytes=node.getElementsByTagName('Bytes')[0].firstChild.data
        Bits=node.getElementsByTagName('Bits')[0].firstChild.data
        Label=node.getElementsByTagName('Label')[0].firstChild.data
        Scale=node.getElementsByTagName('ScaleFactor')[0].firstChild.data
        Units=node.getElementsByTagName('Units')

        if len(Units)!= 0:
            Units=Units[0].firstChild.data
        else:
            Units=''
        if Bytes in element:
            element[Bytes][Bits]={'label':Label,'scale':Scale,'values':{},'units':Units}
        else:
            element[Bytes]={Bits:{'label':Label,'scale':Scale,'values':{},'units':Units}}
        pgndict[id]=element
    return pgndict

##### Main
## Configure argument parsing
argParser = argparse.ArgumentParser(description='Parse CAN BUS messages according with PGN XML file.')
argParser.add_argument('file', metavar='filename', type=open, nargs='?', default="data.log",
                    help='the log file with CAN BUS messages to be processed (default data.log)')
argParser.add_argument('-p',metavar='PGNfilename', type=open, default="PGN.xml",
                    help='the XML file with the PGN specification (default PGN.xml)')
argParser.add_argument('-pcan',action='store_const',const=True, default=False,help='the log fils is according with PEAK PCAN View dump format.')
argParser.add_argument('-pcan2',action='store_const',const=True, default=False,help='the log fils is according with PEAK PCAN View dump format newer version.')
argParser.add_argument('-v',action='store_const',const=True, default=False,help='verbose')
argParser.add_argument('-vv',action='store_const',const=True, default=False,help='verbose with hex')
argParser.add_argument('-vvv',action='store_const',const=True, default=False,help='verbose with bin')
argParser.add_argument('-f',action='store_const',const=True, default=False,help='follow the file')
argParser.add_argument('-d',action='store_const',const=True, default=False,help='for debugging print the original line')
argParser.add_argument('-o',action='store_const',const=True, default=False,help='outputs a verbose list separated by pipes good for being imported into Excel (it overwrites -v -vv -vvv and does not print the summary (-q))')
argParser.add_argument('-x',action='store_const',const=True, default=False,help='outputs a list separated by TABs with each PGN in a column for Excel (overwrites -o -v -vv -vvv and does not print the summary (-q))')
argParser.add_argument('-xx',action='store_const',const=True, default=False,help='same as -x but values in each line stick until updated')
argParser.add_argument('-xxx',action='store_const',const=True, default=False,help='same as -xx but only starts printing after all columns have values')
argParser.add_argument('-q',action='store_const',const=True, default=False,help='no summary')
argParser.add_argument('-unusedPGN',action='store_const',const=True, default=False,help='show PGNs which are not used in the processed (and filtered) log')
argParser.add_argument('-unlistedPGN',action='store_const',const=True, default=False,help='show only PGNs which are used but not in PGN.xml')
argParser.add_argument('-e',action='store_const',const=True, default=False,help='print timestamps for which messages are separated by more than 1 second')
argParser.add_argument('-c',type=int, default=0,help='the number of lines (inclusive invalid ones) to process (default 0). If c equals 0 all the log will be processed.')
argParser.add_argument('-s',type=int, default=0,help='the number of lines (inclusive invalid ones) to skip before processing (default 0). If greater than -c no lines will be processed.')
argParser.add_argument('-sa',nargs=1,help='filter and only process this Source Address')
argParser.add_argument('-id',nargs=1,help='filter and only process this ID + SA')
argParser.add_argument('-sample',nargs=1,help='merges N lines into a single one')
argParser.add_argument('-m',action='store_const',const=True, default=False,help='monitor a given ID (use with -id and one of -v, -vv, -vvv or -o)')
argParser.add_argument('-service',action='store_const',const=True, default=False,help='show Vectrix service data (hardcoded values not configurable)')
args = argParser.parse_args()

if (args.m and not args.id) or (args.m and (not args.v and not args.vv and not args.vvv and not args.o)):
    argParser.error('-m requires -id and at least -v, -vv, -vvv or -o')


## init variables
verbose=0
if args.v:
    verbose=1
if args.vv:
    verbose=2
if args.vvv:
    verbose=3
if args.o:
    if args.unlistedPGN:
        verbose=200
    else:
        verbose=100
if args.x or args.xx or args.xxx:
    verbose=300
    args.q=True

if args.service:
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.addstr('CAN Bus monitor',curses.A_BOLD)
    stdscr.addstr(10,16,' Temperature')
    stdscr.addstr(11,13,'Low   High  Amb')
    stdscr.addstr(10,33,'Voltage')
    stdscr.addstr(11,31,'Low (Cell)  High (Cell)')  
    stdscr.addstr(16,11,'MC')
    stdscr.addstr(16,16,'Cap1')
    stdscr.addstr(16,22,'Cap2')
    stdscr.addstr(16,28,'Cap3')
    stdscr.addstr(5,70,'Brd 0')
    stdscr.addstr(5,77,'Brd 1')
    stdscr.addstr(5,84,'Brd 2')             


elapsed=args.e
filterSA=args.sa
filterID=args.id

TIME=""
INITTIME=""

## read PGN file into PGNdict
doc = xml.dom.minidom.parse(args.p.name)
PGNdict=readPGN(doc)

## read logfile line by line up to c lines (argument or default)
file=args.file
temp_time=""
last_time=""
count = 0
if args.f:
    file.seek(0,2) # go to the end of the file
while True and (args.c==0 or count < args.c):
    count += 1
    line = file.readline()
    if not line:
        if args.f:
            time.sleep(1/100)
        else:
            break
    if args.d:
        print(line.strip())
    if args.service:
        stdscr.refresh()

    if count>args.s:
        if args.pcan:
            temp_time=parsePEAKTrace(count,line.strip(),last_time,elapsed,verbose,filterSA,filterID)
        elif args.pcan2:
            temp_time=parsePEAKTrace2(count,line.strip(),last_time,elapsed,verbose,filterSA,filterID)
        else:
            temp_time=parse(count,line.strip(),last_time,elapsed,verbose,filterSA,filterID)
    if temp_time != "":
        TIME=temp_time
        last_time=temp_time
    if INITTIME == "":
        INITTIME=TIME
## finish by printing report if not quite mode
if not args.q:
    print("Sampled from {} to {}".format(INITTIME,TIME))
if args.unlistedPGN:
    print("UnlistedPGN: ")
    for pgn in UnlistedPGN:
        print(pgn,UnlistedPGN[pgn])
elif not args.q and not args.o:
    printUsedPGN(True)
    if args.unusedPGN:
        printUsedPGN(False)
    print("UnlistedPGN: ")
    for pgn in UnlistedPGN:
        print(pgn,UnlistedPGN[pgn])
    print("Source Addresses:")
    for sa in SAs:
        print(sa,SAs[sa])
file.close()
if args.x or args.xx or args.xxx:
    print('Line NR\t'+"".join('{}\t'.format(x.strip()) for x in x_labels))
    line_value={}
    for linenr in x_output:
        position=0
        line=str(linenr)+'\t'
        line_value[position]=str(linenr)
        position=position+1
        for l in x_output[linenr]:
            for i in range(position,l):
                line=line+'\t '
                position=position+1
            line=line+str(x_output[linenr][position])
            line_value[position]=str(x_output[linenr][position])
        if args.x:
            print(line)
        elif args.xx:
            line=''
            for val in line_value:
                line=line+line_value[val]+'\t'
            print(line)
        elif args.xxx and position==len(x_labels):
            line=''
            for val in line_value:
                line=line+line_value[val]+'\t'
            print(line)
    
if args.service:
    curses.nocbreak()
    stdscr.keypad(False)
    curses.endwin()
    curses.echo()