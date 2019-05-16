
/*========================================================//
date:    Wed Oct 18 14:43:07 CEST 2017
sources: Libs-fc/fcio/fcio.c
//========================================================*/
#ifndef INCLUDED_fcio_h
#define INCLUDED_fcio_h

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

int FCIODebug(int level)
;
#define FCIOReadInt(x,i)        FCIORead(x,sizeof(int),&i)
#define FCIOReadFloat(x,f)      FCIORead(x,sizeof(float),&f)
#define FCIOReadInts(x,s,i)     FCIORead(x,s*sizeof(int),(void*)(i))
#define FCIOReadFloats(x,s,f)   FCIORead(x,s*sizeof(float),(void*)(f))
#define FCIOReadUShorts(x,s,i)  FCIORead(x,s*sizeof(short int),(void*)(i))

#define FCIOWriteInt(x,i)       { int data=(int)(i); FCIOWrite(x,sizeof(int),&data); }
#define FCIOWriteFloat(x,f)     { float data=(int)(f); FCIOWrite(x,sizeof(float),&data); }
#define FCIOWriteInts(x,s,i)    FCIOWrite(x,(s)*sizeof(int),(void*)(i))
#define FCIOWriteFloats(x,s,f)  FCIOWrite(x,(s)*sizeof(float),(void*)(f))
#define FCIOWriteUShorts(x,s,i) FCIOWrite(x,(s)*sizeof(short int),(void*)(i))

#define FCIOMaxChannels 2304
#define FCIOMaxSamples  4000
typedef struct {  // Readout configuration (typically once at start of run)
  int telid;                     // CTA-wide identifier of this camera
  int adcs;                      // Number of FADC channels
  int triggers;                  // Number of trigger channels
  int eventsamples;              // Number of FADC samples per trace
  int adcbits;                   // Number of bits per FADC sample
  int sumlength;                 // Number of samples of the FPGA integrator
  int blprecision;               // Precision of the FPGA baseline algorithm (1/LSB)
  int mastercards;               // Number of master cards
  int triggercards;              // Number of trigger cards
  int adccards;                  // Number of FADC cards
  int gps;                       // GPS mode flag (0: not used, 1: sync PPS and 10 MHz)
} fcio_config;
typedef struct {    // Calibration data and results (typically once at start of run)
  int status;                    // Result of the calibration procedure (0: error, 1: success)
  int upsample;                  // Used upsampling factor
  int presamples;                // Used number of samples before pulse maxima
  float pulseramp;               // Used pulser amplitude (a.u.)
  float threshold;               // Used threshold for peak search (LSB)
  float pz[2304];                // Estimated deconvolution parameters
  float bl[2304];                // Average baselines during calibration (LSB)
  float pos[2304];               // Average peak positions of calibration pulses (samples)
  float max[2304];               // Average pulse heights of calibration pulses (LSB)
  float maxrms[2304];            // RMS of the pulse heights of the calib. pulses (LSB)
  float *traces[2304];           // Accessors for average traces
  float *ptraces[2304];          // Accessors for average de-convolved traces
  float tracebuf[2304 * 4002];   // internal tracebuffer don't use
  float ptracebuf[2304 * 4002];  // internal ptracebuffer don't use
} fcio_calib;
typedef struct {  // Raw event
  int type;                       // 1: Generic event, 2: calibration event
  float pulser;                   // Used pulser amplitude in case of calibration event
  int timeoffset[10];             // [0] the offset in sec between the master and unix
                                  // [1] the offset in usec between master and unix
                                  // [2] the calculated sec which must be added to the master
                                  // [3] the delta time between master and unix in usec
                                  // [4] the abs(time) between master and unix in usec
                                  // [5-9] reserved for future use
  int deadregion[10];             // [0] start pps of the next dead window
                                  // [1] start ticks of the next dead window
                                  // [2] stop pps of the next dead window
                                  // [3] stop ticks of the next dead window
                                  // [4] maxticks of the dead window
                                  // the values are updated by each event but
                                  // stay at the previous value if no new dead region
                                  // has been detected. The dead region window
                                  // can define a window in the future
  int timestamp[10];              // [0] Event no., [1] PPS, [2] ticks, [3] max. ticks
                                  // [5-9] dummies reserved for future use
  unsigned short *trace[2304];    // Accessors for trace samples
  unsigned short *theader[2304];  // Accessors for traces incl. header bytes
                                  // (FPGA baseline, FPGA integrator)
  unsigned short traces[2304 * 4002];  // internal trace storage
} fcio_event;
typedef struct {  // Readout status (~1 Hz, programmable)
  int status;         // 0: Errors occured, 1: no errors
  int statustime[5];  // fc250 seconds, microseconds, CPU seconds, microseconds, dummy
  int cards;          // Total number of cards (number of status data to follow)
  int size;           // Size of each status data
  // Status data of master card, trigger cards, and FADC cards (in that order)
  // the environment vars are:
  // 5 Temps in mDeg
  // 5 Voltages in mV
  // 1 main current in mA
  // 1 humidity in o/oo
  // 2 Temps from adc cards in mDeg
  // links are int's which are used in an undefined manner
  // current adc links and trigger links contain:
  // (one byte each MSB first)
  // valleywidth bitslip wordslip(trigger)/tapposition(adc) errors
  // these values should be used as informational content and can be
  // changed in future versions
  struct {
    unsigned int reqid, status, eventno, pps, ticks, maxticks, numenv,
                  numctilinks, numlinks, dummy;
    unsigned int totalerrors, enverrors, ctierrors, linkerrors, othererrors[5];
    int          environment[16];
    unsigned int ctilinks[4];
    unsigned int linkstates[256];
  } data[256];
} fcio_status;
typedef struct {
  fcio_config *config;
  fcio_calib *calib;
  fcio_event *event;
  fcio_status *status;
  int nconfigs;
  int ncalibs;
  int nevents;
  int nstatus;
} FCIODataBuffer;
typedef struct { // FlashCam envelope structure
  void *ptmio;                     // tmio stream
  int magic;                       // Magic number to validate structure
  fcio_config config;
  fcio_calib calib;
  fcio_event event;
  fcio_status status;
  int nconfigs;
  int ncalibs;
  int nevents;
  int nstatus;
  FCIODataBuffer *buffers;
  int nbuffers;
  int cur_buf;
} FCIOData;
// valid record tags
// all other tags are skipped
#define FCIOConfig 1
#define FCIOCalib  2
#define FCIOEvent  3
#define FCIOStatus 4

FCIOData *FCIOOpen(const char *name, int timeout, int buffer)
;
int FCIOClose(FCIOData *x)
;
int FCIOGetRecord(FCIOData* x)
;
FCIODataBuffer *FCIOGetBufferedData(FCIOData *x, int offset)
;
typedef void* FCIOStream;

FCIOStream FCIOConnect(const char *name, int direction, int timeout, int buffer)
;
int FCIODisconnect(FCIOStream x)
;
int FCIOWriteMessage(FCIOStream x, int tag)
;
int FCIOWrite(FCIOStream x, int size, void *data)
;
int FCIOFlush(FCIOStream x)
;
int FCIOReadMessage(FCIOStream x)
;
int FCIORead(FCIOStream x, int size, void *data)
;
typedef struct {
  fcio_config *config;
  fcio_calib *calib;
  fcio_event *event;
  fcio_status *status;
  int last_tag;
} FCIOState;
typedef struct {
  void *stream;
  int nrecords;
  int max_states;
  int cur_state;
  FCIOState *states;
  unsigned int selected_tags;
  int nconfigs;
  int ncalibs;
  int nevents;
  int nstatuses;
  int cur_config;
  int cur_calib;
  int cur_event;
  int cur_status;
  fcio_config *configs;
  fcio_calib *calibs;
  fcio_event *events;
  fcio_status *statuses;
} FCIOStateReader;

FCIOStateReader *FCIOCreateStateReader(
  const char *peer,
  int io_timeout,
  int io_buffer_size,
  unsigned int state_buffer_depth)
;
int FCIODestroyStateReader(FCIOStateReader *reader)
;
int FCIOSelectStateTag(FCIOStateReader *reader, int tag)
;
int FCIODeselectStateTag(FCIOStateReader *reader, int tag)
;
FCIOState *FCIOGetState(FCIOStateReader *reader, int offset)
;
FCIOState *FCIOGetNextState(FCIOStateReader *reader)
;
#ifdef __cplusplus
}
#endif // __cplusplus

#endif
