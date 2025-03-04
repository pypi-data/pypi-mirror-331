#/usr/bin/python3

# from marlin_utils import *


# from marlin_data.marlin_data import MarlinDerivedData
# from marlin_data.marlin_data import MarlinDataStreamer
# from marlin_data.marlin_data import MarlinData

from marlin_data import *

# --- Build f profile from marlin_adapter fourier & fast index ---

sim_ids = ["595319575884544847440835"] #HP snapshot (10s)
locations = ['67149847']

# only if you want to save locally
simulation_data_path = "/Users/vixen/rs/dev/sim"

# create data adapter and download
data_adapter = MarlinData(load_args={'limit' : 10000})
sim_ids  =data_adapter.download_simulation_snapshots(load_args={'simulation_path':simulation_data_path, 'location':locations,  "time_start" : "140822_145029.000" , "time_end" : "140822_185029.000"}, id_only = True)
    



# create iterable datafeed
data_feed = MarlinDataStreamer()

# initialise data feed
data_feed.init_data(data_adapter.simulation_data, data_adapter.simulation_index)

# # define parms for marlin data signal processing
# nfft = 2048 # 65536#2048 #65536
# min_f = 100000
# max_f = 140000

# # indexing parms [splitting fourier data up into a more efficient indexing algorithm for the ML framework]
# delta_t = 0.002
# dd_delta_f = 500

# # build marlin-data adapters for data feed
# for snapshot in data_feed:
#     data_adapter.derived_data = None
#     data_adapter.build_derived_data(n_fft=nfft)
    
#     startt(name="build_derived_data")
#     snapshot_derived_data = data_adapter.derived_data.build_derived_data(simulation_data=snapshot, f_min = min_f, f_max = max_f)
#     stopt(desc="build_derived_data", out = 1)
    
#     # nb. time issue 
#     startt(name="index_fourier")
#     data_adapter.derived_data.ft_build_band_energy_profile(sample_delta_t=delta_t, simulation_data=snapshot, discrete_size = 500)
#     stopt(desc="index_fourier")
    

# get snapshots for locaiton and time

       
    



