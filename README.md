# superCodingBot
TELEGRAM BOT FOR COMPETITIVE PROGRAMMERS 
# SYNOPSIS
superCodingBot is a telegram bot built in python using python-telegram-bot wrapper.It can be used as a tool to check progress in
Competitive Programming, get the ongoing and upcoming competitions and also compile and run programs using hackerrank api. Programming websites supported are
Hackerearth, Hackerrank, Codechef, Spoj, Codeforces
# LIBRARIES USED
PYTHON-TELEGRAM-BOT
HTML5LIB
BEAUTIFUL SOUP
HACKERRANK API
APSCHEDULER
XLMX WRITER
# USAGE
You can use it by replacing the token in app.py with your telegram bot token wich you can get from telegrams official site by activating 
bot father and api key by replacing the api key generated on hackerrank.com, you need to login to hackerrank to do that. You need to host the 
script, For hosting on open shift online just change the token and api key, save the files in a git repository, then create an account on redhat
create a project, choose python latest version and put the path of your repository and build your application.
# COMMANDS
/help- to get a list of commands used  
/register - to register your handle to the bot  
/unregister - unregister your handle from the bot  
/update - initialise the updation of your info  
Automatic update takes place every day at 0:00 by APScheduler  
/ranklist - to get a ranklist  
/upcoming - to see a list of upcoming competitions  
/ongoing - to see a list of ongoing competitions  
/compiler - to compile and run program  
/adminhandle - to get a list of all handles  
/adminupdate - to update all info  
