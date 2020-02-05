import matplotlib.pyplot as plt
import numpy as np
import h5py
import sys
import time
import argparse

print("")
nevts    = 5 # max number of events to show
fevt     = 0 # first evt to show
mode     = 1 # display mode
filename = './tier1/t1_run117.lh5' # input filename

par = argparse.ArgumentParser(description="lh5 FlashCam data parser")
arg, st, sf = par.add_argument, "store_true", "store_false"
arg("-f", "--file" , nargs=1, help="tier1 filename")
arg("-m", "--mode" , nargs=1, help="[1=print status-2=plot status-3=plot waveform")
arg("-n", "--nevts", nargs=1, help="number of events to show")
arg("-e", "--fevt" , nargs=1, help="first event to show")
args = vars(par.parse_args())

if args['file']:  filename = args['file'][0]
if args['mode']:  mode     = int(args['mode'][0])
if args['nevts']: nevts    = int(args['nevts'][0])
if args['fevt']:  fevt     = int(args['fevt'][0])

f = h5py.File(filename,'r')
dset = f['daqdata']
conf = f['header']

print("Header info: ",conf.keys())
print("Data info: ",dset.keys())

# DAQ status information (1 Hz) loaded into memory (small amount of data)
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

if mode == 1:
    print("")
    print("Data structure:")
    print("  status: ",s_cards.shape,s_environment.shape)
    print("")
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

if mode == 2:
    print("")
    print("Data structure:")
    print("  status: ",s_cards.shape,s_environment.shape)
    print("")
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

if mode == 3:
    nadcs   = conf['nadcs'][0]
    nsamp   = conf['nsamples'][0]
    old_evt = fevt
    nwf     = 0

    print("Plot event built waveforms")
    for evt,t,adc,bl,en,nt in zip(dset['ievt'],dset['timestamp'],dset['channel'],dset['baseline'],dset['energy'],dset['numtraces']):
        if evt < fevt: 
            nwf = nwf+1
            continue
        if evt > fevt + nevts: break
        # Only plot when we reach next event
        if evt != old_evt: 
            print("")            
            plt.xlabel("Time [16 ns]")
            plt.ylabel("Baseline subt. amplitude [LSB]")
            plt.legend(title=("Bkg run117 - event %d" % old_evt))
            plt.show()
            old_evt = evt

        print("  nwf %d evt %d time %f adc %d bl %d energy %d" % (nwf,evt,t,adc,bl,en))
        # build the waveform from flat data
        waveform = dset['waveform']['values']['flattened_data'][nwf*nsamp:(nwf+1)*nsamp]
        plt.plot(np.array(waveform,dtype=np.int32)-bl, label="ch %d - bl = %d" %(adc,bl))
        nwf = nwf+1

    sys.exit()



