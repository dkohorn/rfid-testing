import serial
import time
from collections import defaultdict

SCAN_FREQUENCY = 0.10
NUM_READINGS = 300     #Will read once every 0.1 seconds (100 ms)  for 30 seconds (300 readings)

PORT = 'COM4'

SINGLE_POLL_BYTES = bytes.fromhex('BB 00 22 00 00 22 7E')
MULTIPLE_POLL_BEGIN_BYTES = bytes.fromhex('BB 00 27 00 03 22 27 10 83 7E')
MULTIPLE_POLL_STOP_BYTES = bytes.fromhex('BB 00 28 00 00 28 7E')
ser = serial.Serial(PORT, 115200, timeout=0.5)

# These will match the EPC hex values to tags from the kit for easier ID during testing
# These were obtained through manual scans and data parsing
known_tags = {
    '00471118b06026a28e0114346c': "Medium 1",
    '004717929064269d88010e9392': "Medium 2",
    '8068940000501a4a9584a57fde': "Large",
    '801190a50300614bffd47b7d31': "Small",
    '000017570d0155255013e89a23': "Card"
}

#dictionary for holding relevant info for each tag, changed through the update_totals function
#formated like tag_name: [scan_count, rssi_count]
tag_collection_data = {}

unknown_tag_count = 0


# Return a list [epc, rssi] that is extracted from a frame 
def extract_epc_rssi(frame):
    frame = frame.hex()

    frame = frame[-44:] # Ensure that any leading bits are cut off from the frame (gets rid of headers like "bb")
    frame = frame[2:] # Remove "type" field 
    frame = frame[2:] # Remove "command" field
    frame = frame[4:] # Remove "payload length" field MSB and LSB

    rssi = frame[0:2] # RSSI field is a signal strength indicator field

    #! Normalize rssi for distance, current range is just 226-181 needs to normalize to -16 to -56.
    #! This is an approximate formula to do so (after converting to decimal)
    rssi = int(rssi, 16)
    x1, x2, y1, y2 = 226, 181, -16, -56
    normalized_rssi = y1 + ((rssi - x1) / (x2 - x1)) * (y2 - y1)

    frame = frame[8:] # Remove the PC MSB and LSB fields (as well as RSSI), which define extra flags for the tag (dont know what they might be for though)
    frame = frame[:-2] # Remove checksum

    return [frame, normalized_rssi] 


def update_totals(tag_name, rssi):
    if tag_name in tag_collection_data:
        tag_collection_data[tag_name] = [tag_collection_data[tag_name][0] + 1, tag_collection_data[tag_name][1] + rssi]
    else: 
        tag_collection_data[tag_name] = [1, rssi]






print(f"Beginning inventory (scan {NUM_READINGS} times every {SCAN_FREQUENCY} seconds)")

try:
    for i in range(NUM_READINGS + 1): #Add one extra because first scan is always an error scan
        ser.write(SINGLE_POLL_BYTES)
        data = ser.read(ser.in_waiting or 1)

        if not data:
            print("\nNothing returned")
        else:
            print(f"\nReading #{i}")
            # Check for frame end marker
            if b'\x7e' in data:
                frames = data.split(b'\x7e') #'7e' is an end of tag marker used to split each seperate tag reading
                for frame in frames:
                    if frame:
                        tag_info = extract_epc_rssi(frame)

                        if tag_info[0] in known_tags:
                            print("EPC:", tag_info[0], "| RSSI:", tag_info[1], "| Name:", known_tags[tag_info[0]])
                            update_totals(known_tags[tag_info[0]], tag_info[1])
                        else:
                            print("Unknown, incomplete, or error tag")
                            unknown_tag_count += 1
                        
            else:
                print("Error data frame (nothing scanned):", data)

        time.sleep(SCAN_FREQUENCY)

    print("\nTotals:")
    print(f"{'Name':<35} | {'Frequency':<10} | {'Avg RSSI':<15}")
    print("-" * 60)
    for tag in tag_collection_data:
        scans = tag_collection_data[tag][0]
        avg_rssi = int(tag_collection_data[tag][1]) / scans
        print(f"{tag:<35} | {f'{scans}/{NUM_READINGS}':<10} | {avg_rssi:<15}")
    print(f"{'Unknown, incomplete, or error tag':<35} | {f'{unknown_tag_count}/{NUM_READINGS}':<10}")
    

except KeyboardInterrupt:
    print("\nStopping inventory")
finally:
    ser.close()

