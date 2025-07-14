REQUIRED_TIMEFRAME = 1 
MIN_DATA_VALUE = -80  
MAX_DATA_VALUE = -10   

def set_parameters(rt=1, mindv=-80, maxdv=-10):
    global REQUIRED_TIMEFRAME, MIN_DATA_VALUE, MAX_DATA_VALUE

    REQUIRED_TIMEFRAME = rt
    MIN_DATA_VALUE = mindv
    MAX_DATA_VALUE = maxdv



previous_valid_time = None       #Used for comparing the required timeframe with the new data point


def is_continuously_reading(current_time, data_value):
    """
    Will use the current data point along with previous data to determine if there is continuity in tag readings from the scanner.

    Arguments:
        current_time: Time in seconds of the reading
        data_value: Value of the reading in dbm

    Returns:
        Boolean: True if there is continuity from the last valid reading, false otherwise
    """
    global previous_valid_time, previous_return_result

    #Valid data received
    if (data_value <= MAX_DATA_VALUE and data_value >= MIN_DATA_VALUE):
        if (previous_valid_time != None and current_time - previous_valid_time <= REQUIRED_TIMEFRAME):
            previous_valid_time = current_time
            return True
        previous_valid_time = current_time
        return False
    
    #No valid data
    else:
        if (previous_valid_time != None and current_time - previous_valid_time <= REQUIRED_TIMEFRAME):
            return True
        return False
    

#Function quirks:
# - Will skip over outlier spikes, unless there are multiple that are within the REQUIRED_TIMEFRAME
# - If there is continuity with an invalid data point between valid points, the function will still return true
# - Due to accounting for these previous quirks, the function will take REQUIRED_TIMEFRAME seconds before and after a valid reading to decide on the next return value. 
#   This means that it will take an extra second after a valid reading before the function realizes it should start or end continuity
    
        

    
    

    




