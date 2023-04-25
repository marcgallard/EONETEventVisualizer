"""
    Description: Attempts to homogenize EONET data to only contain Points.
    Categories and Sources JSON files are also parsed for useful info only that 
    will later be used for Tableau (added after data has been homogenized).
    
    Data is read from "./data" by default, though this can later be changed to
    be a script argument or configuration instead. Only 3 files should be in
    the data folder; Events, Categories, and Sources, each following filename
    convention as stated in pullData.py. This may be changed in the future to be
    more intelligent.
    
    Any errors are written to a log file for post review, stored where processed 
    data is in ("./output/[time-based name]", where the time-based folder name 
    is determined in determineFolderName and "." is used by default).

    Input: None (Assumes data is from a folder called 'data', same location as 
    this script. This could be changed to accept a script argument or config
    file that specifies where to read data from)

    Output: Homogenized GeoJSON file of type Point, log, and parsed JSON files; 
    files located in "./output/[time-based name]" folder by default
"""

## IMPORTS
from datetime import datetime # For standardizing filenames
import geopandas as gpd # For exporting GeoJSON files + manipulating them
import json # For reading EONET, Sources, and Categories files
import logging # For logging purposes
from pathlib import Path # For making directories, files, and parsing file names

## CONSTANTS
numDataFiles = 3 # Currently only 3 data files are supported from EONET
geo_crs = "EPSG:4326" # WGS84 coordinate system

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
    eventsFile = f"{outputFolder}/homogenizedEvents.geojson"
    categoriesFile = f"{outputFolder}/parsedCategories.json"
    sourcesFile = f"{outputFolder}/parsedSources.json"
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

def homogenizeData(parsedEONETData):
    """
        Homogenizes EONET Events data. Currently this is limited to making all
        data as geometry type Point. Note that LineString in data is already
        mentioned as a Point, thus coordinates in LineString are duplicates.
        Supported types: Point, LineString
        
        Input: Dict of dicts of parsed EONET data; only 'Events' is used
        
        Output: GeoDataFrame of homogenized Events data
    """
    # Grab Events data from parsedEONETData and import into geopandas data frame
    eventsData = parsedEONETData['Events']
    eventsGDF = gpd.GeoDataFrame.from_features(eventsData["features"], crs=geo_crs)
    
    # Only grab Point geometry entries and exclude 'geometryDates' column
    filtered_gdf = eventsGDF[eventsGDF['geometry'].apply(lambda x : x.geom_type == 'Point')]
    filtered_gdf = filtered_gdf.drop(columns=['geometryDates'])
    
    return filtered_gdf

def improveReadability(homogenizedEvents, parsedEONETData):
    """
        Adds two columns to the homogenized events data: 'simpleCategory' and 
        'simpleSources'. Like the names suggest, they are simple renditions of 
        the event's respective categories and sources info. This was done due to 
        Tableau limited capabilities + only having access to Tableau Public.
        
        Input: GeoDataFrame homogenizedEvents to alter, dict of dicts 
        parsedEONETData for creating the two new columns
        
        Output: Modded GeoDataFrame homogenizedEvents that contains the new 
        columns
    """
    # Adding a simpler version of categories for each event
    categories = parsedEONETData['Categories']
    # Lambda function for mapping to categories column; maps to full title
    getCategory = lambda e : categories[e[0]['id']]['title']
    homogenizedEvents['simpleCategory'] = homogenizedEvents.categories.apply(getCategory)
    
    # Adding a simpler version of sources for each event
    sources = parsedEONETData['Sources']
    # Lambda function for mapping to sources column; maps to full title of sources
    getSources = lambda e : ', '.join([sources[d['id']]['title'] for d in e])
    homogenizedEvents['simpleSources'] = homogenizedEvents.sources.apply(getSources)
    
    return homogenizedEvents

def parseData(EONETData):
    """
        Parses Dict of dicts, each dict entry representing EONET data. In this
        case there should only be 3 at this time: Events, Categories, Sources.
        Events is currently untouched while Categories and Sources are parsed.
        
        Input: Dict of dicts called EONETData
        
        Output: Dict of dicts with parsed data
    """
    parsedEONETData = {}
    
    # Parse events; currently unimplemented as it's not necessary at this time
    parsedEONETData['Events'] = EONETData['Events']
    
    # Parse Categories
    parsedCategories = {}
    for categoryDict in EONETData['Categories']['categories']:
        categoryId = categoryDict['id']
        title = categoryDict['title']
        description = categoryDict['description']
        parsedCategories[categoryId] = {'title': title, 
                                        'description': description}
    parsedEONETData['Categories'] = parsedCategories
    
    # Parse Sources
    parsedSources = {}
    for sourceDict in EONETData['Sources']['sources']:
        sourceId = sourceDict['id']
        title = sourceDict['title']
        source = sourceDict['source']
        parsedSources[sourceId] = {'title': title, 'source': source}
    parsedEONETData['Sources'] = parsedSources
    
    return parsedEONETData

def readData(inputLocation = './data'):
    """
        Reads in GeoJSON + JSON data for Events, Categories, and Sources from
        inputLocation. Assumes files follow standard naming convention as 
        defined in "pullData.py" script.
        
        Input: String inputLocation that defines where data is stored in,
        './data' by default
        
        Output: Dict of Dicts containing each file's respective data
    """
    # Determine list of files in inputLocation
    inputPath = Path(inputLocation)
    files = list(file for file in inputPath.iterdir() if file.is_file())
    
    # Quick sanity check that there are only 3 files
    errorMsg = f"There should only be {numDataFiles} files in {inputLocation}"
    assert len(files) == numDataFiles, errorMsg
    
    # Determine which file is which
    fileLocations = {}
    for file in files:
        fileName = file.name
        tokenizedFileName = fileName.split('.')
        typeFile = tokenizedFileName[0].title() # Grab type of file
        if typeFile not in fileLocations:
            fileLocations[typeFile] = f"./data/{fileName}"
        else:
            errorMsg = f"Detected repeated {typeFile} file in {inputLocation}"
            raise Exception(errorMsg)
            
    # Read in data files
    filesData = {}
    for typeFile in fileLocations:
        with open(fileLocations[typeFile], "r") as inFile:
            filesData[typeFile] = json.load(inFile)
            
    return filesData

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
                    
def writeEONETData(fileLocations, parsedEONETData, homogenizedEvents):
    """
        Attempts to write parsed + homogenized data into their respective
        empty files, the locations of which are specified in fileLocations
        
        Input: Dict with type of EONET data and their respective file location
        called fileLocations, dict of each type of EONET data with the 
        associated data for each called parsedEONETData (ignoring 'Events'),
        GeoDataFrame of homogenized Events
        
        Output: None as the data should be successfully written to each datum's
        respective file
    """
    # First write homogenized data to appropriate file
    with open(fileLocations['Events'], "w") as outFile:
        outFile.write(homogenizedEvents.to_json(drop_id = True, indent = 4))
        
    # Then write parsed Categories and Sources to respective files
    typeList = ['Categories', 'Sources']
    for typeData in typeList:
        
        # Serialize data to JSON
        jsonData = json.dumps(parsedEONETData[typeData], indent=4)
        
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
        
        # Read in GeoJSON + JSON data
        logging.info('Reading in data')
        EONETData = readData()
        
        # Grab relevant info from EONET data (limited to Categories and Sources)
        logging.info('Parsing read EONET data')
        parsedEONETData = parseData(EONETData)
        
        # Homogenize EONET Events and modify info for readability purposes
        homogenizedEvents = homogenizeData(parsedEONETData)
        homogenizedEvents = improveReadability(homogenizedEvents, parsedEONETData)
        
        # Attempt to write GeoDataFrame + JSON data
        logging.info('Writing homogenized EONET data to respective files')
        writeEONETData(fileLocations, parsedEONETData, homogenizedEvents)
        
        # Successful run
        logging.info('Data successfully parsed and homogenized')
        print("EONET data was successfully homogenized and parsed; refer to "
              "'output' folder for data.\n\nExiting script")

    except Exception as error:
        logging.exception("Traceback of error:")
        print("Error! Script failed to execute properly. Refer to log for more"
              " details")
