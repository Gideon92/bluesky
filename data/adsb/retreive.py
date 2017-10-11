import pymysql as my
import pandas as pd
import pickle

def retrieve_data():
    db = my.connect(host="localhost", user="root", passwd="atmresearch2017", db="flightdata")
    c = db.cursor()

    query = """ select * from FRANED where org='AMS' and des='CDG' """

    c.execute(query)
    data = c.fetchall()
    db.close()

    return data

def save_data(data,name):
    data = data
    name = name

    # Make Dataframe
    df = pd.DataFrame(list(data))
    df.columns = ["icao", "lat", "lon", "hdg", "alt", "spd", "mdl", "regid", "ts", "org", "des", "roc", "fn"]

    # Save Dataframe as pickle
    df.to_pickle(name)

    return

def main():
    name = "test1.pkl"
    data= retrieve_data()
    save_data(data,name)

    return

main()