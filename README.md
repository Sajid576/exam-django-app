# ExamSpace-Django-Backend


# To run the project on windows:
  py -m venv venv
  .\venv\Scripts\activate
  pip install -r requirements.txt
  python manage.py makemigrations
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver


# To Run the project on linux:
  virtualenv venv
  source venv/bin/activate
  pip install -r requirements.txt
  python manage.py makemigrations
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver
---------------------------------------------------------------------------------------------------------------------

# To deploy django in gcp standard app engine:
  * Follow the guidelines of the below link to download and install google SDK:
    https://cloud.google.com/sdk/docs/install
  

  * Few important gcloud commands to set up the project:
    gcloud init
    gcloud projects list
    gcloud config configurations list
    gcloud config set project `PROJECT ID`


  * Three external services have been used along with the backend:
    1. Postgres SQL Database (To store data)

    2. Redis Database (To store access and refresh key for authentication)
    
    3. Bucket for Media Storage (To store images and other user uploaded files)
    
    All of the services have already been configured with `settings.py` file.
  

  * To reflect the changes of your models to the production SQL database follow the below instructions:
    1. First download and install cloud sql proxy from the following link and rename it as `cloud_sql_proxy.exe`:
        https://cloud.google.com/sql/docs/mysql/sql-proxy#linux-64-bit
    
    2. Use the below command to get the connection name:
        gcloud sql instances describe `INSTANCE_NAME`
        For this project, `INSTANCE_NAME` = examspace-database
    
    3. Run the below command to connect to the sql database from your local machine:
        cloud_sql_proxy.exe -instances="`YOUR_INSTANCE_CONNECTION_NAME`"=tcp:3306
        For this project the connection name is as follows:
        `YOUR_INSTANCE_CONNECTION_NAME` = exms-302404:asia-southeast1:exms-database

    4. Now that the connection is established use the following command to migrate the changes of the models:
        python3 manage.py migrate


  * To deploy the codebase use the below instructions:
    1. Go to your project folder. Make sure the correct git branch is checked out.
    
    2. Open the terminal / command prompt and use the following command to deploy the codebase:
        gcloud app deploy      


# To show server log, use the following command:
  gcloud app logs tail -s default


# To directly access app engine standard DB from local machine use the below command:
  1. First establish the connection as described above using cloud sql proxy
  
  2. Then run the following command:
      psql -U "USERNAME" -p "PORT_NO" --host 127.0.0.1


# To get redis database description, use the below command (Not part of deployment):
  gcloud redis instances describe examspace-redis --region=asia-southeast1
---------------------------------------------------------------------------------------------------------------------

# To run the project on VM instance, follow the below instruction:
  1. It is the same as running the project on linux as described above except the last command.
  
  2. Replace the last command with the below command:
      nohup python3 "path/to/manage.py/file" runserver 0.0.0.0:8000 &
  
  N.B: This method is only for development purposes. If you desire to run the server on VM instance for production purpose, it is recommended to use nginx web server.  


# To connect VM instance DB from local machine, follow the below guidelines:
  1. Configure PostgreSQL remote access:
      https://cloud.google.com/community/tutorials/setting-up-postgres#connecting_remotely
  
  2. Open the network port:
      https://cloud.google.com/community/tutorials/setting-up-postgres#open_the_network_port
  
  3. Connect using the below command: 
      psql -U "DB_USERNAME" -p "DB_PORT_NO" --host "VM_EXTERNAL_IP_ADDRESS"
  
  DB_USERNAME, DB_PORT_NO & VM_EXTERNAL_IP_ADDRESS are provided in the environment file which is located at "Environemt" folder under the Backend channel of "Examspace" Team.