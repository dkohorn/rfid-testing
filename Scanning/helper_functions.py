from helper_data import RAW_MAX, RAW_MIN, DBM_MAX, DBM_MIN

# Normalize rssi for distance, current range is just 226-181 needs to normalize to -16 to -56.
# Ranges pulled from manual testing and comparison with the scanner sdk app
def normalize_rssi(rssi):
    x1, x2, y1, y2 = RAW_MAX, RAW_MIN, DBM_MAX, DBM_MIN
    normalized_rssi = int(y1 + ((rssi - x1) / (x2 - x1)) * (y2 - y1))
    return normalized_rssi

# Return a list [epc, rssi] that is extracted from a frame 
def extract_epc_rssi(frame):
    frame = frame.hex()

    #Catch incomplete/error frames
    if len(frame) < 44:
        return ["err", 0]
    
    frame = frame[-44:] # Ensure that any leading bits are cut off from the frame (gets rid of headers like "bb")
    frame = frame[2:] # Remove "type" field 
    frame = frame[2:] # Remove "command" field
    frame = frame[4:] # Remove "payload length" field MSB and LSB

    rssi = frame[0:2] # RSSI field is a signal strength indicator field

    rssi = int(rssi, 16)

    frame = frame[8:] # Remove the PC MSB and LSB fields (as well as RSSI), which define extra flags for the tag (dont know what they might be for though)
    frame = frame[:-2] # Remove checksum

    return [frame, rssi] 

def print_totals(tag_collection_data, num_readings, unknown_tag_count):
    print("\nTotals:")
    print(f"{'Name':<35} | {'Frequency':<10} | {'Avg RSSI':<15} | {'Normalize':<15}")
    print("-" * 80)
    for tag in tag_collection_data:
        scans = tag_collection_data[tag][0]

        avg_rssi = int(tag_collection_data[tag][1] / scans)
        normalized_rssi = normalize_rssi(avg_rssi)

        print(f"{tag:<35} | {f'{scans}/{num_readings}':<10} | {avg_rssi:<15} | {normalized_rssi:<15}")
    print(f"{'Unknown, incomplete, or error tag':<35} | {f'{unknown_tag_count}/{num_readings}':<10}")


#CSV data writing
def write_to_csv(tag_name, rssi_raw, rssi_norm, time, output_file):
    output_file.write(f"{tag_name}, {rssi_raw}, {rssi_norm}, {time}\n")

def write_totals_to_csv(tag_collection_data, num_readings, unknown_tag_count, output_file):
    output_file.write("\nTotals:\n")
    output_file.write("Name, Frequency, Avg RSSI, Avg Norm RSSI\n")
    for tag in tag_collection_data:
        scans = tag_collection_data[tag][0]

        avg_rssi = int(tag_collection_data[tag][1] / scans)
        normalized_rssi = normalize_rssi(avg_rssi)

        output_file.write(f"{tag}, {scans}/{num_readings}, {avg_rssi}, {normalized_rssi}\n")
    output_file.write(f"Unknown, {unknown_tag_count}/{num_readings}\n")