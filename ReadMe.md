# Requirements

```
sudo apt install python3-venv
python3 -m venv flaskappenv
source flaskappenv/bin/activate
pip install --upgrade pip
sudo [apt-get|yum] install python3-devel
sudo [apt-get|yum] install gcc
sudo pip install -r requirements.txt
// port açma
firewall-cmd --zone=public --add-port=1625/tcp --permanent
firewall-cmd --reload
gunicorn wsgi:app
gunicorn --bind 185.126.177.153:1625 wsgi:app
python3 wsgi.py
```


###Centos 7 Deploy
```
cd /var/www/python3-blockchain-microservice/
sudo chown -R coinswifter:coinswifter ./
source flaskappenv/bin/activate
pip install -r requirements.txt
pm2 start wsgi.py
```

###Centos 7 Stop
```
lsof -i :1625
kill -9 [ID]
```

###Windows
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\flaskappenv\Scripts\activate
waitress-serve --listen=127.0.0.1:8000 myflaskappdev:app
```


###### Software by DATAkul