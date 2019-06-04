# cmpe272-property-listing-app


# Install Property Listing Application

This application is optimized to work in Python3, check to see if you have python3 on your host

``python3 --version``

Make sure you have the following python3 packages

``pymongo``, ``flask``, ``jwt``, ``authlib``, ``python-dotenv``

If you don't have, use the below method to install python3 packages

``python3 -m pip install <package-name>``

PS: Application has been tested to work with Python2 as well, but recommend to run it in python3 
  
  ### Important Assumption - This application expects Mongodb to be installed along with the data provided by Prof for this project (and this application has been coded to have the database name as abnb with three collections, named respectively calendar, listings and reviews. These collection shall be populated with the data provide by prof in the data.zip)
  
  Will try and automate the package requirements using appropraite method and upload the file to the git soon.
  
  For now the below three steps are to be done manually.
  
  1.Git clone the repo
  
  2.Run below command to install all the needed python packages/modules as specified/listed in the setup.py
  
  ``pip install -e . ``
  
  3.Add the below environment variable 
  
`` export AUTH0_CLIENT_SECRET=Client secret goes here ``

`` export AUTH0_AUDIENCE=https://airbnb/teamamk ``

`` export AUTH0_DOMAIN=Auth0 domain info goes here ``

`` export AUTH0_CLIENT_ID=client ID goes here ``

`` export AUTH0_CALLBACK_URL=http://localhost:5000/callback ``

  
  4.Run the below command to start the application
  
  `` python3 app.py ``
  
  5.Use a browser to access the below URL after confirming that there are no issues running the above applcation and host is listening on port 5000
  
  `` http://localhost:5000 ``
  
  6.Use the login option and use Google credential to enter the property listings. Alternatively a user ID/password can be created using the signup option to get authenticated using the local authentication infra provided by Auth0.
