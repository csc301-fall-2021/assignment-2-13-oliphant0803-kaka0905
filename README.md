[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-f059dc9a6f8d3a56e377f745f24479a46679e63a5d9fe6f495e02850cd0d8118.svg)](https://classroom.github.com/online_ide?assignment_repo_id=6163542&assignment_repo_type=AssignmentRepo)
### Dev Branch
Your API needs to be deployed and running on a server (e.g., Heroku, AWS, Google Cloud, etc.). You can refer to our “Cloud Resources” page to learn more about your options. You need to share the details of your server (e.g., url, routes) in your submission so your TAs know how to test your application. Your program needs to be able to do the following: 

Add a new data file: You can assume the file is consistent and follows the format specified here (Links to an external site.). You can use one of the files in this GitHub repo. The files have two possible formats:
Time Series (Links to an external site.) (/time_series/): You should implement this first. The user should be able to send a csv file to your program. Your program needs to account for the different types of time series that are in the linked repo.
Daily reports (Links to an external site.) (/daily_reports): These are more detailed files that take in the data one day at a time. Your program needs to be able to take this information in as well. 
Note: With both of the formats above, you only need to store the data we would want to query later. You don’t need to store everything.

Update existing files (/time_series/ or /daily_reports/): If a file is uploaded again, you should update the data you store to reflect the new information.
Query data by one or more countries, provinces/states, combined_keys (/cases): The data can be any of the following:
* Deaths
* Confirmed
* Active
* Recovered 
#### Any one day or a period of time
#### Your program should support returning the data in multiple formats:
* JSON
* CSV
