import pymysql as my
import pandas as pd
import pickle

def retrieve_data():
    db = my.connect(host="localhost", user="root", passwd="atmresearch2017", db="flightdata")
    c = db.cursor()

    query = """ select * from eurotest1 order by ICAO, ts"""
    #
    # c.execute(query)

    df = pd.read_sql(query,db)
    # data = c.fetchall()

    # df = pd.DataFrame(list(c.fetchall()))
    # df.columns = ["icao", "lat", "lon", "hdg", "alt", "spd", "mdl", "regid", "ts", "org", "des", "roc", "fn"]
    db.close()
    #
    name = "0911-eurodata.pkl"
    df.to_pickle(name)

    return df

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
    # name = "0711-eurodata.pkl"
    retrieve_data()
    # save_data(data,name)

    return

main()