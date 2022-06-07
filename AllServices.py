import datetime
import time
import requests
import pandas as pd


def convert_toDate(unix):
    '''
    convert_toDate takes in a unix time stamp and converts this to a readable date-time stamp
    
    Returns: Date-time stamp
    
    Arguments: Unix time in the form of a float
    '''
    months = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08': 'Aug','09':'Sep','10':'Oct','11':'Nov', '12':'Dec'}
    int_representation = int(unix)
    date = str(datetime.datetime.fromtimestamp(int_representation))
    day = date[8:10]
    month = date[5:7]
    year = date[0:4]
    word_date = months[month]+' '+day+', '+year
    return word_date

def convert_time(date):
    '''
    convert_time takes in a date in the form of year-month-day or year/month/day (2022/02/23) and converts this to unix time stamp required for future API calls
    
    Returns: Unix time stamp equivalent of date specified
    
    Arguments: date in the form 2022/12/23 or 2022-12-23
    '''
    ## Convert date to unix date time
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:11])
    date_time = datetime.datetime(year, month, day, 0, 0)
    unix = time.mktime(date_time.timetuple())
    return unix





def get_dates_forward(date):
    '''
    get_dates is responsible for taking a quarter start date (2020/02/02) and produces all 13 specific weeks within the quarter and their start (&end) dates.
    
    Returns: an array of date-times that define the start and end of a week within the quarter in a particular year
    
    arguments: A string containing the quarter's start date
    '''
    
    unix = convert_time(date)
    store = []
    for e in range(0,14):
        # There are 13 weeks in our quarter
        newT = unix + (604800*e)
        # 7 Days equates to 604 800 seconds, which can be added to a unix time stamp to gain the next week's date
        store.append(newT)

    return store

def get_endWeekDate(unix):
    '''
    get_endWeekDate is responsible for calculating the last day of the week based on the first day of the week's date
    
    Returns: The date of the last day of the week within a quarter
    
    Arguments: The unix time of the first day of the week
    '''
    unix2 = (518400 + unix)
    return unix2

def check_apiKey(APIkey):
    '''
    check_apiKey will be used to check that the api key sequence provided by the user is correct and works to access Spare's API
    
    Returns: an integer value of a status code linked to the response provided by the API 
    '''
    URL = 'https://api.sparelabs.com/v1/services'
    headers1 = {'Authorization': APIkey}
    r = requests.get(url=URL, headers=headers1)
    statCode = r.status_code
    return statCode

def callfor_services(APIkey):
    '''
    
    callfor_services will be used to provide service specific KPI's for the quarterly report.
    
    Arguments: APIkey is the api-key specific to the organization with which to build the report from.
    
    Returns: a dataframe consiting of the Service Id's and the names of the service associated
    
    '''
    
    URL = 'https://api.sparelabs.com/v1/services'
    headers1 = {'Authorization': APIkey}
    r = requests.get(url=URL, headers=headers1)
    r = r.json()
    data = r['data']
    df = pd.json_normalize(data)
    result_df = df[df['status'] == 'enabled']
    result_df = result_df[['id', 'name']]
    result_df = result_df.set_index('name')
    return result_df

def get_requestKPI_total(fromT, toT, APIkey):
    '''
    get_requestKPI_total will call the request metric from the internal API call /metrics/services and return a cleaned dataframe with all KPI's related to the QGR reports
    
    Returns: Dataframe holding all KPI values for a particular week within a quarter
    
    Arguments: The start date and end date in unix format and the APIkey associated with the organization of interest
    '''
    headers1 = {'Authorization': APIkey}
    
    URL3 = 'https://api.sparelabs.com/v1/metrics/services'
    URL4 = 'https://api.sparelabs.com/v1/metrics/fleets'
    
    params2 = {'fromTs': f'{fromT}', 'toTs': f'{toT}', 'metricTypes[]': ['request']}
    params3 = {'fromTs': f'{fromT}', 'toTs': f'{toT}', 'metricTypes[]': ['onTimePerformance']}
    params4 = {'fromTs': f'{fromT}', 'toTs': f'{toT}', 'metricTypes[]': ['duty']}
    params5 = {'fromTs': f'{fromT}', 'toTs': f'{toT}', 'metricTypes[]': ['allTimeRequest']}
    params6 = {'fromTs': f'{fromT}', 'toTs': f'{toT}', 'metricTypes[]': ['review']}

    r2 = requests.get(url=URL3, headers=headers1, params=params2)
    r3 = requests.get(url=URL3, headers=headers1, params=params3)
    r4 = requests.get(url=URL4, headers=headers1, params=params4)
    r5 = requests.get(url=URL3, headers=headers1, params=params5)
    r6 = requests.get(url=URL3, headers=headers1, params=params6)
    
    r2 = r2.json()
    r3 = r3.json()
    r4 = r4.json()
    r5 = r5.json()
    r6 = r6.json()
    
    data = r2['metrics']
    data2= r3['metrics']
    data3 = r4['metrics']
    data4 = r5['metrics']
    data5 = r6['metrics']
    #Grab #of unique riders from requests
    number_uniqueRiders = len(r2['metrics'][0]['data']['uniqueRiderIds'])
    
    ###DF is the main request dataframe
   
    df = pd.json_normalize(data)
    df2 = pd.json_normalize(data2)
    df3 = pd.json_normalize(data3)
    df4 = pd.json_normalize(data4)
    
    
    
    df5 = pd.json_normalize(data5)
    df5.rename(columns = { 'data.meanReviewRating': 'averageReview'}, inplace=True)
    df5['averageReview'] = round(df5['averageReview']*100, 2)
    #We grab ontimeBookings from service/ontimeperformance
    onTimeBookings = int(df2['data.numOnTimeBookings'])
    
    df3['data.totalVehicleHoursS'] = (df3['data.totalVehicleHoursS']/3600)
    df3 = df3[['data.numPooledBoardings', 'data.totalVehicleHoursS']]
    
    
    df['usersFirstTrip'] = df4['data.numNewRiders']
    df['averageReview'] = df5['averageReview']
    
    
    
    df.rename(columns = {'data.numOfTerminalRequests': 'totalRequests', 'data.numOfCompletedRequests': 'completedRequests', 'data.numOfCompletedBoardings': 'completedBoardings', 'data.numOfCancelledRequests': 'requestCancellations', 'data.numOfNoShows': 'noShowCancellation', 'data.numOfCancelledBoardings': 'boardingCancellations', 'data.numOfNoShowBoardings': 'boardingCancellationNoShow', 'data.avgWaitTimeSeconds': 'meanWaitTime', 'data.medianWaitTimeSeconds': 'medianWaitTime', 'data.numBookingsAdminInterface': 'numberOfAdminBookings', 'data.numBookingsRiderInterface': 'numberOfRiderAppBookings','data.numBookingsDriverInterface': 'flagDownBookings'}, inplace = True)
    df['dates'] = convert_toDate(fromT)+'/'+convert_toDate(toT)
    df['TotalCancelled'] = round(((df['boardingCancellations']/(df['completedBoardings']+df['boardingCancellations']))*100), 2)
    df['noShowCancelled'] = round(((df['boardingCancellationNoShow']/(df['completedBoardings']+df['boardingCancellations']+df['boardingCancellationNoShow']))*100), 2)
    df['meanWaitTime'] = round((df['meanWaitTime']/60), 2)
    df['medianWaitTime'] = round((df['medianWaitTime']/60), 2)
    df['percentAdminBookings'] = round( (df['numberOfAdminBookings']/df['completedBoardings'])*100, 2 )
    df['percentRiderAppBookings'] = round( (df['numberOfRiderAppBookings']/df['completedBoardings'])*100, 2 )
    df['percentFlagDownBookings'] = round( (df['flagDownBookings']/df['completedBoardings'])*100, 2 )
    df['activeRiders'] = number_uniqueRiders
    df['OTP'] = round((onTimeBookings/df['completedRequests'])*100, 2)
    df['avgBoardingVehicleHr'] = round(df['completedBoardings']/df3['data.totalVehicleHoursS'], 2)
    df['pooledTripsRatio'] = round((df3['data.numPooledBoardings']/df['completedBoardings'])*100, 2)
    df = df[['dates','completedBoardings','TotalCancelled','noShowCancelled','activeRiders','completedRequests','avgBoardingVehicleHr', 'pooledTripsRatio','OTP','totalRequests','requestCancellations','noShowCancellation','boardingCancellations','boardingCancellationNoShow','meanWaitTime', 'medianWaitTime','percentAdminBookings','percentRiderAppBookings','percentFlagDownBookings', 'usersFirstTrip' ,'averageReview' ]]
    
    return df
    


def generateQuarter(date, APIkey):
    '''
    
    
    '''
    #dates will store all 13 weeks generated from the start date
    dates = get_dates_forward(date)
    
    #df will be the dataframe we add all weeks too
    # df = pd.DataFrame(columns = ['dates','completedBoardings','TotalCancelled','noShowCancelled','activeRiders','completedRequests','avgBoardingVehicleHr', 'pooledTripsRatio','OTP','totalRequests','requestCancellations','noShowCancellation','boardingCancellations','boardingCancellationNoShow','meanWaitTime', 'medianWaitTime','percentAdminBookings','percentRiderAppBookings','percentFlagDownBookings', 'usersFirstTrip', 'averageReview'])
    
    frames = []
    for weeks in range(13):
        fromT = dates[weeks]
        toT = get_endWeekDate(fromT)
        weekData = get_requestKPI_total(fromT, toT, APIkey)
        frames.append(weekData)
        
    results = pd.concat(frames)
    results = results.set_index('dates')
    return results



