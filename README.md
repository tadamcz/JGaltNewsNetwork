# Notes on extremely quick and dirty Ubuntu setup


Installing dependencies with patched qt:
```shell
sudo apt install -y xvfb
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb
sudo apt install -y ./wkhtmltox_0.12.6-1.bionic_amd64.deb
```

Launcher shell script (something like this):
```shell
exec &>> logs.txt
PATH=$PATH":/usr/local/bin"
echo "Running cron-job jgalt at $(date)"

/home/thomas/.cache/pypoetry/virtualenvs/jgaltnewsnetwork-H6aRXdm--py3.8/bin/python /home/thomas/JGaltNewsNetwork/main.py
```

Crontab:
```
*/40 * * * * bash -lc "cd /home/thomas/JGaltNewsNetwork && /home/thomas/JGaltNewsNetwork/run.sh"
```

