# Rohisha Adke
# November 20, 2016
# Functions for researchers to load data into db, get data out of db

import sqlite3
import numpy as np
import pandas as pd
import scipy.io as sio

sqlite_file = 'mooredb.sqlite'  # name of the sqlite database file
# table_name1 = 'my_table_1'  # name of the table to be created
# table_name2 = 'my_table_2'  # name of the table to be created
# new_field = 'my_1st_column' # name of the column
# field_type = 'INTEGER'  # column data type
'''
# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

# Creating a new SQLite table with 1 column
c.execute('CREATE TABLE {tn} ({nf} {ft})'\
        .format(tn=table_name1, nf=new_field, ft=field_type))

# Creating a second table with 1 column and set it as PRIMARY KEY
# note that PRIMARY KEY column must consist of unique values!
c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
        .format(tn=table_name2, nf=new_field, ft=field_type))

# Committing changes and closing the connection to the database file
conn.commit()
conn.close()
'''

def delete_table(table):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute("DROP TABLE {tn};".format(tn=table))

    conn.commit()
    conn.close()


# Create given table definition
def create_table(table):
    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    if table == 'spikes':
        # Creating a new SQLite table with 1 column
        c.execute('CREATE TABLE spikes (trialID INTEGER PRIMARY KEY, chanID INTEGER, t REAL, spike INTEGER)')

    if table == 'channels':
        # Creating a new SQLite table with 1 column
        c.execute('CREATE TABLE channels (chanID INTEGER PRIMARY KEY)') #, area TEXT)')

    if table == 'events':
        # Creating a new SQLite table with 1 column
        c.execute('CREATE TABLE events (trialID INTEGER PRIMARY KEY, t REAL, event TEXT)')

    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()



def load_file_to_table(matlab_file, ts_variable = 'spikeTimes', attr_table = "channels", ts_table = 'spikes', config_file = None):
    # Take in a configuration file with the chanID attributes you want to get (if they're there), 
    # and the name of the time series data to load, tables you want to load these into,
    # any other parameters and where they're to be found (ex: in the directory name)
    # Should put the parmeters currently in this function into config file
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    file_types = sio.whosmat(matlab_file) 
    print file_types
    #returns tuple with one for each array (or other object) in the file.
    # Each tuple contains the name, shape and data type of the array.

    # If you want all length 1 dimensions squeezed out, try this:
    mat_contents = sio.loadmat(matlab_file, squeeze_me=True)
    # Add filename as a key/value item
    mat_contents['file'] = str(matlab_file)
    attr_vars = mat_contents.keys()
    attr_vars.remove(ts_variable)
    attr_vars.remove('__header__')
    # attr_vars.append("file") #NOTE: change this when know what file names usually mean

    # Put everything in the file besides the given time series data variable in another attributes table for this channel
    # NOTE: if an attribute is not 1D, entire thing will be inserted into the same cell

    # Add each column that isn't ts_variable to channel attributes table (should specify this table in config file)
    for var in attr_vars:
        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN {col} {type};".\
                format(tn = attr_table, col = var, type = "NONE")) # NOTE: everything currently added as blobs (add type input to config file?)
        except:
            pass

    # Add a row in the attr_table for the attr values that are in this file, put these file values into table
    # Include the matlab file name as data source
    #c.execute("INSERT INTO {tn} attr_vars VALUES (mat_contents[attr] for attr in attr_vars)")

    col_names_str = ', '.join(str(col_name) for col_name in attr_vars)
    print col_names_str
    #file_values_string = ', '.join(str(mat_contents[col_name]) for col_name in attr_vars)
    file_values_string = ', '.join("'{}'".format(str(mat_contents[col_name])) for col_name in attr_vars)
    #'"{}"'.format(word)
    print file_values_string

    print("INSERT INTO {tn} ({col_names}) VALUES ({file_values})".\
                format(tn=attr_table, col_names = col_names_str, file_values = file_values_string))

    c.execute("INSERT INTO {tn} ({col_names}) VALUES ({file_values})".\
                format(tn=attr_table, col_names = col_names_str, file_values = file_values_string))

    conn.commit()
    conn.close()

    return mat_contents
    #struct = mat_contents['my_struct']
    #print mat_contents.shape


# Load table with created data
def load_table(table):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    # Create data
    # Create three nd arrays of trialIDs, chanIDs, times, spikes (0/1)
    trialIDs = np.concatenate(([1]*20, [2]*20, [3]*20, [4]*20))
    chanIDs = np.array([1, 2, 3, 4, 5]*16)
    times = np.random.uniform(0.0, 5.0, 80) #[0.001]*5, [0.02]*5, [1.33]*5, [2.54]*5))
    jitter = np.random.random_sample([80])
    times = times + jitter
    spikes = np.array([1]*80)
    areas = np.array(['V4', 'V4', 'FEF', 'V1', 'FEF'])
    e_trials = np.concatenate(([1]*2, [2]*2, [3]*2, [4]*2))
    e_times = np.random.uniform(0.0, 5.0, 8)
    events = np.array(['fixation', 'microsaccade']*4)

    if table == 'spikes':

        for i in range(len(trialIDs)):
            c.execute("INSERT INTO {tn} (trialID, chanID, t, spike) VALUES ({ti}, {ci}, {ts}, {s})".\
                format(tn=table, ti=trialIDs[i], ci = chanIDs[i], ts = times[i], s=spikes[i]))

    if table == 'channels':
        uniq_chanIDs = np.unique(chanIDs)
        for i in range(len(uniq_chanIDs)):
            c.execute("INSERT INTO {tn} (chanID, area) VALUES ({ci}, '{a}')".\
                format(tn=table, ci = uniq_chanIDs[i], a = areas[i]))

    if table == 'events':

        for i in range(len(e_trials)):
            #print("INSERT INTO {tn} (trial_id, t, event) VALUES ({et}, {eti}, '{e}')".\
            #    format(tn=table, et=e_trials[i], eti = e_times[i], e = events[i]))
            c.execute("INSERT INTO {tn} (trialId, t, event) VALUES ({et}, {eti}, '{e}')".\
                format(tn=table, et=e_trials[i], eti = e_times[i], e = events[i]))

    
    conn.commit()
    conn.close()



# Print out all the data in a table
def get_data(table):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute('SELECT * FROM {tn}'.format(tn=table))
    data = c.fetchall()
    print(data)

    conn.commit()
    conn.close()


# HAVE THIS SAVE TO CSV
# Get data where some attribute is true
# area='V4'
# can have "1=1" for all
def get_spikes(subset_criteria = "area='V4'"):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    query = ' '.join((  # note double parens, join() takes an iterable
    "SELECT spikes.trialID, spikes.chanID, spikes.t, channels.area",
    "FROM spikes",
    "INNER JOIN channels",
    "ON spikes.chanID=channels.chanID",
    "WHERE {sc};".format(sc=subset_criteria),
    ))

    c.execute(query) 
    '''
    "SELECT spikes.trialID, spikes.chanID, spikes.t, channels.area FROM spikes"\
        "INNER JOIN channels"\
        "ON spikes.chanID=channels.chanID"\
        "WHERE area='V4';")
        '''
    data = c.fetchall()
    # print(data)

    conn.commit()
    conn.close()

    df = pd.DataFrame(data)
    df.columns = ['trialID', 'chanID', 't', 'area']
    print df

    return data


# Can norm to event or not
def get_spikes_within_event(data, event ='microsaccade', before_event = 0.3, after_event = 0.5, norm_to_event = False):
    df = pd.DataFrame(data)
    #df = pd.DataFrame(data=get_spikes(subset_criteria))
    df.columns = ['trialID', 'chanID', 't', 'area']

    # For each trial, get the time the event happened
    trials = pd.unique(df['trialID'])

    # Get the event times for the trials from the db
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    query = ' '.join((  # note double parens, join() takes an iterable
    "SELECT *",
    "FROM events",
    "WHERE events.event='{ev}';".format(ev=event),
    ))

    c.execute(query) 
    event_times = pd.DataFrame(c.fetchall())
    event_times.columns = ['trialID', 'e_time', 'event']

    print event_times

    spikes_within_event = pd.DataFrame(columns = ['trialID', 'chanID', 't', 'area'])

    for t in trials:
        print t
        if len(event_times[event_times.trialID==t].index)>0:
            trial_times = event_times[event_times.trialID==t]
            time = trial_times['e_time']
            # print t
            # print time
            time = time.iloc[0]
            # print time

            min_spike_time = time - before_event
            max_spike_time = time + after_event
            # print 'min'
            #print min_spike_time[0]

            # print min_spike_time
            relevant_spikes = df.loc[(df['trialID']==t) & (df['t'] > min_spike_time) & (df['t'] < max_spike_time)]
            print (relevant_spikes)
            # print relevant_spikes

            # Norm times by event time
            if norm_to_event:
                relevant_spikes['t']= relevant_spikes['t'] - time

            spikes_within_event = spikes_within_event.append(relevant_spikes)

   
    print spikes_within_event
    return spikes_within_event #must have ['trialID', 'chanID', 't', 'area'] as columns


#Pass in data, window to compute firing rates on (note: currently naming columns)
def get_fr(data, window = 0.05): #subset_criteria = "area='V4'", window = 0.05):
    df = pd.DataFrame(data)
    #df = pd.DataFrame(data=get_spikes(subset_criteria))
    df.columns = ['trialID', 'chanID', 't', 'area']
    print df

    #print pd.rolling_count(df.iloc[:, [2]], 0.5)
    # For each unique trial, unit pair, for each bin between, count how many times are in that bin
    trials = pd.unique(df['trialID'])
    channels = pd.unique(df['chanID'])

    rates = pd.DataFrame(columns = ['trialID', 'chanID', 'bin_start', 'spikes', 'fr'])

    for t in trials:
        for c in channels:
            # Get the timestamps that apply
            # print t
            # print c
            spike_times = df[((df.trialID==t) & (df.chanID==c))]['t']

            if (len(spike_times.index)>0):

                for bin_start in np.arange(0.0, 5.0, window):
                    num_spikes = len(spike_times[((spike_times >= bin_start) & (spike_times < (bin_start + window)))])

                    #print t, c, bin_start, num_spikes

                    row = pd.DataFrame([[t, c, bin_start, num_spikes, (num_spikes/window)]], columns=['trialID', 'chanID', 'bin_start', 'spikes', 'fr'])
                    #pd.DataFrame([[t, c, bin_start, num_spikes, num_spikes/window]])
                    #print df

                    rates = rates.append(row)
                    #print ('appended')
                    #print rates

    print rates #TODO: save to csv

    return rates

