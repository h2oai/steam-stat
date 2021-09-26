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
2. Run
<br> pip install -r requirements.txt
3. Get latest wave targz from https://wave.h2o.ai/docs/installation and unpack
4. Run waved (wave server)
5. Run 
<br> wave run --no-reload steam_stats.py
6. Go to http:<localhost|server ip>:10101
<img width="1240" alt="Screen Shot 2021-09-25 at 7 51 42 PM" src="https://user-images.githubusercontent.com/13601376/134791652-454185ae-4f30-4777-b54d-5f9fc22a8642.png">
7. Get your steam logs from Steam (need admin account) and Click Browse and Upload to upload the log to the App<br>
8. View main Dashboard<br>
<img width="1336" alt="Screen Shot 2021-09-25 at 7 53 00 PM" src="https://user-images.githubusercontent.com/13601376/134791665-165778d0-0d4c-4b81-b54d-49317b88801a.png">
9. Click "Drilldown" on the left to get nice graphs!<br>
<img width="1409" alt="Screen Shot 2021-09-25 at 7 53 09 PM" src="https://user-images.githubusercontent.com/13601376/134791675-d086c037-302a-418f-aead-480463f9056e.png">
10. Hit "Back" to go back to main Dashboard
