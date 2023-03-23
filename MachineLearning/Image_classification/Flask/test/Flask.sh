conda install flask
export FLASK_APP=app.py
export FLASK_ENV=development



# python
import requests

resp = requests.post("http://localhost:5000/predict",
                     files={"file": open('/home/ant/koshort.jpg','rb')})
                     


resp = requests.post("http://localhost:5000/predict",
                     files={"file": open('/home/ant/dotch.jpg','rb')})
print(resp.json())


resp = requests.post("http://localhost:5000/predict",
                     files={"file": open('/home/ant/al.jpg','rb')})
print(resp.json())

