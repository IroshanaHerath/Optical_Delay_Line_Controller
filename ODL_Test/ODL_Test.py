#### Written By Iroshana Herath #########
#### Dec. 2020 ######
 
######### Inputs ##############
startStep = 20000
endStep = 22000
stepSize =2000
iterations = 4

###############################

TIMEOUT = 10
MAXSTEP = 627125
MAXRX = 5

import serial
import time

ser = serial.Serial('COM5', 115200, timeout=TIMEOUT)  # open serial port
print(ser.name)         # check which port was really used

def initDevice():
    ser.write(b'FH\r\n')
    cnt = 0
    while cnt < MAXRX:
        line = ser.readline().decode()
        print(line)
        if line[:4] == 'Done':
            print('Find Home Success...\n')
            break
        cnt += 1
    if cnt >= MAXRX:
        print('Find Home Failed...!!!\n')
        #return 0
    time.sleep(1)
    
    ser.write(b'GR\r\n')
    cnt = 0
    while cnt < MAXRX:
        line = ser.readline().decode()
        print(line)
        if line[:4] == 'Done':
            print('Go To Home Success...\n')
            break
        cnt += 1
    if cnt >= MAXRX:
        print('Go To Home Failed...!!!\n')
        return 0
##    line = ser.readline().decode()
##    print(line)
##    line = ser.readline().decode()
##    print(line)
##    if line[:4] == 'Done':
##        print('Go To Home Success...\n')
##    else :
##        print('Go To Home Failed...!!!\n')
##        return 0
    time.sleep(1)
    
    ser.write(b'S?\r\n')
    cnt = 0
    flag = 0
    while cnt < MAXRX:
        line = ser.readline().decode()
        print(line)
        if line[:6] == 'STEP:0':
            print('Home STEP Count is Valid...\n')
            flag = 1        
        if flag == 1 and line[:4] == 'Done':
            print('Home STEP Count Read Done...\n')
            break
        cnt += 1
    if cnt >= MAXRX:
        print('Home STEP Count is InValid...!!!\n')
        return 0
##    line = ser.readline().decode()
##    print(line)
##    line = ser.readline().decode()
##    print(line)
##    if line[:6] == 'STEP:0':
##        print('Home STEP Count is Valid...\n')
##    else :
##        print('Home STEP Count is InValid...!!!\n')
##        return 0
    time.sleep(1)

    ser.write(b'T?\r\n')
    cnt = 0
    flag = 0
    while cnt < MAXRX:
        line = ser.readline().decode()
        print(line)
        if line[:6] == 'TIME:0':
            print('Home TIME Delay is Valid...\n')
            flag = 1        
        if flag == 1 and line[:4] == 'Done':
            print('Home TIME Delay Read Done...\n')
            break
        cnt += 1
    if cnt >= MAXRX:
        print('Home TIME Delay is InValid...!!!\n')
        return 0
##    line = ser.readline().decode()
##    print(line)
##    line = ser.readline().decode()
##    print(line)
##    line = ser.readline().decode()
##    print(line)
##    if line[:6] == 'TIME:0':
##        print('Home TIME Delay is Valid...\n')
##    else :
##        print('Home TIME Delay is InValid...!!!\n')
##        return 0
    time.sleep(1)
    return 1

def runDevice():
    stepList = []
    timeList = []
    start = int(round(time.time() * 1000))
    for x in range(0, iterations):
        #startit = int(round(time.time() * 1000))
        currentStep = startStep
        if currentStep < 0 or currentStep > MAXSTEP:
            print('Step %d Out of Range...!!!\n')
            return 0

        numSteps = abs(endStep - startStep)/abs(stepSize) + 1
        #print('Total Steps = ' , numSteps, "\n")

        for y in range(0, int(numSteps)):
            #print('Current Step : ', currentStep, '\n')
            cmd = 'S' + str(currentStep) + '\r\n'
            startop = int(round(time.time() * 1000))
            #ser.write(b'S')
            ser.write(str(cmd).encode())
            #ser.write(b'\r\n')
            

            cnt = 0

            while cnt < MAXRX:
                line = ser.readline().decode()
                #print(line)
                if line[:1] == 'S':
                    stepList.append(line[1:len(line)-2])
                if line[:4] == 'Done':
                    endop = int(round(time.time() * 1000))
                    timeList.append(endop - start)
                    #print('STEP ', currentStep, ' Success...')
                    #print('Time for STEP = ' + str(endop-startop) + ' ms\n')
                    currentStep += stepSize
                    if currentStep < 0 or currentStep > MAXSTEP:
                        print('Step ', currentStep, ' Out of Range...!!!\n')
                        return 1
                    break
                cnt += 1
            if cnt >= MAXRX:
                print('STEP ', currentStep, ' Failed...!!!\n')
                return 0
##            line = ser.readline().decode()
##            print(line)
##            line = ser.readline().decode()
##            print(line)
##            line = ser.readline().decode()
##            print(line)
##            if line[:4] == 'Done':
##                print('STEP ', currentStep, ' Success...\n')
##                currentStep += stepSize;
##                if currentStep < 0 or currentStep > MAXSTEP:
##                    print('Step ', currentStep, ' Out of Range...!!!\n')
##                    return 1
##            else :
##                print('STEP ', currentStep, ' Failed...!!!\n')
##                return 0
        #endit = int(round(time.time() * 1000))
        #print('Total Time for Complete Iteration = ' + str(endit-startit) + ' ms ---------------')
    end = int(round(time.time() * 1000))
    print('Total Time for Operation = ' + str(end-start) + ' ms **************')
    print("Step Matrix : ")
    print(stepList)
    print("Time Matrix : ")
    print(timeList)
    print('Device Operation Successfully Completed...\n')
    return 1

print('Initializing Device...\n')

if initDevice() == 0:
    print('Problem in Device Initializing...!!!\n')
else :
    if runDevice() == 0:
        print('Device Operation Failed...\n')
       
#ser.write(str(MAXSTEP).encode())     # write a string
#res = runDevice()
ser.close()             # close port
print('END of Program\n')
