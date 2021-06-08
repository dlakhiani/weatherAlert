from flask import Flask, render_template, request
from datetime import datetime
import requests as req

app = Flask(__name__)
apikey = "21e0b1d1654e633828cb873e5ca4d9be"

# route to home page
@app.route('/', methods=['GET', 'POST'])
def index():
  title = desc = temp = pressure = wind = time = ""
  if request.method == 'POST':
    print('data recieved')
    form = request.form
    country = form.get('country')
    code = form.get('code')

    params = dict(q=f"{country}, {code}", appid= apikey)
    api = req.get(url="http://api.openweathermap.org/data/2.5/weather", params=params)

    data = api.json()
    if data:
      print(data)
      
      weather = dict(desc = data["weather"][0]["description"],
                     temp = ((data["main"]["temp"] - 273.15)*100)//100, 
                     tempFeel = ((data["main"]["feels_like"] - 273.15)*100)//100, 
                     pressure = data["main"]["pressure"] // 10,
                     humidity = data["main"]["humidity"],
                     vis = data["visibility"]//1000,
                     wind = ((data["wind"]["speed"]*3.6)*100)//100,
                     sunrise = datetime.utcfromtimestamp(data["sys"]["sunrise"]).strftime('%Y-%m-%d %H:%M:%S'),
                     sunset = datetime.utcfromtimestamp(data["sys"]["sunset"]).strftime('%Y-%m-%d %H:%M:%S'))
      print(weather)
      sunrise = weather["sunrise"][11:]
      sunset = weather["sunset"][11:]

      title = f"{country}, {code}:"
      desc = f"Description: {weather['desc']} with a visibility of {weather['vis']} km"
      temp = f"Temperature: {weather['temp']} Celsius, but feels like {weather['tempFeel']} Celsius"
      pressure = f"Pressure of {weather['pressure']} kPa, with a humidity of {weather['humidity']}%"
      wind = f"Wind speeds of {weather['wind']} km/h"
      time = f"Sunrise: {sunrise} to Sunset: {sunset}"

  # display using jinja2 variables 
  return render_template('index.html', country = title, desc = desc, temp = temp, pressure = pressure, wind = wind, time = time)

if __name__ == '__main__':
  app.run(debug=True, threaded=True)
# debug: allows flask to update & catch errors
# threaded: run services concurrently, so its fast
