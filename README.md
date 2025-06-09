# rfid-testing

## Acknowledgements

All code was written by me with the aid of ChatGPT.

## Contents and Purpose

This repository contains code for a connected RFID scanner. This project serves to test the capabilites of the scanner.

## How to Use

Download rfid_testing.py onto a machine and connect an RFID scanner via USB. All output on scanned tags will be displayed to the console after running the program. Ensure ports for serial reading are configured correctly.

## Things to note

- The program will use the single polling method which will run every 1 second. Single polling takes an instant snapshot of all readable tags, so must be called multiple times for a constant reading. The frequency of snapshots can be changed via the SCAN_FREQUENCY variable.
- Though not used in this example, the code also contains definitions for the multiple polling start and stop commmands. Multiple polling will read constantly as opposed to taking single snapshots, only stopping after a command is given.
- The returned data from the sensor is parsed using this documentation: https://github.com/frux-c/uhf_rfid/blob/master/assets/res/MagicRF_M100%26QM100_Firmware_manual_en.pdf 
- The console will output both the EPC bytes and the signal strength on each tag it reads. Comments within the file will detail what data is parsed out of the raw output from the scanner.
- The EPC data returned for each tag seemingly does not conform to the EPC Tag Data Standard, meaning exact serial ID and other company information cannot be directly parsed from the EPC. The following are theories on what the hex output of the EPC value could be:
    - The first 2 digits may define some kind of flags for the tags. Of the 5 flags tested, they displayed either 00 or 80 in this spot.
    - The next 3 digits likely allude to the type of tag scanned. Of the 5 flags tested, 2 of these values matched. The 2 that matched are seemingly identical tags physically, while the others all differ in size and shape.
    - The rest of the data in the EPC tag does not appear to show any patterns to discern information from. However, since these values differ completely, they should be enough to work as IDs on individual tags.
 - The program is designed for testing with the specific 5 tags packaged with the scanner. These values are hard coded into some of the functionality for testing purposes. The program runs 25 iterations of single poll scanning and records signal strength and detection frequency on each iteration. At the end of the iterations, it will display statistics on overall data from the 25 iterations ran. Note that iteration 0 is buffered at the start to capture the initial failed reading on startup.
