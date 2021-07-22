##### Written by Iroshana Herath #############
##### Jan. 2021 ############

KK = 0.01              ################## Multiplier Value  ##########

import config_master as parametrs
import numpy as np

import zhinst.utils

import matplotlib
import matplotlib.pyplot as graph
from matplotlib.ticker import ScalarFormatter

import os
import sys
import glob

from time import time, sleep, ctime


import serial

apilevel_example = []
err_msg = []
daq = []
device = []

TIMEOUT = 10

TcArr = {'0.01' : 0, '0.03' : 1, '0.1' : 2, '0.3' : 3, '1' : 4, '3' : 5, '10' : 6, '30' : 7, '100' : 8, '300' : 9,
      '1000' : 10, '3000' : 11, '10000' : 12, '30000' : 13, '100000' : 14, '300000' : 15, '1000000' : 16, '3000000' : 17, '10000000' : 18, '30000000' : 19}


if parametrs.labOne_mode :
    
    apilevel_example = 6
    err_msg = "This mode only supports instruments with demodulators."

    (daq, device, _) = zhinst.utils.create_api_session(
            'dev4946', apilevel_example, required_devtype=".*LI|.*IA|.*IS", required_err_msg=err_msg)
    zhinst.utils.api_server_version_check(daq)
    daq.setInt('/%s/demods/0/enable' % device, 1)
    daq.setDouble("/%s/demods/0/rate" % device, 1.0e3)
    daq.setDouble('/%s/demods/0/timeconstant'%device,0.001*parametrs.Tc)
    daq.sync()
    sample_cmd = '/%s/demods/0/sample' % device
else :
    print('SR810 Lock In Amplifier Mode');
    serl = serial.Serial('COM9', 9600, timeout=0.1)  # open serial port
    print(serl.name)         # check which port was really used
    sleep(1)

if parametrs.mode == 1:
    ######### Inputs ##############
    startStep = parametrs.startStep
    endStep = parametrs.endStep
    stepSize =parametrs.stepSize
    iterations = parametrs.iterations

    ###############################

    
    MAXSTEP = 627125
    MAXRX = 5

    #import serial
    import time

    ser = serial.Serial('COM7', 9600, timeout=TIMEOUT)  # open serial port
    print(ser.name)         # check which port was really used
    ser.write(b'B5\r\n'); 
    time.sleep(1)
    ser.close()
    ser = serial.Serial('COM7', 115200, timeout=TIMEOUT)  # open serial port
    ser.write(b'A?\r\n'); 
    time.sleep(1)

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
        labone = []
        
        header = open('config_master.py','r').read()
        if os.path.exists('scans_odl/%s.csv'%parametrs.name):
            import string
            print('Warning: name %s already exists'%(parametrs.name))
            basename = parametrs.name.rstrip(string.digits)
            newname = basename+'_%d'%(len(glob.glob('scans_odl/%s*.csv*'%basename))+1)
            header = header.replace(parametrs.name,newname)  
            parametrs.name = newname
        
        start = int(round(time.time() * 1000))
        for x in range(0, iterations):
            #startit = int(round(time.time() * 1000))
            stepArr = []
            labArr = []
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
                        stepArr.append(line[1:len(line)-2])
                    if line[:4] == 'Done':
                        endop = int(round(time.time() * 1000))
                        timeList.append(endop - start)
                        #print('STEP ', currentStep, ' Success...')
                        #print('Time for STEP = ' + str(endop-startop) + ' ms\n')

                        

                        if parametrs.labOne_mode :
                            sample = daq.getSample(sample_cmd)
                            sample["R"] = np.abs(sample["x"] + 1j * sample["y"])
                            sample["phi"] = np.angle(sample["x"] + 1j * sample["y"])
                            labone.append(sample['R'][0])
                            labArr.append(sample['R'][0])
                        else :
                            serl.write(b'OUTP?1\r\n')
                            sample["x"] = float(serl.readline().decode())
                            serl.write(b'OUTP?2\r\n')
                            sample["y"] = float(serl.readline().decode())
                            sample["R"] = np.abs(sample["x"] + 1j * sample["y"])
                            sample["phi"] = np.angle(sample["x"] + 1j * sample["y"])
                            labone.append(sample['R'])
                            labArr.append(sample['R'])
                        
                        
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
            graph.plot(stepArr, labArr, label = x+1)
        end = int(round(time.time() * 1000))
        
        graph.xlabel('ODL Step')
        graph.ylabel('Voltage (V)')
        graph.title('ODL Motor')
        graph.grid(True)
        #graph.plot(stepList, labone)
        graph.legend(loc='best')
        graph.savefig(r'scans_odl/%s.png'%parametrs.name)
        graph.show()
        
##        sf = ScalarFormatter(useOffset=False)
##        fig,ax = graph.subplots(1,1,figsize=(8,14)) 
##        ax.plot(stepList,labone)
##        ax.yaxis.set_major_formatter(sf)
##        ax.set_xlabel('Current Step')
##        ax.set_ylabel('Volts (mV))')  
##        ax.grid()
##        graph.draw()
##        graph.savefig(r'scans_odl/%s.png'%parametrs.name,bbox_inches='tight')
    
        data = [list(a) for a in zip(stepList, labone)]
        print(len(stepList))
        print(len(labone)) 
        print("Data Array")
        print(data)

        #np.savetxt('scans_odl/%s.csv'%parametrs.name,data,fmt='%e',header='%s\n'%ctime()+header,comments='# ')
        #a = np.array(data)
        np.savetxt('scans_odl/%s.csv'%parametrs.name,data,delimiter=",", fmt = '%s', header='%s\n'%ctime()+header,comments='# ')
        #np.savetxt('scans_odl/%s.csv'%parametrs.name, a, fmt='%e', header='%s\n'%ctime()+header,comments='# ')
        
        print('Total Time for Operation = ' + str(end-start) + ' ms **************')
        print("Step Matrix : ")
        print(stepList)
        print("Time Matrix : ")
        print(timeList)
        
        print('Device Operation Successfully Completed...\n')
        graph.close('all')
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
    if parametrs.labOne_mode == 0 : serl.close()
    print('END of Program\n')

elif parametrs.mode == 2:

    import string
    from ctypes import *
    from ctypes import byref as p, c_int as i
    from scipy.constants import speed_of_light

    resolution = 100
    width = 0.3
    marker = 0.5
    formatter_limits = (-3, 4)

    parametrs.start = parametrs.start * 100
    parametrs.stop = parametrs.stop * 100
    parametrs.step = parametrs.step * 100
    
    
    limits = (-620,19450)  #19450 (-620*256,1947700*256)
    sw_range = (-627*256-243,19477*256+199) #19472 (-627*256-243,1947700*256+199)
    range_st = 0.1 # [m]
    
    matplotlib.rcParams['figure.dpi'] = resolution
    matplotlib.rcParams['lines.linewidth'] = width
    matplotlib.rcParams['lines.marker'] = 'o'
    matplotlib.rcParams['lines.markersize'] = marker
    matplotlib.rcParams['markers.fillstyle'] = 'full'
    matplotlib.rcParams['axes.formatter.limits']  = formatter_limits
    
    
    header = open('config_master.py','r').read()
    if os.path.exists('scans/%s.csv'%parametrs.name):
      print('Warning: name %s already exists'%(parametrs.name))
      basename = parametrs.name.rstrip(string.digits)
      newname = basename+'_%d'%(len(glob.glob('scans/%s*.csv*'%basename))+1)
      header = header.replace(parametrs.name,newname)  
      parametrs.name = newname
      print('Renamed %s'%(parametrs.name)) 
      
    graph.ion()
    fig,ax = graph.subplots()
    ax.set_autoscalex_on(True)
    ax.set_autoscaley_on(True)
    sf = ScalarFormatter(useOffset=False)#True)
    graph.grid()
    graph.gca().yaxis.set_major_formatter(sf)

    T = np.arange(parametrs.start,parametrs.stop + parametrs.step,parametrs.step).astype(float) # [ps] 
    Fs = 1./(T[1]-T[0])
    L = len(T)
    
    def nextpow2(n): 
        return int(np.ceil(np.log2(np.abs(n))))
    NFFT = 2**nextpow2(L)
    f = Fs/2*np.linspace(0,1,NFFT//2+1)

    
    usteps = 1e-12 * ((sw_range[1]-sw_range[0])/range_st) * 2 * speed_of_light
    print(sw_range,usteps)


    
    Xref = 0
    X = (T*usteps - Xref).astype(np.int)
    print(X)
    input_range = (parametrs.start, parametrs.stop, parametrs.step)
    if np.any(T<limits[0]) or np.any(T>limits[1]):
      print('Position Range ERROR...!!! '%limits)
      print('Invalid Inputs... '%T)
      sys.exit()
    s = np.zeros((parametrs.Nmeas,len(X),4))

    if parametrs.labOne_mode :
        for it in range(10): 
            daq.getSample(sample_cmd) # flush

    cwd = os.getcwd()
    os.chdir(r'C:\Program Files\XILab')
    sys.path.append(r'C:\Program Files\XILab')
    from pyximc import lib as pyxl
    import pyximc as pyxi
    os.chdir(cwd)
    dev_enum = pyxl.enumerate_devices(pyxi.EnumerateFlags.ENUMERATE_PROBE) 
    if pyxl.get_device_count(dev_enum)==0: 
        print('Stage Not Found...!!!'); 
        sys.exit()
        
    d = pyxl.open_device(pyxl.get_device_name(dev_enum,0)) 
    pos = pyxi.get_position_t()
    pyxl.get_position(d,byref(pos))
    tpos = 1*pos.Position
    print('Initial Position : ',tpos)
    print(T)

    def test_move(lib, device_id, distance, udistance, mode=1):
        #
        """
        Move to the specified coordinate.

        Depending on the mode parameter, you can set coordinates in steps or feedback counts, or in custom units.
        :param lib: structure for accessing the functionality of the libximc library.
        :param device_id: device id.
        :param distance: the position of the destination.
        :param udistance: destination position in micro steps if this mode is used.
        :param mode:  mode in feedback counts or in user units. (Default value = 1)
        """
        
        if mode:
            print("\nGoing to {0} steps, {1} microsteps".format(distance, udistance))
            result = lib.command_move(device_id, distance, udistance)
        else:
            # udistance is not used for setting movement in custom units.
            print("\nMove to the position {0} specified in user units.".format(distance))
            result = lib.command_move_calb(device_id, c_float(distance), byref(user_unit))


    ax.set_xlim(T[0],T[-1])
    try:
      for imeas in range(parametrs.Nmeas):
        #print('Checkpoint 1')
        for ix,x in enumerate(T):
          #print('Checkpoint 2')
          t0 = time()
          #(_Position,_uPosition) = divmod(x,256)
          pyxl.command_move(d,int(T[ix]),0)       
          pyxl.command_wait_for_stop(d,0)
          #test_move(pyxl, d, int(T[ix]), 0, 1)
          t1 = time()
          #print('Checkpoint 4')
##          if ix<2:
##            sleep(2*parametrs.wait_time) 
##            for t in range(5): sample = daq.getSample(sample_cmd)       
          sleep(parametrs.wait_time)
          

          if parametrs.labOne_mode :
              sample = daq.getSample(sample_cmd)
              R = np.abs(sample['x'] + 1j*sample['y'])
              pos = pyxi.get_position_t()
              pyxl.get_position(d,byref(pos))
              #_pos = float(1.000*pos.Position)
              _pos = float(T[ix])
              s[imeas,ix] = (_pos,sample['x'][0],sample['y'][0],R[0])
              #print(sample)
          else :
              sample = {}
              serl.write(b'OUTP?1\r\n')
              sample["x"] = float(serl.readline().decode())
              serl.write(b'OUTP?2\r\n')
              sample["y"] = float(serl.readline().decode())
              R = np.abs(sample['x'] + 1j*sample['y'])
              

              #print('Check ')
              #print(sample['x'])
              #print(sample['y'])
              #print(R)
              pos = pyxi.get_position_t()
              pyxl.get_position(d,byref(pos))
              _pos = 1.000*pos.Position
              s[imeas,ix] = (_pos,sample['x'],sample['y'],R)
          #sample = daq.getSample(sample_cmd)
          #print('Checkpoint 5')
          
##          print('Check ')
##          print(R) 
##          print(sample['x'])
##          print(sample['y'])
##          print(sample['x'][0])
##          print(sample['y'][0])
##          print(R[0])
          #print('Checkpoint 6')
          
          #print('Checkpoint 7')
          
          #print('Checkpoint 8')
          
          
          #print('Checkpoint 9')
          if ix%5==0:
            graph.clf()
            graph.grid()
            graph.gca().yaxis.set_major_formatter(sf) 
            graph.plot((s[imeas,:ix,0]*KK),s[imeas,:ix,3])
            graph.show()
            graph.pause(0.0001)
          print('%3d %6.3f %6d %2d %.6e   '%(ix,t1-t0,x,_pos,R),end='\r')
      if parametrs.labOne_mode == 0 : serl.close()
      pos = pyxi.get_position_t()
      pyxl.get_position(d,byref(pos))
      tpos = 1.000*pos.Position
      print('Last Position : ',tpos)
      pyxl.close_device(byref(cast(d, POINTER(c_int))))
    except:
      print('Terminated Process...!!!')
      if parametrs.labOne_mode == 0 : serl.close()
      pyxl.close_device(byref(cast(d, POINTER(c_int))))
      m = s[0].T
      m[0] = (m[0]-Xref)*usteps  
      np.savetxt('scans/%s.csv'%parametrs.name,m.T,fmt='%e',header='%s\n'%ctime()+header,comments='# ')

    
    graph.close('all')
 
    
    fig,(ax0,ax1) = graph.subplots(2,1,figsize=(8,14))  
    m = s.mean(0).T
    m[0] = m[0]*KK
    #print(m.T)
    np.savetxt('scans/%s.csv'%parametrs.name,m.T,fmt='%s',header='%s\n'%ctime()+header,comments='# ')
    R = m[3]

    T = list(map(lambda x: x * KK, T))

    ax0.plot(T,R,ms=1,lw=1,ls= '-')
    ax0.yaxis.set_major_formatter(sf)
    ax0.set_xlabel('Step * KK')
    ax0.set_ylabel('R - mean(R[1:%d])'%parametrs.Nbaseline)  
    ax0.grid()

    x = m[1]
    ax1.plot(T,x,ms=1,lw=1,ls= '-',label='X - mean(X[1:%d])'%parametrs.Nbaseline)
    y = m[2]
    ax1.plot(T,y,ms=1,lw=1,ls= '-',label='Y - mean(Y[1:%d])'%parametrs.Nbaseline)
    ax1.yaxis.set_major_formatter(sf)  
    ax1.set_xlabel('Step * KK')
    ax1.set_ylabel('signal [mV]')
    ax1.grid()
    ax1.legend(loc='best')

    
##    DFFT = np.fft.rfft(x-x.mean(),NFFT)/L
##    s = np.abs(DFFT[:NFFT//2+1])
##    g = np.power((s/s[10:L].max()),2) 
##    ax2.plot(f,g)
##    ax2.yaxis.set_major_formatter(sf)  
##    ax2.set_xlim(0,None) 
##    ax2.set_ylim(0,1)
##    ax2.set_xlabel('f [THz]')
##    ax2.set_ylabel('FFT[X-mean(X)]')  
##    ax2.grid()

##    ipeak_position = np.argmax(R)
##    peak_position = int(X[ipeak_position])  
##    pyxl.command_move(d,peak_position,0)
##    pyxl.command_wait_for_stop(d,0)
##    pyxl.get_position(d,p(pos))
##    print('\npeak position: %d %d %d'%(ipeak_position,peak_position,pos.EncPosition))
##    pyxl.close_device(p(i(d)))

    graph.draw()
    graph.savefig(r'scans/%s.png'%parametrs.name,bbox_inches='tight')  
    graph.show()
    
    print('End of Program\n')
