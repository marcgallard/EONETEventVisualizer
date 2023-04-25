"""
    Description: Requests the latest natural events and disasters using NASA's
    EONET API. Script also requests Categories and Sources' JSON for 
    presentation purposes. Once requested, EONET will attempt to return the info 
    in GeoJSON format if the rate limit has not been reached. The info is then 
    written to a local folder at the script's location called 
    "./output/[dateTime]", where dateTime is standardized according to date and 
    time script was run. The folder's name is standardized according to when the 
    data was pulled (refer to "determineFileName" function for more details).
    
    Any errors are written to a log file for post review; logs are stored in 
    "./output/logs".

    Input: None (This could be changed to accept script arguments for defining
    where to write the file and if the user would like to pass parameters to the 
    HTTP requests)

    Output: GeoJSON + JSON files containing EONET info; files located in 
    "./output" folder. Logs stored in "./output/logs" folder. Files are either
    "log", "events", "categories", or "sources" (excluding file extension)
"""

## IMPORTS
from datetime import datetime # For standardizing filenames
import json # For parsing data from the API call
import logging # For logging purposes
from pathlib import Path # For making directories and files
import requests # For sending and receiving API calls to EONET API
from requests import HTTPError # In case responses are no good
import time # For waiting between requests

## CONSTANTS
apiBaseURL = "https://eonet.gsfc.nasa.gov/api/v3"
EONETEventsURL = f"{apiBaseURL}/events/geojson"
EONETCategoriesURL = f"{apiBaseURL}/categories"
EONETSourcesURL = f"{apiBaseURL}/sources"

## HELPER FUNCTIONS 

def createOutputFiles(outputLocation="."):
    """
        Attempts to write the GeoJSON, JSON, and log files to 
        "[outputLocation]/output/[folderName]", where [folderName] is determined 
        from "determineFolderName". Will create directories if not already 
        created.
            
        Input: Folder location to write output files to. Will use ".", the 
        current location of the script, by default.
        
        Output: Dict of locations for empty GeoJSON + JSON + log files
    """
    # Determine and create output folder
    folderName = determineFolderName()
    outputRoot = f"{outputLocation}/output"
    outputFolder = f"{outputRoot}/{folderName}"
    
    # Make root output folder and time-based folder
    Path(outputRoot).mkdir(exist_ok=True)
    Path(outputFolder).mkdir(exist_ok=False) # Folder should not already exist
    
    # Figure out file names to use
    eventsFile = f"{outputFolder}/events.geojson"
    categoriesFile = f"{outputFolder}/categories.json"
    sourcesFile = f"{outputFolder}/sources.json"
    logFile = f"{outputFolder}/log.log"
    
    # Make files; error raised if already exists
    fileLocations = {"Events": eventsFile, "Categories": categoriesFile, 
                     "Sources": sourcesFile, "Log": logFile}
    for file in list(fileLocations.values()):
        Path(file).touch(exist_ok=False)
    
    # Return locations for files
    return fileLocations

def determineFolderName():
    """
        Determines the folder name to use when writing the EONET and log data to 
        files. Standard is "DD-MM-YYYY_HH-MM-SS". 
        Example: "21-04-2023_15-17-44".
        
        Returns: String of standardized folder name based on current date and 
        time
    """
    # Grab current date and time and determine folder name
    currentDateTime = datetime.now()
    folderName = currentDateTime.strftime("%d-%m-%Y_T%H-%M-%S")
    return folderName

def setupLogging(logFile):
    """
        Sets up logging with an initial logging message to indicate logger has
        started.
        
        Input: Log file location to start logging in
        
        Returns: None
    """
    # Create logger
    logFormatting = ("%(asctime)s %(levelname)-8s [%(filename)s:function "
                     "%(funcName)s:%(lineno)d] - %(message)s")
    logging.basicConfig(filename=logFile, filemode="w", level=logging.DEBUG, 
                        format=logFormatting)

def requestEONETData(tryTimes = 3, pauseTime = 3):
    """
        Requests EONET data from NASA using NASA's EONET API. Will attempt 3
        times in total by default to get data, 3 seconds by default between each
        request. Grabs Events, Categories, and Sources
        
        Input: Positive integer tryTimes for capping number of requests, 
        positive float pauseTime for # of seconds to wait between each request
        
        Output: List of dicts containing EONET data in GeoJSON + JSON format
    """
    # Determine list of tuples of URLs to try
    listURLs = [("Events", EONETEventsURL), ("Categories", EONETCategoriesURL), 
                ("Sources", EONETSourcesURL)]
        
    # Go through URL list and attempt to request JSON data from each
    jsonData = {}
    for typeURL, URL in listURLs:
        logging.info(f"Requesting {typeURL} at {URL}")
        responseData = requestHTTPJSON(URL, tryTimes, pauseTime)
        jsonData[typeURL] = responseData
        time.sleep(1) # Wait a second between each successful retrieval
    
    return jsonData
        
def requestHTTPJSON(URL, tryTimes, pauseTime):
    """
        Tries to request a resource from URL up to tryTimes; raises an error if 
        unsuccessful. Waits for pauseTime seconds between each request.
        
        Input: String URL to attempt, integer tryTimes for establishing limit
        requests on, positive float pauseTime for waiting given seconds between
        requests
        
        Output: JSON dict received from URL if successful, else an error will be
        raised
    """
    # Starting requests
    success = False
    triedTimes = 0
    while not success and triedTimes < tryTimes:
        response = requests.get(URL)
        if response.status_code == 200:
            success = True # Successful response; no more need to try
        else: # Failed response; try again, up to tryTimes
            logger.info(f"API call #{triedTimes + 1} out of f{tryTimes} not "
                        f"successful; received status code "
                        f"[{response.status_code}]")
            triedTimes += 1
            if triedTimes < tryTimes: # Still more times to try
                time.sleep(pauseTime) # Wait before attempting again
    if not success: # Tried tryTimes yet still failed; can't run rest of script
        response.raise_for_status()
    return response.json()
           
def writeEONETData(fileLocations, EONETData):
    """
        Attempts to write the data stored in EONETData into their respective
        empty files, the locations of which are specified in fileLocations
        
        Input: Dict with type of EONET data and their respective file location
        called fileLocations, and a dict of each type of EONET data with the 
        associated data for each called EONETData
        
        Output: None as the data should be successfully written to each datum's
        respective file
    """
    # Write EONET data to each associated file
    for typeData in EONETData:
        
        # Serialize data to JSON
        jsonData = json.dumps(EONETData[typeData], indent=4)
        
        with open(fileLocations[typeData], "w") as outFile:
            outFile.write(jsonData)
           
## MAIN
if __name__ == "__main__":

    try:
        
        # Set up output files to check if outputs can be written without issue
        fileLocations = createOutputFiles()
        
        # Initialize logging
        setupLogging(fileLocations["Log"])
        logging.info('Main logger initialized')
        
        # Request EONET data
        logging.info('Requesting EONET data')
        print("\nRequesting EONET data...")
        EONETData = requestEONETData()
        print("Data grabbed!")
        
        # Attempt to write GeoJSON + JSON data
        logging.info('Writing EONET data to respective files')
        writeEONETData(fileLocations, EONETData)
        
        # Successful run
        logging.info('Data successfully grabbed')
        print("EONET data was successfully saved; refer to 'output' folder for"
              " data.\n\nExiting script")

    except Exception as error:
        logging.exception("Traceback of error:")
        print("Error! Script failed to execute properly. Refer to log for more"
              " details")
