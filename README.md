# neuroscience

# mooredb.sqlite
channels, events, spikes 

# db.py Sample Commands

import db

### Get contents of table
spikes_table = db.get_data('spikes')

chan_table = db.get_data('channels')

events_table = db.get_data('events')

### Get all spikes (joined to area)
all_spikes = db.get_spikes("1=1")

### Get subset of spikes
trial_spikes = db.get_spikes("trialID=2")

V4_spikes = db.get_spikes("area='V4'")

FEF_spikes = db.get_spikes("area='FEF'")


### Get

