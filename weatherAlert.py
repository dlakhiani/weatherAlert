from flask import Flask, render_template, request
from datetime import datetime
import requests as req

app = Flask(__name__)
apikey = "21e0b1d1654e633828cb873e5ca4d9be"

def searchCities(lat, lon):
  cities = []
  # fetch info of surrounding cities using lat & lon of previous
  params = {
    "lat": lat,
    "lon": lon,
    "appid": apikey
  }
  api = req.get(url="http://api.openweathermap.org/data/2.5/find", params=params)

  # convert to json
  data = api.json()
  if int(data['cod']) == 200:
    print(data)

    # list of city dicts
    cities = [dict(name=(data["list"][i]["name"]),
                    temp=((data["list"][i]["main"]["temp"] - 273.15)*100)//100,
                    tempFeel=((data["list"][i]["main"]["feels_like"] - 273.15)*100)//100,
                    pressure=data["list"][i]["main"]["pressure"] // 10,
                    humidity=data["list"][i]["main"]["humidity"],
                    wind=((data["list"][i]["wind"]["speed"]*3.6)*100)//100,
                    desc=(data["list"][i]["weather"][0]["description"])) for i in range(1, len(data["list"]))]

  else:
    return None
  return cities

def fetchApi(params):
  cities = []
  # fetch info of city given
  api = req.get(url="http://api.openweathermap.org/data/2.5/weather", params=params)
  # convert to json
  data = api.json()

  if int(data['cod']) == 200:
    print(data)

    # simplicity dict
    initial = dict(desc=data["weather"][0]["description"],
                    temp=((data["main"]["temp"] - 273.15)*100)//100,
                    tempFeel=((data["main"]["feels_like"] - 273.15)*100)//100,
                    pressure=data["main"]["pressure"] // 10,
                    humidity=data["main"]["humidity"],
                    vis=data["visibility"]//1000,
                    wind=((data["wind"]["speed"]*3.6)*100)//100,
                    sunrise=datetime.utcfromtimestamp(data["sys"]["sunrise"]).strftime('%Y-%m-%d %H:%M:%S'),
                    sunset=datetime.utcfromtimestamp(data["sys"]["sunset"]).strftime('%Y-%m-%d %H:%M:%S'))

    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]
    cities = searchCities(lat, lon) # search cities around
    print(cities)
    
    cities.insert(0, initial) # insert inital city to return
  else:
    return None
  return cities

def convertUnix(initial):
  # edit date to be readable
  sunrise = initial["sunrise"][11:]
  sunset = initial["sunset"][11:]
  return sunrise, sunset

# route to home page
@app.route('/', methods=['GET', 'POST'])
def index():
  weather = []
  title = desc = temp = pressure = wind = time = ""
  if request.method == 'POST':  # recieve user input
    print('data recieved')
    form = request.form  # store user input from form

    # get values from dict keys
    country = form.get('country')
    code = form.get('code')

    # call api for country
    params = dict(q=f"{country}, {code}", appid= apikey)
    weather = fetchApi(params)
    print(weather)

    if weather != None:
      initial = weather.pop(0) # remove initial city
      print(initial)
      time = convertUnix(initial)

      # prep html text
      title = f"{country}, {code}:"
      desc = f"Description: {initial['desc']} with a visibility of {initial['vis']} km"
      temp = f"Temperature: {initial['temp']} Celsius, but feels like {initial['tempFeel']} Celsius"
      pressure = f"Pressure of {initial['pressure']} kPa, with a humidity of {initial['humidity']}%"
      wind = f"Wind speeds of {initial['wind']} km/h"
      time = f"Sunrise: {time[0]} UTC to Sunset: {time[1]} UTC"

    else:
      title = "City not found."

  # display using jinja2 variables 
  return render_template('index.html', country = title, desc = desc, temp = temp, pressure = pressure, wind = wind, time = time,
                          cities=weather)

if __name__ == '__main__':
  app.run(debug=True, threaded=True)
# debug: allows flask to update & catch errors
# threaded: run services concurrently, so its fast
