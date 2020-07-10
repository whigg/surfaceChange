#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 21:00:02 2019

@author: ben
"""

import matplotlib.pyplot as plt
import numpy as np
from PointDatabase.mapData import mapData
import scipy.ndimage as snd
import sys
import os

step=sys.argv[1]
if len(sys.argv) > 2:
    defaults_file=os.path.abspath(sys.argv[2])


if step not in ['centers', 'edges','corners']:
    raise(ValueError('argument not known'))
    sys.exit()

xy_jako=(-160000, -2280000)
#out_dir='/Volumes/ice2/ben/ATL14_test/Jako_d2zdt2=5000'
#out_dir='/Volumes/ice2/ben/ATL14_test/Jako_d2zdt2=5000_d3z=0.00001_d2zdt2=1500_RACMO'

XR=[-440000., -120000.]; YR= [-1840000., -1560000.]

Wxy=80000
Hxy=Wxy/2
mask_G=mapData().from_geotif('/Volumes/ice1/ben/GimpMasks_v1.1/GimpIceMask_1km.tif')
mask_G.z=snd.binary_dilation(mask_G.z, structure=np.ones([20, 20], dtype='bool'))

with open(defaults_file,'r') as fid:
    for line in fid:
        if line[0:3]=='-b=':
            out_dir=line.replace('-b=','').rstrip()
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)
step_dir=out_dir+'/'+step
if not os.path.isdir(step_dir):
    os.mkdir(step_dir)


if step=='centers':
    delta_x=[0]
    delta_y=[0]
    symbol='r*'
elif step=='edges':
    delta_x=[-1, 0, 0, 1.]
    delta_y=[0, -1, 1, 0.]
    symbol='bo'
elif step=='corners':
    delta_x=[-1, 1, -1, 1.]
    delta_y=[-1, -1, 1, 1.]
    symbol='ms'
x0=np.unique(np.round(mask_G.x/Hxy)*Hxy)
y0=np.unique(np.round(mask_G.y/Hxy)*Hxy)
x0, y0 = np.meshgrid(x0, y0)

xg=x0.ravel()
yg=y0.ravel()
good=(np.abs(mask_G.interp(xg, yg)-1)<0.1) & (np.mod(xg-xy_jako[0], Wxy)==0) & (np.mod(yg-xy_jako[1], Wxy)==0)

if XR is not None:
    good &= (xg>=XR[0]) & (xg <= XR[1]) & (yg > YR[0]) & (yg < YR[1])

#mask_G.show()
xg=xg[good]
yg=yg[good]
#[xg, yg]=pad_bins([xg, yg], 2, [Wxy/2, Wxy/2])
ind=np.argsort(np.abs(xg+1j*yg-xy_jako[0]-1j*xy_jako[1]))
xg=xg[ind]
yg=yg[ind]
#plt.plot(xg, yg,'g.')
queued=[];
for xy0 in zip(xg, yg):
    for dx, dy in zip(delta_x, delta_y):  
        xy1=np.array(xy0)+np.array([dx, dy])*Hxy
        if tuple(xy1) in queued:
            continue
        else:
            queued.append(tuple(xy1))
        out_file=out_dir+'/%s//E%d_N%d.h5' % (step, xy1[0]/1000, xy1[1]/1000)  
        if not os.path.isfile(out_file):
            #plt.plot(xy0[0], xy0[1],'r*')
            #if np.sqrt((xy1[0]-320000.)**2 + (xy1[1]- -2520000.)**2) > 2.e5:
            #    continue
            #plt.plot(xy1[0], xy1[1],symbol)
            print('python3 ~/git_repos/surfaceChange/ATL11_to_ATL15.py %d %d --%s @%s' % (xy1[0], xy1[1], step, defaults_file))
#plt.show()