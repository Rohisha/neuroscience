# neuroscience

# mooredb.sqlite
channels, events, spikes 

# db.py Sample Commands

import db

### Get contents of table
spikes_table = db.get_data('spikes')  
chan_table = db.get_data('channels')  
events_table = db.get_data('events')  

### Get all spikes (and their area)
all_spikes = db.get_spikes("1=1")

### Get subset of spikes
trial_spikes = db.get_spikes("trialID=2")  
V4_spikes = db.get_spikes("area='V4'")  
FEF_spikes = db.get_spikes("area='FEF'")  

### Get spikes within a certain window of an event
(spike_data is data from the above subset functions)  
event_spikes = db.get_spikes_within_event(spike_data, event ='microsaccade', before_event = 0.3, after_event = 0.5, norm_to_event = False)  
event_spikes = db.get_spikes_within_event(spike_data, event ='fixation', before_event = 0.3, after_event = 0.5, norm_to_event = True)  

### Get firing rates
(spike_data is data from the above subset functions)  
firing_rates = db.get_fr(spike_data, window = 0.05)


