#Serial port
PORT = 'COM4'
BAUD_RATE = 115200

#Scanning
SINGLE_POLL_BYTES = bytes.fromhex('BB 00 22 00 00 22 7E')
SCAN_FREQUENCY = 0.10
NUM_READINGS = 600     #Will read once every 0.1 seconds (100 ms)  for 60 seconds (600 readings)


# These will match the EPC hex values to tags from the kit for easier ID during testing
# These were obtained through manual scans and data parsing
known_tags = {
    #'00471118b06026a28e0114346c': "Medium 1",
    #'004717929064269d88010e9392': "Medium 2",
    #'8068940000501a4a9584a57fde': "Large",
    #'801190a50300614bffd47b7d31': "Small",
    #'000017570d0155255013e89a23': "Card",
    '8068940000402eda82fc8105c8': "Metal",
    '80f30200000000d613e4f2ac96': "Small",
    '80f30200000000718da7a146fc': "Circle",
    '80f30200000000ce82ab129d27': "Mini",
}

#Normalization for signal strength readings
RAW_MAX = 226
RAW_MIN = 181
DBM_MAX = -16
DBM_MIN = -56