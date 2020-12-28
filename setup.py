

## Setup to run when the pi boots up ##
import time, datetime, pickle
import sqlite3 as lite

## Establish start time for naming new db table ##
now = datetime.datetime.now()
sessionDate = now.strftime("%Y_%m_%d")
sessionName = "session_started_on_" + sessionDate
with open('/home/pi/FermentorApp/sessionName.pkl', 'wb') as f:
    pickle.dump(sessionName, f)

## some properties ##
dbName = 'sensorsData.db'
startingTemp = 75 #change using flask interface
with open('/home/pi/FermentorApp/tempSet.pkl','wb') as f:
    pickle.dump(startingTemp, f)

## Create a new db table for the current session ##
## Overwrites existing table if another started on this day ##
con = lite.connect(dbName)
with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS " + sessionName)
    cur.execute("CREATE TABLE " + sessionName +
    " (timestamp DATETIME, tempIn NUMERIC, tempOut NUMERIC, tempBeer NUMERIC, tempSet NUMERIC)")
con.close()
