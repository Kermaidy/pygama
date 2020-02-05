*** FLASHCAM file reader ***

# File structure:
- Tier0 FlashCam file in ./raw/Run117/
- Tier1 lh5 file      in ./tier1/

# Tier1 production
- mv ./tier1/t1_run117. ./tier1/t1_run117.lh5
- ./process_test.py -ds 0 --daq_to_raw -o -v -n 999

# Plot waveform from selected event
- check ['print_status','plot_stauts','plot_wf'] flags in 'plot_wf_h5py.py'
- run 'python plot_wf_h5py.py'
