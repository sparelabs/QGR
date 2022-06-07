from tokenize import group
import streamlit as st
import matplotlib.pyplot as plt
import AllServices as mt
import hydralit_components as hc
import serviceSpecific as meS
import base64
import pandas as pd
import numpy as np

@st.cache
def getQuarter(date, apiKey):
    data = mt.generateQuarter(date, apiKey)
    return data

@st.cache
def getQuarter_service(date, apiKey):
    data = meS.generateServiceData(date, apiKey)
    return data

@st.cache
def getservices(date, APIkey, serviceId):
    data = meS.generateQuarter_service(date, APIkey, serviceId)
    return data

def getDelta(value1, value2):
    #Value1 is current Quarter, value2 is last quesa
    val = value1-value2
    return round(val, 2)
    
def filedownload(df, date):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="{date}.csv">Download CSV File</a>'
    return href

@st.cache
def genGraph(type, columnX, xName, columnY1, yName, columnY2):
    '''
    Arguments:
        type: this will define if the graph will be of bar, or line type
        columnX: this will be most often the dates found within the quarter
        columnY1: this is the data type specified by the user, from old quarter data
        columnY2: this is the data type specified by the user, from the current quarters data
        xname: is the title of the data held in the x-axis
        yname: is the title of the data held in the two y-axis sets
    '''
    
    
    if type == 'Bar':
        plt.figure(figsize=(30,10))
        x_axis = np.arange(len(columnX))
        plt.bar(x_axis-0.2, columnY1, width=0.4, label="Last Quarter", color=(0.29,0,0.51))
        plt.bar(x_axis+0.2, columnY2, width=0.4, label="Current Quarter", color=(0.30,0.72,0.65) )
        plt.xticks(x_axis, columnX)
        plt.xlabel(f"{xName}")
        plt.ylabel(f"{yName}")
        plt.grid(axis = 'y', color='grey', linestyle='-')
        plt.legend()
        plt.tick_params(axis='x', labelsize=8)
        
        return plt
    
    elif type == 'Line':
        plt.figure(figsize=(30,10))
        plt.tick_params(axis='x', labelsize=8)
        plt.plot(columnX, columnY1, marker = "*", label="Last Quarter", color=(0.29,0,0.51))
        plt.plot(columnX, columnY2, marker = "o", label="Current Quarter", color=(0.30,0.72,0.65))
        plt.xlabel(f"{xName}")
        plt.ylabel(f"{yName}")
        plt.legend()
        
        return plt

st.set_page_config(layout="wide")

metric_labels = {'dates':'Dates', 'completedBoardings':'Number of Completed Boardings', 'TotalCancelled':'Total Cancellation Percentage (%)', 'noShowCancelled':'No-Show Cancellation Percentage (%)', 'activeRiders':'Number of Active Riders', 'completedRequests':'Number of Completed Requests', 'avgBoardingVehicleHr':'Average Boarding / Vehicle Hour', 'pooledTripsRatio':'Pooled Trips Ratio (%)', 'OTP':'On Time Performance (%)', 'totalRequests':'Number of Completed Requests', 'requestCancellations':'Number Of Request Cancellations', 'noShowCancellation':'Number of No-Show Cancellations', 'boardingCancellations':'Number of Boarding Cancellations', 'boardingCancellationNoShow':'Number of No-Show Boarding Cancellations', 'meanWaitTime':'Mean Wait Time (Mins)', 'medianWaitTime':'Average Wait Time (Mins)', 'percentAdminBookings':'Admin Panel Bookings (%)', 'percentRiderAppBookings':'Rider App Bookings (%)', 'percentFlagDownBookings':'Flag Down Bookings (%)', 'usersFirstTrip':'Number of First Trip Riders', 'averageReview':'Average Rider Review (%)'}


clicked = None
date1 = None
date2 = None
API_key = None
serviceName = None
options = None

with st.container():
    col1, col2 = st.columns([2,3])
    
    with col1: 
        st.title("Quarterly Goal Reporting")

    with col2:
    # We begin by asking the User the api key in the GUI corresponding to the organization they are interested in
        API_key = 'Bearer '+st.text_input("Enter the API key provided in the organization's admin page!")
        date1 = st.text_input("Enter Last Quarter Start Date")
        date2 = st.text_input("Enter Current Quarter Start Date")

        if mt.check_apiKey(API_key) == 200:
            serviceNames = mt.callfor_services(API_key)
            serviceName = serviceNames.to_dict()
            
            options = st.multiselect(
                'Select Services to include',
                serviceName['id'])
            clicked = st.button("Create Report")
           
            
data1 = pd.DataFrame()
data2 = pd.DataFrame()

if clicked:
    
    with hc.HyLoader('Wait for it...... This can take up to 60 seconds', hc.Loaders.standard_loaders, index=5):
        data1 = getQuarter(date1, API_key)
        data2 = getQuarter(date2, API_key)
        st.balloons()
    

    with st.container():
        st.title("Quarter Total KPIs")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric('Total Boardings', f"{data2['completedBoardings'].sum()}", f"{getDelta(data2['completedBoardings'].sum(), data1['completedBoardings'].sum())}")
            st.metric(f"Highest Week: {data2['completedBoardings'].idxmax()}", f"{data2['completedBoardings'].max()}")
            st.metric("On Time Performance", f"{round(data2['OTP'].mean(), 2)}%", f"{getDelta(data2['OTP'].mean(), data1['OTP'].mean())}%")
            
        with col2:
            st.metric('Admin Panel Bookings', f"{round(data2['percentAdminBookings'].mean(),2)}%", f"{getDelta(data2['percentAdminBookings'].mean(), data1['percentAdminBookings'].mean())}%")
            st.metric('Rider App Booking', f"{round(data2['percentRiderAppBookings'].mean(), 2)}%", f"{getDelta(data2['percentRiderAppBookings'].mean(), data1['percentRiderAppBookings'].mean())}%")
            st.metric('Average Rider Review', f"{round(data2['averageReview'].mean(), 2)}%", f"{getDelta(data2['averageReview'].mean(), data1['averageReview'].mean())}%")
        
        with col3:
            st.metric('Avg Boarding/ Vehicle Hour', f"{round(data2['avgBoardingVehicleHr'].mean(),2)}", f"{getDelta(data2['avgBoardingVehicleHr'].mean(), data1['avgBoardingVehicleHr'].mean())}")
            st.metric('Median Wait Time', f"{round(data2['medianWaitTime'].median(), 2)}", f"{getDelta(data2['medianWaitTime'].median(), data1['medianWaitTime'].median())}")
            st.metric('Average Wait Time', f"{round(data2['meanWaitTime'].mean(), 2)}", f"{getDelta(data2['meanWaitTime'].mean(), data1['meanWaitTime'].mean())}")
        
        with col4:
            st.metric("Cancelled Trip Percentage", f"{round(data2['TotalCancelled'].mean(), 2)}%", f"{getDelta(data2['TotalCancelled'].mean(), data1['TotalCancelled'].mean())}%" )
            st.metric("No-Show Percentage", f"{round(data2['noShowCancelled'].mean(), 2)}%", f"{getDelta(data2['noShowCancelled'].mean(), data1['noShowCancelled'].mean())}%" )
            st.metric("Average Pooled Trips", f"{round(data2['pooledTripsRatio'].mean(), 2)}%", f"{getDelta(data2['pooledTripsRatio'].mean(), data1['pooledTripsRatio'].mean())}%" )
            
    with st.expander("Click to See each Quarter's Data!"):
        st.header(f"Last Quarter's Data: {date1} ")
        st.dataframe(data1)
        st.markdown(filedownload(data1, date1), unsafe_allow_html=True)
        st.header(f"Current Quarter's Data: {date2}")
        st.dataframe(data2)
        st.markdown(filedownload(data2, date2), unsafe_allow_html=True)
   

with st.expander("Click to see Bar graphs of each of the KPIs"):
    attributes = list(data2.columns)
    for metric in attributes:
        st.header(f"{metric_labels[metric]}")
        st.pyplot(genGraph('Bar', list(data2.index), 'Dates', list(data1[f"{metric}"]), f"{metric_labels[metric]}", list(data2[f"{metric}"])), clear_figure=False)
    

with st.expander("Click to see Line graphs of each of the KPIs"):
    attributes = list(data2.columns)
    for metric in attributes:
        st.header(f"{metric}")
        st.pyplot(genGraph('Line', list(data2.index), 'Dates', list(data1[f"{metric}"]), f"{metric_labels[metric]}", list(data2[f"{metric}"])), clear_figure=False)

if not data2.empty:
    leng = len(options)
    for id2 in range(0,leng):
        serviceId = serviceName['id'][options[id2]]
        service_Name = options[id2]
        with st.expander(f"Click to see Data for {service_Name}"):
            data = pd.DataFrame()
            with hc.HyLoader('Wait for it...... This can take up to 60 seconds', hc.Loaders.standard_loaders, index=5):
                data = getservices(date2, API_key, serviceId)
            if not data.empty:
                st.header(f"Quarter Data for {service_Name}")
                st.dataframe(data)
                st.markdown(filedownload(data, date2), unsafe_allow_html=True)
            