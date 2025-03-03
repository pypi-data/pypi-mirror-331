# DTCV2-utils


This is a library with utilities developed in DTGEO project in DTCV2 for general purpose. This library contains scripts and functions required for:
- ****Input file validation:****  through a json file definition of variables
- ****Log (error) file manager:**** creates and writes the log_file
- ****Meteo utils:**** utilities for meteorological download
- ****ESP utils:**** utilities for Eruption Source Parameters 

For more information related to this package please consult the [Wiki](https://gitlab.geo3bcn.csic.es/dtgeo/WP5-general/dtcv2-utils-base/-/wikis/WP5-utilities) 
## Input file validation

The meteo_inp.py Python script serves as a data validation tool to ensure that input files adhere to predefined criteria specified in an options configuration file (`options.json`). The script validates variables for dependencies, types, and values according to the specifications outlined in the options file.

## Log (error) file manager 

The function constructs a JSON object containing the log message details, including the description, hour, date, type, locator, and code. It then appends this object to the specified log file.

If the log file directory does not exist, a "FATAL ERROR" message is printed, and the script exits.

## Meteo utils

The Python code is part of a system for managing meteorological data and resources. It includes several classes and functions to handle various aspects of the meteorological data retrieval process.

## License

The information of the license is avavilable in the [File](LICENSE.md)

## Project status
In progress
