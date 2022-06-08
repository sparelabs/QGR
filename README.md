# Automated Quarterly Goal Review
Project Owner: Joe Gaspari 

### GOAL
 With a growing customer base, and diversified customer needs Spare’s Partner Success team will need a system of reporting that allows for reduced preparation time, and lesser need for data understanding. The result of a more efficient system would provide the PSM’s with:
Reduced QGR report creation time
More time focused on customer needs
Stress free reporting

### Value 
The process currently involves PSM’s alternating between multiple pages within Spare Analyze to acquire single metrics that are most often logged into a single CSV or Excel file. The automated report will ask the PSM for an API-key associated with the organization. The report will also ask the PSM for the start date of the quarter they are interested in. The value of the automated report will be in an aggregated CSV file that will be downloadable to the user. This CSV file or xlsx file will include all KPI’s required by PSM’s to execute their quarterly goal meet flawlessly and with less effort put forward. 


### Requirements

Spare Internal API calls: 

- 'https://api.sparelabs.com/v1/metrics/services'
- 'https://api.sparelabs.com/v1/services'
- 'https://api.sparelabs.com/v1/metrics/fleets'

StreamLit API

Python

### Files

- AllService.py holds all functions required to scrape and process API calls
- serviceSpecific.py hold similar functions to AllService but produce a per-service output
- requirements.txt maintains all the package dependencies required to run the web app

## Version 1

** Currently the APP has not been published **

The application works on a per-organization level, meaning the system will produce KPIs specific to a single organization. The security of this software depends on a user's access to the Spare platform, as the API key required to complete the report will be generated from the organization's settings page, under API keys. 

### Launching From Local Device

If you wish to run the application from you local machine here are the steps:

    1. Clone the QGR repository onto your computer using Git
    2. Once on local machine, navigate to the folder within your terminal screen (drag and drop the folder from finder onto the terminal window and press enter)
    3. Run 'pip install requirements.txt' to download the required dependancies
    4. Run 'streamlit run QGR.py' to begin the session, here the program will automatically generate a new chrome tab that holds the web application.
#### Required Inputs

*API Key* 
- The App requires the user to input an API key generated from the Admin page of the Spare platform. 

*Previous Quarter's Start Date*

- The start date of the quarter prior to the one the user is currently interested in. This is because many of the graphs generated show a comparison between the two quarters. The KPI table also shows a delta calculation of all the metrics generated which shows green or red depending on the change between quarters. Format: 2022-05-29 OR 2022/05/29
- By providing the date we are able to create a set of 13 weeks that account for the duration of each quarter, this data is fed into AllServices.py and serviceSpecific.py at the time of function call.

*Current Quarter's Start Date*

- The start date of the quarter the user is interested in reporting on. Again this will be used to generate the 13-week date-times that comprise the quarter. Format: 2022-05-29 OR 2022/05/29.

*Select Service (Multi-selectbox)*

- Once you have inputted the API_key the system will perform a check of the key, and will subsequently return a list of services under that organization if the correct sequence is entered. 

- The user is able to select the services in which they are interested in reviewing with customers, the output is a data frame consisting of KPI data for all 13 weeks of the current quarter.

