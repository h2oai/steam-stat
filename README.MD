<h1> Steam Stats App </h1>

**App Goal:** To take the file sessions.csv from customer Steam usage and generate insights

**Target Audience:** H2O SE/AE/CSM/TAM, Customers

**Industry:** Horizontal

**Actively Being Maintained:** Yes

**Last Updated:** Mar 26th, 2021

**Comes with Demo Mode (pre-loaded data, models, results, etc.):** No

**Allows for Uploading and Using New Data:** Yes

**Features:**
* Upload feature for uploading a sessions.csv file
* Generate KPI Dashboard, Visuals


<hr>

<h3> How to run it on your Desktop or an ubuntu server ?</h3>

1. Create a virtualenv python 3.7 (which worked for me) and activate an environment
2. Get latest wave targz from wave.h2o.ai
3. Run waved (wave server)
4. Run 
<br> wave run --no-reload steam_stats.py
5. Go to http:<localhost|server ip>:10101
