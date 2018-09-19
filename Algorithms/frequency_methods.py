# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 20:52:57 2018

@author: Daniel Reimhult

@version: 0.1
"""

import numpy as np
from scipy.signal import butter,lfilter
from test_signal_generation import Signal

def bergeron_derivate(s, startup_periods = 0):
    """ Computes frequency based on Roger Bergeron's suggestion
    using the derivate.
    """
   
    def rk4(x,ts=1):
        fd = []
    
        for n in range(2,len(x)-2):
            fd.append( ( x[n-2] - 8*x[n-1] + 8*x[n+1] - x[n+2] ) / (12*ts) )
            
        fd = [fd[0],fd[1]] + fd +[fd[-2],fd[-1]]
        
        return fd

    ts = s.time[1]-s.time[0]
    fs = 1/ts
    spp = s.samples_per_period

    bp_lp_b, bp_lp_a = butter(4, [70*2/fs], btype='lowpass')
    bp_hp_b, bp_hp_a = butter(4, [50*2/fs], btype='highpass')
    
    vfilt1 = lfilter(bp_lp_b, bp_lp_a, s.values)
    vfilt2 = lfilter(bp_hp_b, bp_hp_a, vfilt1)
    
    vdiff = rk4(vfilt2,ts)

    f = [None]*startup_periods
    for n in range(spp*startup_periods,len(s.values)-spp,spp):
        f.append(max(vdiff[n:n+spp]) / max(vfilt2[n:n+spp]) / (2*np.pi))

    t = s.time[0::spp][0:len(f)]
    return Signal(t, f, s.nom_freq, s.nom_freq)

def dq_phase_angle(s, downsample = 1):
    """ Computes the phase angle using convoluation with the direct and 
    quadrature components.
    """

    spp = s.samples_per_period
    
    sine_d = [np.sin(2*np.pi*i/spp) for i in range(spp)]
    sine_q = [np.sin(2*np.pi*i/spp+np.pi/2) for i in range(spp)]
    
    phase_angle = []
    t = []
    for i in range(spp, len(s.values), downsample):
        d = np.dot(sine_d, s.values[i-spp:i])
        q = np.dot(sine_q, s.values[i-spp:i])
        t.append(s.time[i])
        phase_angle.append(np.arctan2(q,d))
        
    return Signal(t,phase_angle,s.sample_rate/downsample)

def synchrophasor_frequency(s, startup_periods = 0):
    """ Computes the frequency based on phase angles.
    """
    
    phase_angles = dq_phase_angle(s, downsample = s.samples_per_period)

    f = s.nom_freq + 1/(2*np.pi/s.nom_freq)*np.diff(phase_angles.values)
    t = phase_angles.time[0:len(f)]

    return Signal(t, f, s.nom_freq, s.nom_freq)

def filtered_zerocrossing(s, startup_periods = 0):
    """ Computes the frequency based on the zero crossings after band pass
    filtering the signal.
    """

    ts = s.time[1]-s.time[0]
    fs = 1/ts

    bp_lp_b, bp_lp_a = butter(2, [70*2/fs], btype='lowpass')
    bp_hp_b, bp_hp_a = butter(2, [50*2/fs], btype='highpass')
    
    vfilt1 = lfilter(bp_lp_b, bp_lp_a, s.values)
    vfilt2 = lfilter(bp_hp_b, bp_hp_a, vfilt1)

    zc = [i for i,j in enumerate(np.diff(np.sign(vfilt2))) if j > 0]
    t = [s.time[i] for i in zc]
    t = t[1:]

    f = fs / np.diff(zc)
    f[0:startup_periods] = [None]
    
    return Signal(t, f, s.nom_freq, s.nom_freq)

def phase_separation(s, limit, downsample = 1):
    """ Separates the phase angle changes into phi and psi, where phi contains 
    ideally slow changes expected in the power system during normal operation 
    and psi contains the abrupt changes related to some external event.
    """

    phi = [s.values[0]]
    psi = [0]
    t = [s.time[0]]
    
    phdiff = np.diff(s.values)
    
    dtot = 0
    for i,pd in enumerate(phdiff):
        if abs(pd) > limit:
            psi.append(pd)
            phi.append(phi[-1]-dtot)
            dtot += pd
        else:
            psi.append(psi[-1])
            phi.append(s.values[i]-dtot)

        t.append(s.time[i])

    return Signal(t,phi,s.sample_rate/downsample),Signal(t,psi,s.sample_rate/downsample)

def separated_frequency(s):
    ph_sig = dq_phase_angle(s, downsample = s.samples_per_period)
    phi_sep, psi_sep = phase_separation(ph_sig, 0.05, downsample = 1)
    freq_sep = Signal(phi_sep.time[1:], 
               [s.nom_freq+phi_sep.sample_rate*((a+np.pi) % (2*np.pi) - np.pi) \
                    / (2*np.pi) for a in np.diff(phi_sep.values)], 
               phi_sep.sample_rate)
    
    return freq_sep
