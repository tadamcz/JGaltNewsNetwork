# Ubuntu setup

Installing dependencies with patched qt:
```shell
sudo apt install -y xvfb
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb
sudo apt install -y ./wkhtmltox_0.12.6-1.bionic_amd64.deb
```

launcher shell script:
```shell
exec &>> logs.txt
echo "Running cron-job jgalt at $(date)"

/home/thomas/.cache/pypoetry/virtualenvs/jgaltnewsnetwork-H6aRXdm--py3.8/bin/python main.py
```

