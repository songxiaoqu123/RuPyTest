# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 09:02:53 2019

@author: easixno
"""
import re
import numpy as np
from scipy.fftpack import fft, ifft, fftshift
import matplotlib.pyplot as plt
import time


def load_wf(fileName, filePath='.'):
    # load waveform file as a list of IQ pair
    fileName = filePath + '\\' + fileName
    with open(fileName, "r") as f:
        data = f.read()
        data = data.strip()
        data = data.strip(',')
        data = data.strip()
        data = re.split('\t|\s|,|\t', data)
        float_data = []
        for d in data:
            float_data.append(float(d))
        data = np.array(float_data)
        data = np.array(data[0::2]) + 1j * np.array(data[1::2])  # transform to complex list
    return data


def transform_complexlist_to_byte(data, clock, comment='EASIXNO', copyright ='EASIXNO', fullScale=32767):
    # input data is a list of complex list I + jQ

    binary_list = []
    checksum = 0
    TabType = '{{TYPE: SMU-WV,{}}}'.format(checksum)
    binary_list.append(TabType.encode('ascii'))

    comment = comment
    TabComment = '{{COMMENT: {}}}'.format(comment)
    binary_list.append(TabComment.encode('ascii'))

    copyright = copyright
    TabCopyright = '{{COPYRIGHT: {}}}'.format(copyright)
    binary_list.append(TabCopyright.encode('ascii'))

    date = time.ctime()
    TabDate = '{{DATE: {}}}'.format(date)
    binary_list.append(TabDate.encode('ascii'))

    rmsoffset = calculate_PAR(data)
    peakoffset = 0
    TabLevel = '{{LEVEL OFFS: {}, {}}}'.format(rmsoffset, peakoffset)
    binary_list.append(TabLevel.encode('ascii'))

    clock = clock
    TabClock = '{{CLOCK: {}}}'.format(clock)
    binary_list.append(TabClock.encode('ascii'))

    samples = len(data)
    TabSamples = '{{SAMPLES: {}}}'.format(samples)
    binary_list.append(TabSamples.encode('ascii'))

    waveformlength = int(samples *4 +1)
    TabWaveform = '{{WAVEFORM-{}:#'.format(waveformlength)
    binary_list.append(TabWaveform.encode('ascii'))

    #data list to byte
    scaleFactor = np.max(np.abs(data))

    iqpair = []
    for d in data:
        iqpair.append(np.real(d))
        iqpair.append(np.imag(d))
    iqpair = np.divide(iqpair, scaleFactor)  # max power is normalized to 1
    iqpair = np.floor(np.multiply(iqpair, fullScale))
    iqpair = iqpair.tolist()
    for i in range(len(iqpair)):
        iqpair[i] = int(iqpair[i])
        binary_list.append(iqpair[i].to_bytes(length=2, byteorder='little', signed=True))
    binary_list.append('}'.encode('ascii'))
    iqpairb =b''
    for iq in binary_list:
        iqpairb = iqpairb + iq
    return iqpairb


'''def load_wf_to_complex_list(fileName, filePath=r'..\..\config'):
    data = load_wf(fileName, filePath)
    data = np.array(data[0::2]) + 1j * np.array(data[1::2])
    return data'''



def read_vsa(data):
    if len(data) % 2:
        raise Exception('Number of data should be even')
        return
    data = np.array(data[0::2]) + 1j * np.array(data[1::2])
    return data


def normalize(complexIQ):
    tmp = np.power(complexIQ, 2)
    tmp = np.abs(tmp)
    tmp = np.mean(tmp)
    tmp = np.sqrt(tmp)
    array = complexIQ / tmp
    return array


def to_log10(complexIQ):
    tmp = np.abs(complexIQ)
    tmp = 20 * np.log10(tmp + 1e-2)
    return tmp


def calculate_PAR(complexIQ):
    peak = np.max(np.abs(complexIQ))
    ave = np.sqrt(np.mean(np.abs(np.power(complexIQ, 2))))
    par = to_log10(peak / ave)
    return par


def align_array(inputIQ, outputIQ):
    # tx and tor should be the same length
    N = len(outputIQ)
    relate = np.sum(np.multiply(np.abs(outputIQ), np.abs(inputIQ)))
    for i in range(0, N):
        outputIQ = np.r_[outputIQ[1:N], outputIQ[0]]
        if np.sum(np.multiply(np.abs(outputIQ), np.abs(inputIQ))) > relate:
            relate = np.sum(np.multiply(np.abs(outputIQ), np.abs(inputIQ)))
            tor_tmp = outputIQ
    return tor_tmp


def remove_group_delay(inputIQ, outputIQ):
    idx_all = np.arange(0, len(inputIQ))
    TX = fftshift(fft(inputIQ))
    TOR = fftshift(fft(outputIQ))
    idx = np.where(np.abs(TX) > np.mean(np.abs(TX)))
    idx = idx[0]  # get index data, function 'where return a non-list object'
    TX_est = TX[idx]
    TOR_est = TOR[idx]
    S = np.true_divide(TOR_est, TX_est)
    S_ph = np.unwrap(np.angle(S))
    ####least square method:x = idx, y = S_ph
    x_y_ = np.mean(np.multiply(idx, S_ph))
    x_ = np.mean(idx)
    y_ = np.mean(S_ph)
    x2_ = np.mean(np.power(idx, 2))
    k = (x_y_ - x_ * y_) / (x2_ - np.power(x_, 2))
    b = y_ - k * x_
    S_ph_comp = b + k * idx_all
    TOR = np.multiply(np.exp(-1j * S_ph_comp), TOR)
    outputIQ = ifft(fftshift(TOR))
    return outputIQ


def PaGainPhase(inputIQ, outputIQ):
    # nomallize power of tx and tor to 1
    inputIQ = normalize(inputIQ)
    outputIQ = normalize(outputIQ)
    # align tor to tx
    outputIQ = align_array(inputIQ, outputIQ)
    # remove group delay of tor
    outputIQ = remove_group_delay(inputIQ, outputIQ)
    # calculate par of tor
    par = calculate_PAR(outputIQ)
    # gain is complex, need further calculation out of function
    gain = np.true_divide(outputIQ, (inputIQ + 1e-15))
    ph = np.angle(gain) / np.pi * 180
    return inputIQ, outputIQ, gain, ph, par


def plot_all(inputIQ, outputIQ, InAve, OutAve, title):
    plt.figure(title)
    N = len(inputIQ)
    gain_var = np.true_divide(outputIQ, (inputIQ + 1e-15))
    ph = np.angle(gain_var) / np.pi * 180
    gain_var = to_log10(gain_var)
    gain_var = [i + OutAve - InAve for i in gain_var]

    tx_dbm = to_log10(inputIQ)
    tx_dbm = [i + InAve for i in tx_dbm]
    tor_dbm = to_log10(outputIQ) + OutAve
    tor_dbm = [i + OutAve for i in tor_dbm]

    TX = np.abs(fftshift(fft(inputIQ)))
    TX = to_log10(TX)
    TOR = np.abs(fftshift(fft(outputIQ)))
    TOR = to_log10(TOR)

    # plot time domain data
    ax1 = plt.subplot(2, 2, 1)
    plt.plot(np.abs(fftshift(inputIQ)), '-')
    plt.plot(np.abs(fftshift(outputIQ)), '-')
    plt.title('Time Domain')
    # plt.xlim((-20,20))
    # plt.ylim((-5,5))
    plt.xlabel('Time')
    plt.ylabel('Amplitude(dB)')
    # AMAM
    ax2 = plt.subplot(2, 2, 2)
    plt.plot(tor_dbm, gain_var, '.')
    plt.title('AM-AM')
    plt.xlim((np.max(tor_dbm) - 15, np.max(tor_dbm) + 5))
    plt.ylim((10, 20))
    plt.xlabel('Output Power(dB)')
    plt.ylabel('Gain(dB)')
    # AMPM
    # ax3 = plt.subplot(4,1,3)
    ax3 = plt.subplot(2, 2, 3)
    plt.plot(tor_dbm, ph, '.')
    plt.title('AM-PM')
    plt.xlim((np.max(tor_dbm) - 15, np.max(tor_dbm) + 5))
    plt.ylim((-30, 30))
    plt.xlabel('Output Power(dBm)')
    plt.ylabel('Phase')
    # Spectrum

    ax4 = plt.subplot(2, 2, 4)
    plt.plot(TX)
    plt.plot(TOR)
    plt.title('Spectrum')
    plt.xlim((N / 2 - 30, N / 2 + 30))
    plt.ylim((30, 70))
    plt.xlabel('Frequency')
    plt.ylabel('Amplitude(dB)')


def plot_Rx(freq_list, S21, S11, S22):
    plt.figure('Rx')

    # plot time domain data
    ax1 = plt.subplot(3, 1, 1)
    plt.plot(freq_list, S21, '-')
    plt.title('S21')
    # plt.xlim((-20,20))
    # plt.ylim((-5,5))
    plt.xlabel('Freq')
    plt.ylabel('Amplitude(dB)')

    ax2 = plt.subplot(3, 1, 2)
    plt.plot(freq_list, S11, '-')
    plt.title('S11')
    # plt.xlim((-20,20))
    # plt.ylim((-5,5))
    plt.xlabel('Freq')
    plt.ylabel('Amplitude(dB)')

    ax3 = plt.subplot(3, 1, 3)
    plt.plot(freq_list, S22, '-')
    plt.title('S22')
    # plt.xlim((-20,20))
    # plt.ylim((-5,5))
    plt.xlabel('Freq')
    plt.ylabel('Amplitude(dB)')
