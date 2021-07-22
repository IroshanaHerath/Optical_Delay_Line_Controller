

import config as parametrs
import os
import sys
import numpy as np

import zhinst.utils

import matplotlib
import matplotlib.pyplot as graph
from matplotlib.ticker import ScalarFormatter

from time import time, sleep
from ctypes import byref as p
from scipy.constants import speed_of_light

resolution = 200
width = 0.3
marker = 0.5
formatter_limits = (-3, 4)

sw_range = (-627*256-243, 19472*256+199)
limits = (-620*256, 19450*256)
range_st = 0.1 

T = np.arange(parametrs.start, parametrs.stop,
              parametrs.step).astype(float)  
L = len(T)

matplotlib.rcParams['figure.dpi'] = resolution
matplotlib.rcParams['lines.linewidth'] = width
matplotlib.rcParams['lines.marker'] = 'o'
matplotlib.rcParams['lines.markersize'] = marker
matplotlib.rcParams['markers.fillstyle'] = 'full'
matplotlib.rcParams['axes.formatter.limits'] = formatter_limits

graph.ion()
fig, ax = graph.subplots()
ax.set_autoscalex_on(True)
ax.set_autoscaley_on(True)
sf = ScalarFormatter(useOffset=False)
graph.grid()
graph.gca().yaxis.set_major_formatter(sf)

usteps = 1e-12 * 2 * speed_of_light * ((sw_range[1]-sw_range[0]) / range_st)
print(sw_range, usteps)

Xref = 0
X = (T*usteps - Xref).astype(np.int)
print(X)

if np.any(X < limits[0]) or np.any(X > limits[1]):
    print('Position Range ERROR...!!! [%d,%d]' % limits)
    sys.exit()
mtx = np.zeros((parametrs.Nmeas, len(X), 4))

apilevel_example = 6
err_msg = "This program only supports instruments with demodulators."
(daq, device, _) = zhinst.utils.create_api_session(
    'dev4946', apilevel_example, required_devtype=".*LI|.*IA|.*IS", required_err_msg=err_msg)
zhinst.utils.api_server_version_check(daq)
daq.setInt('/%s/demods/0/enable' % device, 1)
daq.setDouble('/%s/demods/0/timeconstant' % device, 0.001*parametrs.Tc)

daq.sync()
sample_cmd = '/%s/demods/0/sample' % device
for it in range(10):
    daq.getSample(sample_cmd) 

cwd = os.getcwd()
os.chdir(r'C:\Program Files\XILab')
sys.path.append(r'C:\Program Files\XILab')
from pyximc import lib as pyxl
import pyximc as pyxi
os.chdir(cwd)
dev_enum = pyxl.enumerate_devices(pyxi.EnumerateFlags.ENUMERATE_PROBE)
if pyxl.get_device_count(dev_enum) == 0:
    print('Stage Not Found...!!!')
    sys.exit()

d = pyxl.open_device(pyxl.get_device_name(dev_enum, 0))
pos = pyxi.get_position_t()


ax.set_xlim(T[0], T[-1])
try:
    for imeas in range(parametrs.Nmeas):
        for index, x in enumerate(X):
            t0 = time()
            (_Position, _uPosition) = divmod(x, 256)

            pyxl.command_move(d, int(_Position), int(_uPosition))
            pyxl.command_wait_for_stop(d, 0)
            t1 = time()

            if index < 2:
                sleep(2*parametrs.wait_time)
                for t in range(5):
                    sample = daq.getSample(sample_cmd)
            
            sleep(parametrs.wait_time)
            sample = daq.getSample(sample_cmd)
            R = np.abs(sample['x'] + 1j*sample['y'])
            pyxl.get_position(d, p(pos))
            _pos = 256*pos.Position + pos.uPosition
            mtx[imeas, index] = (_pos, sample['x'][0], sample['y'][0], R[0])

            if index % 5 == 0:
                graph.clf()
                graph.grid()
                graph.gca().yaxis.set_major_formatter(sf)
                graph.plot((mtx[imeas, :index, 0]-Xref)*usteps, mtx[imeas, :index, 3])
                graph.show()
                graph.pause(0.0001)

            print('%3d %6.3f %6d %2d %.6e   ' % (index, t1-t0, x, _pos-x, R), end='\r'),
except:
    print('Terminated Process...!!!')

graph.close('all')
print('End of Program\n')
