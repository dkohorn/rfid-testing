from debounce import is_continuously_reading

data_set = {
    0:    -40,    #False
    27:   -30,    #False
    29:   -40,    #False
    30:   -60,    #True
    30.5:  0,     #True
    31:   -60,    #True
    31.8: -60,    #True
    33:   -60,    #False
    34:   -60,    #True
    34.5:  0,     #True
    35:    0,     #True
    38:   -60,    #False
    40:    0,     #False
    55:   -60,    #False
    56:   -60,    #True
    57.1: -60,    #False
    58:   -60,    #True
}

for reading in data_set:
    time = reading
    value = data_set.get(reading)
    print(time, ": ", is_continuously_reading(time, value))