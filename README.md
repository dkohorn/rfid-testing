# rfid-testing

## Acknowledgements

All code was written by me with the aid of ChatGPT.

## Contents and Purpose

This repository contains code for a connected RFID scanner. This project serves to test the capabilites of the scanner. Also included is an algorithm that can be called continuously on each data point to report the state of continuity between tag readings.

## How to Use

Download rfid_testing.py onto a machine and connect an RFID scanner via USB. All output on scanned tags will be displayed to the console after running the program and data will be further logged to a .csv file with name of your choosing for each run of the program. Change all of the information within helper_data.py to configure your scanner and desired test methods properly.

## Things to note

- The program will use the single polling method which will run every SCAN_FREQUENCY seconds. Single polling takes an instant snapshot of all readable tags.
- The returned data from the sensor is parsed using this documentation: https://github.com/frux-c/uhf_rfid/blob/master/assets/res/MagicRF_M100%26QM100_Firmware_manual_en.pdf 
- The console will display a raw byte output for each reading in a snapshot, as well as signal strength, EPC tag, and given nicknames for each recognized tag.
- helper_data.py
 - Configure the PORT and BAUD_RATE for your serial reader
 - Configure SCAN_FREQUENCY and NUM_READINGS to specify the speed and count of snapshots taken
 - Add EPC and nicknames to the known_tags dictionary, which can be found through reading the raw byte output in the console on unknown tags, and manually extracting the EPC
 - Update RAW_MAX, RAW_MIN, DBM_MAX, and DBM_MIN, to normalize the raw byte RSSI reading to an equivalent value in dbm (The conversions were obtained through manual testing and a third party scanner app)
- The first reading (#0) always appears as an error, and will not be considered in any further calculations


## Future
- Deal with duplicate readings
- Ensure errors arent logged if an actual tag was also read
- Add color coding to terminal messages