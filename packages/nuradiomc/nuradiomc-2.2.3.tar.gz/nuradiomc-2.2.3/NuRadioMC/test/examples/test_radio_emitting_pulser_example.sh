#!/bin/bash
set -e
python NuRadioMC/examples/05_pulser_calibration_measurement/radioEmitting_pulser_calibration/A01generate_pulser_events.py

python NuRadioMC/examples/05_pulser_calibration_measurement/radioEmitting_pulser_calibration/runARA02.py \
    emitter_event_list.hdf5 \
    NuRadioMC/examples/05_pulser_calibration_measurement/radioEmitting_pulser_calibration/ARA02Alt.json \
    NuRadioMC/examples/05_pulser_calibration_measurement/radioEmitting_pulser_calibration/config.yaml \
    output.hdf5 output.nur

python NuRadioMC/test/examples/validate_radio_emitter_allmost_equal.py  output.hdf5 \
    NuRadioMC/test/examples/radio_emitter_output_reference.hdf5

rm emitter_event_list.hdf5
# rm output.hdf5
rm output.nur
