
import pandas as pd
import pickle
from os.path import dirname, abspath

def writescenario(data,scenarioname):
    aircraft = data
    scenarioname =scenarioname
    lines=[]    #create list
    area = [54,2.5,50,7.5,40000,10000]  #define the area to be captured [lat1,lon1,lat2,lon2,top,bottom]

    #Create area
    lines.append("00:00:00.00> AREA" +","+ str(area[0]) + ","+ str(area[1]) + ","+ str(area[2]) + "," + str(area[3])
                 + "," + str(area[4])+"\n")


    #Create aircraft
    for i in range(0,len(aircraft),1):
        dataframe = aircraft[i]
        acid = dataframe.iloc[0]['icao']
        actype = dataframe.iloc[0]['mdl']
        lat = dataframe.iloc[0]['lat']
        lon = dataframe.iloc[0]['lon']
        hdg = dataframe.iloc[0]['hdg']
        alt = dataframe.iloc[0]['alt']
        spd = dataframe.iloc[0]['spd']



        lines.append("00:00:00.00> CRE " + str(acid) + "," + str(actype) + "," + str(lat) + "," + str(lon) + ","
                     + str(hdg) + ","+ str(alt) + "," + str(spd) + "\n")

    # Create waypoints
    for i in range(0,len(aircraft),1):
        dataframe = aircraft[i] # consider each aircraft in the set
        for x in range(0,len(dataframe),1):
            acid = dataframe.iloc[x]['icao']    # aircraft reg id
            lat = dataframe.iloc[x]['lat']  # latitude
            lon = dataframe.iloc[x]['lon']  # longitude
            alt = dataframe.iloc[x]['alt']  # altitude


            #print each waypoint
            lines.append("00:00:00.00> ADDWPT " + str(acid) + "," + str(lat) + "," + str(lon) + ","
                         + str(alt) + "\n")

    directory = (dirname(dirname(dirname(abspath(__file__)))))


    file = open(directory+"/scenario/"+scenarioname,'w')
    file.writelines(lines)
    file.close()


    return

def sort_data(data):
    df= data

    #Sort dataframe per aircraft
    aircraft = []
    for group in df.groupby("icao"):
        aircraft.append(group[1])

    return aircraft



def main():
    scenarioname = 'scenario4.scn'
    filename = "test1.pkl"
    with open("/Users/gideon_92/PycharmProjects/bluesky/data/adsb/"+filename, 'rb') as pickle_file:
        df = pickle.load(pickle_file)

    data = sort_data(data=df)
    writescenario(data,scenarioname)

    return

main()

