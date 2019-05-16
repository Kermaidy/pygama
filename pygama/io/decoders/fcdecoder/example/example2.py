from matplotlib import pyplot
import numpy as np
from fcutils import fcio

# The fcio class is used to open the datafile
io = fcio("th228.fcio")

print("Number of adcs", io.nadcs)
print("Number of samples", io.nsamples)

data = io.traces

start = 0
stop = 12 if io.nadcs > 12 else io.nadcs

#fig, axs = pyplot.subplots(2)

while io.next_event():
	if io.eventnumber > 10:
		break

	print("Event time:", io.eventtime)

	for i, (bl, prebl0, integral, trace) in enumerate(zip(io.baselines, io.prebaselines0, io.integrals, io.traces)):
		pyplot.plot(trace - bl, label="Trace %d" % io.eventnumber)

    #print("FlashCam baseline:", bl)
    #print("FlashCam integrator:", prebl0)
    #print("Legend prebaseline_0:", integral)

#axs[io.eventnumber].plot(trace - bl, label="Trace %d" % i)

#pyplot.ylim(190, 210)
pyplot.xlabel("Time [4 ns]")
pyplot.ylabel("Amplitude [LSB]")
pyplot.legend()
pyplot.show()
