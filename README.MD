<h1> Steam Stats App </h1>

**App Goal:** To take the file sessions.csv from customer Steam usage and generate insights
  
**Target Audience:** H2O SE/AE/CSM/TAM, Customers

**Industry:** Horizontal

**Actively Being Maintained:** Yes

**Last Updated:** Nov 22, 2021

**Comes with Demo Mode (pre-loaded data, models, results, etc.):** No

**Allows for Uploading and Using New Data:** Yes

**Features:**
* Upload feature for uploading a sessions.csv file
* Group by on key fields to get row counts
* Generate KPI Dashboard, Visuals
* Download Usage Summary/Daily Peak Usage data
* Choose timeline to filter rows for above to tell usage story

**GitHub:** http://www.github.com/h2oai/steam-stat


<hr>
<b>Author:</b> <i>karthik.guruswamy@h2o.ai</i> <p>
<h3> Where to find the Steam Driverless AI Logs ? </h3>
You need to be an Admin on Steam to access the logs. See below on where to get it from:

<img width="679" alt="Screen Shot 2021-11-16 at 4 38 56 PM" src="https://user-images.githubusercontent.com/13601376/141975249-b28ebe93-faeb-4f5b-9ddd-49be03b9c6ef.png">

Its a CSV file that has the name driverless-report-xyz.csv

It should have the entire historical usage of Driverless AI start/stops.

<h3> What Stats are possible in this App with Steam Logs ?</h3>
<h4> Main Dashboard </h4>
 <p>
 The main dashboard (after you upload the logs), shows you the logs themselves, which you can scroll/sort/group by on any column etc.,<p>
   
 The "Peak usage by the day" table basically breaks down day level information on the entire range of the data. Basically you get "Peak Sessions", "Peak CPUs", "Peak GPUs", "Unique Users" etc., 
 <p>
  <b>Sessions</b>: A session is basically a record in the log that represents the duration of a 'start'/'stop' event of a Driverless AI or H2O-3 instance. Depending on the workload, the session can last anywhere from a few minutes to a few days! So basically our reports chops those sessions into day activities and you get rollups per day!
<p>
The Summary table shows you the following info for the entire log duration:
<ul>
  <li> Log Start
  <li> Log End
  <li> Total Hours of use
  <li> Total Sessions
  <li> # of Unique users
  <li> Max Daily Users
  <li> Max Daily CPUs
  <li> Max Daily GPUs
  <li> # of Days that there were no sessions ! (inactive day basically)
</ul><p>
Both the Peak Usage and Summary information can be downloaded into a CSV, so you can format/chart it in Excel or an Editor of your choice.
   
<h4> Drill Down Charts </h4>
<p>
You can also get insights using drill down charts to see:<br>
Unique users and Peak Sessions (basically day level count) for each day in the log duration - including days that there was no activity. You can also see the how many sessions were present across different versions of Driverless AI and H2O-3 installed on Steam<p>
The top 10 power users in terms of in terms of # of Sessions and # of hours used is also available as chart<p>
  
<h3> How to run it on your Desktop or an ubuntu server ?</h3>

1. Create a virtualenv python 3.7 (which worked for me) and activate an environment<p>
2. Run
<br> pip install -r requirements.txt<p>
3. Get latest wave targz from https://wave.h2o.ai/docs/installation and unpack<p>
4. Run waved (wave server)<p>
5. Run 
<br> wave run --no-reload steam_stats.py<p>
6. Go to http:<localhost|server ip>:10101
<img width="1240" alt="Screen Shot 2021-09-25 at 7 51 42 PM" src="https://user-images.githubusercontent.com/13601376/134791652-454185ae-4f30-4777-b54d-5f9fc22a8642.png"><p>
7. Get your steam logs from Steam (need admin account) and Click Browse and Upload to upload the log to the App<p>
8. View main Dashboard<p>
<img width="1424" alt="Screen Shot 2021-11-22 at 6 53 30 AM" src="https://user-images.githubusercontent.com/13601376/142883003-38311eda-d0cd-4345-8c9b-75a2ee36a80e.png">
  You can use the Grouping Feature on top to group by individual fields, gives you a drilldown per group and counts per group<p>
  You can also use the Filter Timeline feature to filter rows based on various time periods, to compare usage, power users etc., 
<p>
9. Click "Drilldown" on the left to get nice graphs!<p>
<img width="1409" alt="Screen Shot 2021-09-25 at 7 53 09 PM" src="https://user-images.githubusercontent.com/13601376/134791675-d086c037-302a-418f-aead-480463f9056e.png"><p>
10. Hit "Back" to go back to main Dashboard<p>

<h3> Feature request or bugs </h3><p>
   <b>Bugs</b>: Just file an issue  from "issues" tab with a screenshot<p>
   <b>Feature Request</b>: Need info. on what kind of chart or table or a rollup would be interesting in your deployment. If the logs support underlying data, it should be easy for me to add that to the code. In most cases, you should be able to change the code yourself :) and let me know what you did and Im happy to merge that to the main code if it makes sense.
   
