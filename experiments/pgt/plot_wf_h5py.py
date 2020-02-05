import matplotlib.pyplot as plt
import numpy as np
import h5py
import sys
import time

print("")
max_evt = 5 # max number of events to show
print_status = 0
plot_status = 1
plot_wf = 0

f = h5py.File('./tier1/t1_run117.lh5','r')
dset = f['daqdata']
conf = f['header']

print("Header info: ",conf.keys())
print("Data info: ",dset.keys())

nadcs     = conf['nadcs'][0]
nsamp     = conf['nsamples'][0]

# event-wise data
ievt      = dset['ievt'][()]
timestamp = dset['timestamp'][()]
channel   = dset['channel'][()]
numtraces = dset['numtraces'][()]
tracelist = dset['tracelist'][()]
baseline  = dset['baseline'][()]
energy    = dset['energy'][()]
waveform  = dset['waveform']['values']['flattened_data'][()].reshape(baseline.shape[0],nsamp)

# DAQ status information (1 Hz)
s_status     = dset['s_status'][()]
s_statustime = dset['s_statustime'][()]
s_cputime    = dset['s_cputime'][()]
s_size       = dset['s_size'][()]
s_cards      = dset['s_cards'][()]
s_environment= dset['s_environment'][()]
s_totalerrors= dset['s_totalerrors'][()]
s_ctierrors  = dset['s_ctierrors'][()]
s_enverrors  = dset['s_enverrors'][()]
s_linkerrors = dset['s_linkerrors'][()]
s_othererrors= dset['s_othererrors'][()]

print("")
print("Data structure:")
print("  status: ",s_cards.shape,s_environment.shape)
print("  vectors: ",baseline.shape)
print("  waveform:",waveform.shape)
print("")

ntrg = 0
old_evt = ievt[0]

if(print_status):
    print("Print status information")
    for log in range(0,len(s_status)):
        print("Status:",s_status[log],s_statustime[log],s_cputime[log], end=' sec ')
        print(s_cards[log],end=' cards ')
        print(s_size[log])
        for cd in range(0,s_cards[log]):
            print("  ",cd,end=' ')
            for it in range(0,len(s_environment[log][cd])): 
                if(it<5):    print("  ",s_environment[log][cd][it]/1000, end=' deg ')
                elif(it<11): print("  ",s_environment[log][cd][it]/1000, end=' V ')
                elif(it<12): print("  ",s_environment[log][cd][it]/1000, end=' A ')
                elif(it<13): print("  ",s_environment[log][cd][it]/10  , end=' % ')
                elif(it<15): print("  ",s_environment[log][cd][it]/1000, end=' deg ')
                else:        print("  ",s_environment[log][cd][it]     , end=' ')
            print("err:",s_totalerrors[log][cd],s_enverrors[log][cd],s_ctierrors[log][cd],s_linkerrors[log][cd], end=' ')
            for err in s_othererrors[log][cd]: print(err, end=' ')
            print("")

    sys.exit()

if(plot_status):
    print("Plot status information")
    date = []
    for cputime in s_cputime:
        date.append(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(cputime)))

    fig, axs = plt.subplots(4, 1)
    fig.suptitle("Bkg run117")

    for cd in range(0,s_cards[0]):
        # temperature
        for it in range(0,4): 
            axs[0].plot(date,s_environment[:,cd,it]/1000, marker='o', label="card %d - sens. %d" %(cd,it))
        # voltage
        for it in range(5,10): 
            axs[1].plot(date,s_environment[:,cd,it]/1000, marker='o', label="card %d - sens. %d" %(cd,it))
        # current
        axs[2].plot(date,s_environment[:,cd,11]/1000, marker='o', label="card %d - sens. %d" %(cd,it))
        # humidity
        axs[3].plot(date,s_environment[:,cd,12]/10, marker='o', label="card %d - sens. %d" %(cd,it))

    axs[0].set_ylabel("Temp. [deg]")
    axs[1].set_ylabel("Volt. [V]")
    axs[2].set_ylabel("Curr. [A]")
    axs[3].set_ylabel("Humi. [%]")
    axs[3].set_xlabel("Date")

    for ax in axs:
        ax.grid(True)
        delta=len(date)/5
        ax.set_xticks(np.arange(len(date))[::int(delta)])
        ax.set_xticklabels(date[::int(delta)])

    plt.subplots_adjust(hspace = .1)
    fig.autofmt_xdate()
    plt.show()

    sys.exit()

if(plot_wf):
    print("Plot event waveforms")
    for evt,t,adc,bl,en in zip(ievt,timestamp,channel,baseline,energy):
        if evt > max_evt: break
        if evt != old_evt: 
            print("")
            plt.xlabel("Time [16 ns]")
            plt.ylabel("Baseline subt. amplitude [LSB]")
            plt.legend(title=("Bkg run117 - event %d" % old_evt))
            plt.show()
            old_evt = evt

            print("  ntrg %d evt %d time %f adc %d bl %d energy %d" % (ntrg,evt,t,adc,bl,en))
            plt.plot(np.array(waveform[ntrg],dtype=np.int32)-baseline[ntrg], label="ch %d - bl = %d" %(adc,baseline[ntrg]))
            ntrg = ntrg+1

    sys.exit()


