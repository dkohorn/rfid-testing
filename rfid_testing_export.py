import serial
import time
from collections import defaultdict

SCAN_FREQUENCY = 0.10
NUM_READINGS = 300     #Will read once every 0.1 seconds (100 ms)  for 30 seconds (300 readings)

PORT = 'COM4'

SINGLE_POLL_BYTES = bytes.fromhex('BB 00 22 00 00 22 7E')
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




# Return a list [epc, rssi] that is extracted from a frame 
def extract_epc_rssi(frame):
    frame = frame.hex()

    frame = frame[-44:] # Ensure that any leading bits are cut off from the frame (gets rid of headers like "bb") and the resulting tag is complete
    if len(frame) != 44:
        return ["bad"]

    frame = frame[2:] # Remove "type" field 
    frame = frame[2:] # Remove "command" field
    frame = frame[4:] # Remove "payload length" field MSB and LSB

    rssi = frame[0:2] # RSSI field is a signal strength indicator field

    # Convert rssi to dbm and normalize within range
    # Ranges are based on max and min readings on the reader app and the raw byte from this program
    # This is an approximate formula to do so 
    rssi = int(rssi, 16)
    x1, x2, y1, y2 = 226, 181, -16, -56
    normalized_rssi = y1 + ((rssi - x1) / (x2 - x1)) * (y2 - y1)
    normalized_rssi = int(normalized_rssi)

    frame = frame[8:] # Remove the PC MSB and LSB fields (as well as RSSI), which define extra flags for the tag (dont know what they might be for though)
    frame = frame[:-2] # Remove checksum

    return [frame, normalized_rssi] 


def write_to_csv(tag_name, output_file, reading_num, rssi):
    output_file.write(f"{tag_name}, {rssi}, {reading_num}\n")






print(f"Beginning inventory (scan {NUM_READINGS} times every {SCAN_FREQUENCY} seconds)")
output_file = open('data_output.csv', 'w')
output_file.write("Tag Name, RSSI (dbm), Time (sec)\n")

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
                            write_to_csv(known_tags[tag_info[0]], output_file, i / 10, tag_info[1])
                        else:
                            print("Unknown, incomplete, or error tag")
                            write_to_csv("Blank", output_file, i / 10, "-")
            else:
                print("Error data frame (nothing scanned):", data)
                write_to_csv("Blank", output_file, i / 10, "-")

        time.sleep(SCAN_FREQUENCY)
    

except KeyboardInterrupt:
    print("\nStopping inventory")
finally:
    ser.close()

