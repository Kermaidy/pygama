*** FLASHCAM file reader ***

# File structure:
- Tier0 FlashCam file in ./raw/Run117/
- Tier1 lh5 file      in ./tier1/

# Tier1 production
./process_test.py -ds 0 --daq_to_raw -o -v -n 100

# Plot waveform from selected event
run 'python plot_wf_h5py.py'
