import serial
import time

SINGLE_POLL_BYTES = bytes.fromhex('BB 00 22 00 00 22 7E')
MULTIPLE_POLL_BEGIN_BYTES = bytes.fromhex('BB 00 27 00 03 22 27 10 83 7E')
MULTIPLE_POLL_STOP_BYTES = bytes.fromhex('BB 00 28 00 00 28 7E')

SCAN_FREQUENCY = 1

ser = serial.Serial('COM4', 115200, timeout=0.5)

print(f"Beginning inventory (scan every {SCAN_FREQUENCY} seconds)")

try:
    while True:
        ser.write(SINGLE_POLL_BYTES)
        data = ser.read(ser.in_waiting or 1)

        if not data:
            print("\nNothing returned")
        else:
            # Check for frame end marker
            if b'\x7e' in data:
                frames = data.split(b'\x7e') #'7e' is an end of tag marker used to split each seperate tag reading
                for frame in frames:
                    if frame:
                        frame = frame.hex()
                        
                        # Check for error frame
                        if frame == 'bb01ff00011516':
                            print("\nReceived error frame bb01ff00011516 (no RFID scanned or failed CRC check)")
                        else:
                            frame = frame[-44:] # Ensure that any leading bits are cut off from the frame to fix issue of them sometimes not showing up (basically just standardize frame length)
                            frame = frame[2:] # Remove "type" field 
                            frame = frame[2:] # Remove "command" field
                            frame = frame[4:] # Remove "payload length" field MSB and LSB

                            rssi = frame[2:4] # RSSI field is a signal strength indicator field

                            frame = frame[8:] # Remove the PC MSB and LSB fields (as well as RSSI), which define extra flags for the tag (dont know what they might be for though)
                            frame = frame[:-2] # Remove checksum

                            #This should be the EPC value finally (96 bit standard size)
                            print("\nEPC tag hex:", frame)
                            print("Signal strength:", rssi)
            else:
                print("\nError data frame (nothing scanned):", data)

        time.sleep(SCAN_FREQUENCY)

except KeyboardInterrupt:
    print("\nStopping inventory")
finally:
    ser.close()
