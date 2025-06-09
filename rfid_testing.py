import serial
import time

SINGLE_POLL_BYTES = bytes.fromhex('BB 00 22 00 00 22 7E')
MULTIPLE_POLL_BEGIN_BYTES = bytes.fromhex('BB 00 27 00 03 22 27 10 83 7E')
MULTIPLE_POLL_STOP_BYTES = bytes.fromhex('BB 00 28 00 00 28 7E')
PORT = 'COM4'

SCAN_FREQUENCY = 1

# These will match the EPC hex values to tags from the kit for easier ID during testing
epc_name_match = {
    '00471118b06026a28e0114346c': "medium1",
    '004717929064269d88010e9392': "medium2",
    '8068940000501a4a9584a57fde': "large",
    '801190a50300614bffd47b7d31': "small",
    '000017570d0155255013e89a23': "card"
}

medium1_scan_count = 0
medium2_scan_count = 0
large_scan_count = 0
small_scan_count = 0
card_scan_count = 0

medium1_rssi_total = 0
medium2_rssi_total = 0
large_rssi_total = 0
small_rssi_total = 0
card_rssi_total = 0




num_readings = 25

ser = serial.Serial(PORT, 115200, timeout=0.5)

# Return a list [epc, rssi] that is extracted from a frame or None if error frame
def extract_epc_rssi(frame):
    frame = frame.hex()

    if frame == 'bb01ff00011516':
        return None
    else:
        frame = frame[-44:] # Ensure that any leading bits are cut off from the frame to fix issue of them sometimes not showing up (basically just standardize frame length)
        frame = frame[2:] # Remove "type" field 
        frame = frame[2:] # Remove "command" field
        frame = frame[4:] # Remove "payload length" field MSB and LSB

        rssi = frame[2:4] # RSSI field is a signal strength indicator field

        frame = frame[8:] # Remove the PC MSB and LSB fields (as well as RSSI), which define extra flags for the tag (dont know what they might be for though)
        frame = frame[:-2] # Remove checksum

        return [frame, rssi]

def update_totals(tag_name, rssi):
    global medium1_scan_count, medium2_scan_count, large_scan_count, small_scan_count, card_scan_count
    global medium1_rssi_total, medium2_rssi_total, large_rssi_total, small_rssi_total, card_rssi_total

    if tag_name == "medium1":
        medium1_scan_count += 1
        medium1_rssi_total += int(rssi)
    elif tag_name == "medium2":
        medium2_scan_count += 1
        medium2_rssi_total += int(rssi)
    elif tag_name == "large":
        large_scan_count += 1
        large_rssi_total += int(rssi)
    elif tag_name == "small":
        small_scan_count += 1
        small_rssi_total += int(rssi)
    else:
        card_scan_count += 1
        card_rssi_total += int(rssi)
    






print(f"Beginning inventory (scan every {SCAN_FREQUENCY} seconds)")

try:
    for i in range(num_readings + 1):
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
                        
                        if tag_info == None:  
                            print("Received error frame bb01ff00011516 (no RFID scanned or failed CRC check)")
                        else:
                            print("EPC:", tag_info[0], "| RSSI:", tag_info[1], "| Name:", epc_name_match[tag_info[0]])
                            update_totals(epc_name_match[tag_info[0]], tag_info[1])
            else:
                print("Error data frame (nothing scanned):", data)

        time.sleep(SCAN_FREQUENCY)

    print("Totals:\n")
    if (medium1_scan_count > 0):
        print(f"Medium 1 | Scans {medium1_scan_count}/{num_readings} | Avg RSSI = {medium1_rssi_total / medium1_scan_count}")
    if (medium2_scan_count > 0):
        print(f"Medium 2 | Scans {medium2_scan_count}/{num_readings} | Avg RSSI = {medium2_rssi_total / medium2_scan_count}")
    if (large_scan_count > 0):
        print(f"Large | Scans {large_scan_count}/{num_readings} | Avg RSSI = {large_rssi_total / large_scan_count}")
    if (small_scan_count > 0):
        print(f"Small | Scans {small_scan_count}/{num_readings} | Avg RSSI = {small_rssi_total / small_scan_count}")
    if (card_scan_count > 0):
        print(f"Card | Scans {card_scan_count}/{num_readings} | Avg RSSI = {card_rssi_total / card_scan_count}")

except KeyboardInterrupt:
    print("\nStopping inventory")
finally:
    ser.close()

