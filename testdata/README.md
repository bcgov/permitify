# Permitify - Generating/Loading Test Data into TheOrgBook

## Overview

This folder contains reference and test data for Permitify, and a mechanism for managing and generating the reference and test data files that can be imported into the TheOrgBook.

## Requirements

The data generation and import scripts require Python 3 to run.

[PipEnv](https://pipenv.readthedocs.io/en/latest/) is used to simplify dependency management for the scripts. Please refer to PipEnv's guide to install it.

Once PipEnv is installed, run `pipenv sync` from within the `testdata` folder to create the virtual environment and, once the dependencies have been installed, `pipenv shell` to start it.

Please note that under Linux the python executable is called `python3`.

## Generating the Test Data

Test data can be generated using an Excel spreadsheet and parsing it using the provided `xls2json.py` script.

1. Create a new excel spreadsheet containing as many sheets as the different types of credentials that require generating. Make sure the sheet is named exactly as the scema corresponding to the credential that will be inserted, followed by `.csv` (e.g.: registration.permitify.csv for the credential using the registration.permitify schema).
    * It is recommended that a sub-folder is used to store the Excel spreadsheet, as the resulting test data will be stored at the same level as the source spreadsheet.
2. Populate the spreadsheet, creating a column for each item in the schema. The column header should be named **exactly** as the schema element it corresponds to.
3. Once the spreadsheet contains the desired data, create the ready-to-import JSON files using the `xls2json.py` script. Open a shell inside the folder containing the Excel spreadsheet, and run the following command:
```
python ../xls2json.py MY_SPREADSHEET.xls
```
4. The command will create a sub-folder containing JSON data for each one of the sheets containing a data definition.

### Loading the Test Data

Once the data is generated, the `loadClaims.py` script can be used to import it into the instance of TheOrgBook supporting Permitify. From the `testdata` folder, run the following command:
```
AGENT_URL=<AGENT_URL> python loadClaims.py <DATA_FOLDER>
```
Where *AGENT_URL* is the endpoint for the agent that will issue the credential (e.g.: https://devex-von-permitify-dev.pathfinder.gov.bc.ca/bcreg for the BC Registries agent), and <DATA_FOLDER> is the folder containing the test data to be imported (e.g.: ***permitify-data***).
