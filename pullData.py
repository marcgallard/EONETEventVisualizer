"""
    Description: Requests the latest natural events and disasters using NASA's
    EONET API. Script also requests Categories and Sources' JSON for 
    presentation purposes. Once requested, EONET will attempt to return the info 
    in GeoJSON format if the rate limit has not been reached, after which the 
    script parses the info. The info is then written to a local folder at the 
    script's location called "output". The file's name is standardized according 
    to when the data was pulled (refer to "determineFileName" function for more 
    details).
    
    Any errors are written to a log file for post review; logs are stored in 
    "./output/logs".

    Input: None (This could be changed to accept script arguments for defining
    where to write the file and if the user would like to pull from specific
    sources)

    Output: GeoJSON file containing EONET info to later be uploaded to Tableau; 
    file located in "./output" folder. Logs stored in "./output/logs" folder
"""

## IMPORTS
from datetime import datetime # For standardizing filenames
import geojson # For transforming JSON data into GeoJSON
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
        Attempts to write the GeoJSON and log files to "[outputLocation]/output" 
        and "[outputLocation]/output/logs" respectively. Will create directories
        if not already created.
            
        Input: File location to write output files to. Will use ".", the current
        location of the script, by default.
        
        Output: Tuple of locations for empty GeoJSON file for GeoJSON data and 
        empty log file for logging purposes
    """
    # Determine output folders
    outputFolder = f"{outputLocation}/output"
    logFolder = f"{outputFolder}/logs"
    
    # Create associated directories if not already created
    Path(outputFolder).mkdir(exist_ok=True)
    Path(logFolder).mkdir(exist_ok=True)
    
    # Figure out file names to use
    geoDataFileName, logFileName = determineFileName()
    geoDataFile = f"{outputFolder}/{geoDataFileName}.geojson"
    logFile = f"{logFolder}/{logFileName}.log"
    
    # Make files; error raised if already exists
    Path(geoDataFile).touch(exist_ok=False)
    Path(logFile).touch(exist_ok=False)
    
    # Return locations for files
    return (geoDataFile, logFile)

def determineFileName():
    """
        Determines the file name to use when writing the GeoJSON data to a file.
        Standard is "[date]_[time]_eonet_data", where [date] is "DD-MM-YYYY" and 
        [time] is "HH-MM-SS". Example: "21-04-2023_15-17-44_eonet_data". Logs
        also use the same file name format, example: "21-04-2023_15-17-44_log".
        
        Returns: Tuple of standardized file names based on current date and time
        for the GeoJSON and log files
    """
    # Grab current date and time and determine filenames
    currentDateTime = datetime.now()
    prefixFileName = currentDateTime.strftime("%d-%m-%Y_T%H-%M-%S_")
    geoFileName = prefixFileName + "eonet_data"
    logFileName = prefixFileName + "log"
    return (geoFileName, logFileName)

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

def parseJSONData(jsonData):
    """
    """
    pass

def requestEONETData(tryTimes = 3, pauseTime = 3, getCategories = False, 
                     getSources = False):
    """
        Requests EONET data from NASA using NASA's EONET API. Will attempt 3
        times in total by default to get data, 3 seconds by default between each
        request. Grabs Events, skips Categories and Sources by default since 
        they rarely change
        
        Input: Positive integer tryTimes for capping number of requests, 
        positive float pauseTime for # of seconds to wait between each request,
        Bool getCategories and getSources to denote whether they should be 
        grabbed
        
        Output: List of dicts containing EONET data in GeoJSON format
    """
    # Determine list of tuples of URLs to try
    listURLs = [("Events", EONETEventsURL)]
    if getCategories:
        listURLs += [("Categories", EONETCategoriesURL)]
    if getSources:
        listURLs += [("Sources", EONETSourcesURL)]
        
    # Go through URL list and attempt to request JSON data from each
    jsonData = {}
    for typeURL, URL in listURLs:
        logging.info(f"Requesting {typeURL} at {URL}")
        responseData = requestHTTPJSON(URL, tryTimes, pauseTime)
        jsonData[typeURL] = responseData
    
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
           
## MAIN
if __name__ == "__main__":

    try:
        
        # Set up output files to check if outputs can be written without issue
        geoDataFile, logFile = createOutputFiles()
        
        # Initialize logging
        setupLogging(logFile)
        logging.info('Main logger initialized')
        
        # Request EONET data
        logging.info('Requesting EONET data')
        EONETData = requestEONETData() # Requests EONET data as a GeoJSON file
        
        # Parse EONET data
        logging.info('Parsing JSON data')
        
        # Attempt to write GeoJSON data
        pass
        
        # Display number of events and disasters parsed + if any were skipped
        pass

    except Exception as error:
        logging.exception("Traceback of error:")
        print("Error! Script failed to execute properly. Refer to log for more"
              " details")
