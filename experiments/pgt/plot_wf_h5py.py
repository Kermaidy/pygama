import matplotlib.pyplot as plt
import numpy as np
import h5py
import sys

select = 10 # selected event

f = h5py.File('./tier1/t1_run117.lh5','r')
dset = f['daqdata']
conf = f['header']

print("Header info: ",conf.keys())
print("Data info: ",dset.keys())

nadcs=conf['nadcs'][0]
nevts=dset['ievt'].len()
nsamp=conf['nsamples'][0]

print("")
print("nevt x nadcs: ",nevts,nadcs)
print("")

ievt = dset['ievt'][()]
time = dset['timestamp'][()]
numtraces = dset['numtraces'][()]
tracelist = dset['tracelist'][()]
baseline = dset['baseline'][()]
waveform = dset['waveform']['values']['flattened_data'][()].reshape(baseline.shape[0],nsamp)

ntrg = 0

for evt,t,ntraces,adcs in zip(ievt,time,numtraces,tracelist):
    if evt != select: continue
    if evt > select: break
    print("  evt %d time %f adc list" % (evt,t),adcs)
    print("  |")
    for adc in adcs:
        print("  |-> adc %d tigger %d bl %d " % (adc,ntrg,baseline[ntrg]))
        plt.plot(np.array(waveform[ntrg],dtype=np.int32)-baseline[ntrg], label="ch %d - bl = %d" %(adc,baseline[ntrg]))
        ntrg = ntrg+1

print("")
plt.xlabel("Time [16 ns]")
plt.ylabel("Baseline subt. amplitude [LSB]")
plt.legend(title=("Bkg run117 - event %d" % select))
plt.show()

