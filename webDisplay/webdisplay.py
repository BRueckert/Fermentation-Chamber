#!/usr/bin/python3

from matplotlib.backends.backend_agg import FigureCanvasAgg as FC
from matplotlib.figure import Figure
from flask import Flask, render_template, request, make_response
import io
import sqlite3 as lite
import datetime, pickle
app = Flask(__name__)

## Get session name and current set temp
dbName = 'sensorsData.db'
sessionName = pickle.load(open('/home/pi/FermentorApp/sessionName.pkl', 'rb'))
tempSet = pickle.load(open("/home/pi/FermentorApp/tempSet.pkl", "rb"))

def getData():
    con = lite.connect('/home/pi/FermentorApp/' + dbName)
    cur = con.cursor()
    try:
        for row in cur.execute("SELECT * FROM " + sessionName + " ORDER BY timestamp DESC LIMIT 1"):
            #print(row)
            date = row[0]
            tempIn = row[1]
            tempOut = row[2]
            tempBeer = row[3]
            tempSet = row[4]
    except:
        print('error of some kind')
    con.close()
    return date, tempIn, tempOut, tempBeer, tempSet

@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        date, tempIn, tempOut, tempBeer, tempSet = getData()
        templateData = {
            'title' : 'Fermentation Chamber Data',
            'tempOut' : tempOut,
            'tempIn' : tempIn,
            'tempBeer' : tempBeer,
            'tempSet' : tempSet,
            'date' : date
        }
        return render_template('index.html', **templateData)
    if request.method == 'POST':
        tempSet = request.form["tempSet"]
        with open('/home/pi/FermentorApp/tempSet.pkl','wb') as f:
            pickle.dump(tempSet, f)
        templateData = {
            'title' : 'Temperature Set Successful',
            'tempSet' : tempSet,
        }
        return render_template('newSetTemp.html', **templateData)

@app.route('/graph')
def plot_temps():
    con = lite.connect('/home/pi/FermentorApp/' + dbName)
    cur = con.cursor()
    cur.execute("SELECT * FROM " + sessionName + " ORDER by timestamp DESC")
    data = cur.fetchall()
    date = []
    tempIn = []
    tempOut = []
    tempBeer = []
    for row in reversed(data):
        date.append(row[0])
        tempIn.append(row[1])
        tempOut.append(row[2])
        tempBeer.append(row[3])
    samples = list(range(len(date)))
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    axis.set_title("Temperature trends for this session")
    axis.set_xlabel("Sample Number")
    axis.set_ylabel("Temp (deg F)")
    axis.set_ylim([45,80])
    axis.plot(samples, tempIn, label='Fermentor Temp')
    axis.plot(samples, tempOut, label='Ambient Temp')
    axis.plot(samples, tempBeer, label='Beer Temp')
    axis.legend()
    canvas = FC(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=6969, host='0.0.0.0')
