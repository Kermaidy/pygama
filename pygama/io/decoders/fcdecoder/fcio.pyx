cimport fcio_c
cimport numpy as np
import numpy as np

cdef class fcio:
    """
    Simple cython wrapper to the fcio_c library.
    Provides a view into the traces array of the FCIOData struct, so using e.g. matplotlib is simplified.
    As a simple config readout, one can get the number of adcs channels and number of samples with GetSimpleConfig()
    although both values are also provided with the GetTraces().shape.
    """
    
    cdef fcio_c.FCIOData* _thisptr

    def __cinit__(self, name):
        """
        Initializer for the c part of the objects, mallocs the FCIOData structure.
        """
        name = name.encode(u"ascii")
        # cdef const char* c_name = name
        self._thisptr = fcio_c.FCIOOpen(name, 0, 0)
        if self._thisptr == NULL:
            raise MemoryError()

    def __init__ (self, name):
        """
        Initializer for the python part of the object, gets called after __cinit__

        Searches for the first config record in the data file and fills the appropriate data members.
        """
        while fcio_c.FCIOGetRecord(self._thisptr) != 1:
            pass

    def __dealloc__(self):
        fcio_c.FCIOClose(self._thisptr)

    cpdef int next_event(self):
        """
        Gets the next event in the data file loaded into the FCIOData struct.
        Use the .traces property to get a memory view wrapped by an np array to the data traces.
        """
        rc = 1
        while rc > 0:
            rc = fcio_c.FCIOGetRecord(self._thisptr)
            if rc == 3:
                return True
        return False

    def _constructTraces(self):
        """
        Returns an numpy array with a view set to the data fields in the traces array of the FCIOData struct.
        """
        cdef unsigned short [:] trace_view = self._thisptr.event.traces
        nptraces = np.ndarray(shape=(self.nadcs,self.nsamples+2), dtype=np.uint16, offset=4, buffer=trace_view)
        shape = (self.nadcs, self.nsamples)
        strides = ( (self.nsamples+2)*nptraces.itemsize, nptraces.itemsize)
        return np.lib.stride_tricks.as_strided(nptraces, shape=shape, strides=strides, writeable=False)

    def _constructTriggerTraces(self):
        """
        Returns an numpy array with a view set to the triggersum fields in the traces array of the FCIOData struct.
        """
        cdef unsigned short [:] triggertrace_view = self._thisptr.event.traces
        nptraces = np.ndarray(shape=(self.ntriggers,self.nsamples+2), dtype=np.uint16, offset=(4 + 2 * (self.nsamples+2) * self.nadcs), buffer=triggertrace_view)
        shape = (self.ntriggers, self.nsamples)
        strides = ( (self.nsamples+2)*nptraces.itemsize, nptraces.itemsize)
        return np.lib.stride_tricks.as_strided(nptraces, shape=shape, strides=strides, writeable=False)

    def _constructTraceHeader(self, offset=0):
        """
        Returns an numpy array with a view into the integrator header field in the traces array of the FCIOData struct.
        """
        cdef unsigned short [:] baseline_view = self._thisptr.event.traces
        nptraces = np.ndarray(shape=(self.nadcs, self.nsamples+2), dtype=np.uint16, offset=offset, buffer=baseline_view)
        shape = (self.nadcs, )
        strides = ( (self.nsamples+2)*nptraces.itemsize, )
        return np.lib.stride_tricks.as_strided(nptraces, shape=shape, strides=strides, writeable=False).astype(np.int16)

    @property
    def nsamples(self):
        return self._thisptr.config.eventsamples

    @property
    def nadcs(self):
        return self._thisptr.config.adcs

    @property
    def telid(self):
        return self._thisptr.config.telid

    @property
    def ntriggers(self):
        return self._thisptr.config.triggers

    @property
    def adcbits(self):
        return self._thisptr.config.adcbits

    @property
    def sumlength(self):
        return self._thisptr.config.sumlength

    @property
    def blprecision(self):
        return self._thisptr.config.blprecision

    @property
    def mastercards(self):
        return self._thisptr.config.mastercards

    @property
    def triggercards(self):
        return self._thisptr.config.triggercards

    @property
    def adccards(self):
        return self._thisptr.config.adccards

    @property
    def gps(self):
        return self._thisptr.config.gps

    @property
    def traces(self):
        return self._constructTraces()

    @property
    def triggertraces(self):
        return self._constructTriggerTraces()

    @property
    def prebaselines0(self):
        return self._constructTraceHeader(offset=0)

    @property
    def prebaselines1(self):
        return self._constructTraceHeader(offset=2)

    @property
    def average_prebaselines(self):
        return (self.prebaselines0 + self.prebaselines1) / 2.0

    @property
    def baselines(self):
        return self._constructTraceHeader() / self._thisptr.config.blprecision

    @property
    def integrals(self):
        return  ( self._constructTraceHeader(offset=2) - self._constructTraceHeader()) * self._thisptr.config.sumlength / self._thisptr.config.blprecision

    @property
    def eventnumber(self):
        return self._thisptr.event.timestamp[0]

    @property
    def eventtime(self):
        return self._thisptr.event.timestamp[1] + self._thisptr.event.timestamp[2] / (self._thisptr.event.timestamp[3] + 1.0)
    
