[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://t.me/SuperCodeBot) [![releases](https://img.shields.io/github/release/Gotham13121997/superCodingBot.svg)](https://github.com/Gotham13121997/superCodingBot/releases/tag/v2) [![license](https://img.shields.io/cocoapods/l/AFNetworking.svg)](https://github.com/Gotham13121997/superCodingBot/blob/master/LICENSE) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/ac9e193532614cb8a7e90adb0fcbe46d)](https://www.codacy.com/app/Gotham13121997/superCodingBot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Gotham13121997/superCodingBot&amp;utm_campaign=Badge_Grade)
# superCodingBot  

[![Join the chat at https://gitter.im/superCodingBot/Lobby](https://badges.gitter.im/superCodingBot/Lobby.svg)](https://gitter.im/superCodingBot/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

THE TELEGRAM BOT FOR COMPETITIVE PROGRAMMERS  
 
## ABOUT
superCodingBot is a telegram bot built in python 3 using python-telegram-bot wrapper.

## [BOT LINK](https://t.me/superCodeBot)

## FEATURES
* Getting ratings from hackerrank,hackerearth,codeforces,spoj and codechef in the form of ranklist  
* Automatic updation of ratings
* Getting upcoming competitions and setting reminder for them
* Getting ongoing competitions
* Compiling and running code from the bot itself
* Getting questions from codechef and codeforces according to choice
* Getting topics from geeksforgeeks.com
* Subscribing to get Question of the day 

## LIBRARIES USED
* PYTHON-TELEGRAM-BOT  
* HTML5LIB  
* BEAUTIFUL SOUP  
* HACKERRANK API  
* APSCHEDULER  
* XLSX WRITER  
* SQLAlchemy
  
## USAGE
### PREREQUISITES
* python 3 or above

### CONFIGURATION
* Create your bot and Get your telegram bot token from [BotFather](https://core.telegram.org/bots#botfather)
* Get your hackerrank api key from [Hackerrank](https://www.hackerrank.com/api)
* Register to [Clist](https://www.clist.by) and get your username and api key
* Get your telegram chat id
   * You can get your chat id by first messaging to the bot and then checking the url https://api.telegram.org/botYourBOTToken/getUpdates  
It will look somewhat like this  
{"update_id":8393,"message":{"message_id":3,"from":{"id":7474,"first_name":"AAA"},"chat":{"id":,"title":""},"date":25497,"new_chat_participant":{"id":71,"first_name":"NAME","username":"YOUR_BOT_NAME"}}}  
the id of the chat object is your chat id  

* Edit the config.ini file with your telegram bot token, hackerrank api key, clist user name, clist api key. Also put your chat id in admin chat id. You can put multiple admin chat ids seperated by comma. Admins will be notified by the bot whenever data or questions are updated and will have access to admin commands. You can also put your persistent storage point if you will be using OPENSHIFT ONLINE to host the bot (If name of your volume is df then put /df/ in the field) otherwise just leave the field blank 

### RUNNING ON LOCAL PC
* pip install requirements.txt in console
* run app.py script
* enjoy

### HOSTING ON OPENSHIFT ONLINE
* edit the config.ini file
* save all the files in a repository on github  
* create an account on [REDHAT OPENSHIFT ONLINE](https://www.openshift.com)
* select the location of your server 
* wait for a few days till you recieve confirmation
* after recieving confirmation, login and create new application
* select python 3.4 or above
* select name and everything
* enter the url of the github repository
* wait for application to start
* enjoy
* You will have to use persistent storage to prevent data loss on deployments
  * think of a name for mount point eg /df
  * open the openshift console
  * go to storage and create a persistent storage
  * Go to deployments
  * then in deployment configuration attach the persistent storage along with a mount point you thought of
  * wait for the app to re-deploy
  * enjoy

#### REBUILDING PROJECT ON OPENSHIFT ONLINE  
when you want to rebuild your project  

* first of all go to deployments and select the latest deployment
* downscale the no of pods to 0 and wait for it to happen
*  **IMPORTANT** go to deployment configuration and detach the storage. A deployment will start, let it finish
* Go to builds, select name and click on start build
* After finishing build a deployment will start, let it finish
* Go back to deployment configuration and add storage with same mount point as previous and wait for a new deployment
* After deployment finishes, go to deployments. Select latest and scale the pod to 1.  

* **YOU CAN REMOVE YOUR GITHUB REPOSITORY BUT MAKE SURE TO RECREATE IT WHEN REBUILDING YOUR PROJECT**

## COMMANDS
### PUBLIC COMMANDS
* /help - get a list of all the commands
* /compiler - compile and run code  
![alt text](https://github.com/Gotham13121997/superCodingBot/blob/master/gifs/compiler.gif)  
* /register - to register your handle with the bot  
![alt text](https://github.com/Gotham13121997/superCodingBot/blob/master/gifs/register.gif)  
* /unregister - to unregister your handle from the bot
* /update - manually initiate update of your data
* /geeksforgeeks - browse topics from geeksforgeeks.com  
![alt text](https://github.com/Gotham13121997/superCodingBot/blob/master/gifs/geeksforgeeks.gif)  
* /randomcc - get random question from codechef according to choice  
![alt text](https://github.com/Gotham13121997/superCodingBot/blob/master/gifs/randomcc.gif)  
* /randomcf - get random question from codeforces according to choice  
![alt text](https://github.com/Gotham13121997/superCodingBot/blob/master/gifs/randomcf.gif)  
* /ranklist - get a ranklist according to choice  
![alt text](https://github.com/Gotham13121997/superCodingBot/blob/master/gifs/ranklist.jpeg)  
* /upcoming - to get a list of upcoming competitions and setting a reminder for them  
![alt text](https://github.com/Gotham13121997/superCodingBot/blob/master/gifs/upcoming.gif)  
* /ongoing - to get a list of ongoing competitions  
![alt text](https://github.com/Gotham13121997/superCodingBot/blob/master/gifs/ongoing.gif)  
/dontremindme - to tell the bot not to remind you about a competition  
![alt text](https://github.com/Gotham13121997/superCodingBot/blob/master/gifs/dontremindme.gif)  
/subscribe - to subscribe for question of the day
/unsubscribe - to unsubscribe from question of the day  
![alt text](https://github.com/Gotham13121997/superCodingBot/blob/master/gifs/subscribe.gif)  

### ADMIN COMMANDS
* /givememydb - get the sqlite database
* /senddb - send and replace sqlite database
* /getcfjson - get the codeforcesjson file
* /sendcf - send and replace the codeforces json file
* /adminhandle - get a list of all handles
* /adminud - manually start updating all data
* /adminuq - manually start updating questions
* /adminrestart - restart the bot
