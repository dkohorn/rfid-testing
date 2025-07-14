import serial
from serial import SerialException
import time
from datetime import datetime
from helper_functions import normalize_rssi, extract_epc_rssi, print_totals, write_to_csv, write_totals_to_csv
from helper_data import known_tags, NUM_READINGS, SCAN_FREQUENCY, SINGLE_POLL_BYTES, BAUD_RATE, PORT

#dictionary for holding relevant info for each tag, changed through the update_totals function
#formated like tag_name: [scan_count, rssi_count]
tag_collection_data = {}
unknown_tag_count = 0


def update_totals(tag_name, rssi):
    if tag_name in tag_collection_data:
        tag_collection_data[tag_name] = [tag_collection_data[tag_name][0] + 1, tag_collection_data[tag_name][1] + rssi]
    else: 
        tag_collection_data[tag_name] = [1, rssi]

    



print("Enter the name of the file to save data to:")
file_name = input()
if file_name == "":
    file_name = "default"
file_name += ".csv"

output_file = open(file_name, 'w')
todays_date = datetime.now().strftime("%Y-%m-%d")
output_file.write(f"Name, RSSI raw, RSSI norm, Time (sec), , {todays_date}\n")




try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=0.5)

    print(f"Beginning inventory (scan {NUM_READINGS} times every {SCAN_FREQUENCY} seconds)")

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
                
                #track duplicates in a single scan
                duplicates = []
                for frame in frames:
                    if frame:
                        print("Raw:", frame.hex())
                        tag_info = extract_epc_rssi(frame)

                        if tag_info[0] not in duplicates:
                            duplicates.append(tag_info[0])

                            if tag_info[0] in known_tags:
                                norm_rssi = normalize_rssi(tag_info[1])
                                print("EPC:", tag_info[0], "| RSSI:", tag_info[1], "| Norm RSSI:", norm_rssi, "| Name:", known_tags[tag_info[0]])
                                update_totals(known_tags[tag_info[0]], tag_info[1])
                                write_to_csv(known_tags[tag_info[0]], tag_info[1], norm_rssi, i / 10, output_file)
                            else:
                                print("Unknown, incomplete, or error tag")
                                unknown_tag_count += 1
                                write_to_csv("Unknown", "0", "0", i / 10, output_file)
                        
            else:
                print("Error data frame (nothing scanned):", data)

        time.sleep(SCAN_FREQUENCY)

    print_totals(tag_collection_data, NUM_READINGS, unknown_tag_count)
    write_totals_to_csv(tag_collection_data, NUM_READINGS, unknown_tag_count, output_file)

except KeyboardInterrupt:
    print("\nStopping inventory.")
    ser.close()
except SerialException:
    print("\nCould not open serial port. Is your scanner plugged in?")
finally:
    output_file.close()

