Project name-- Live stock market watch list and alert system.
Front and end-- Java script framework(React JS)
Backend-- python based framework (flask)
Database-- postgresSQL. 
Installation-:
1.Python(latest version)
2.Miniconda(latest version)
3.PostgresSQL(latest version)
4.pgadmin
5.React JS(latest version)
6.Flask framework (latest version)
7.visual studio code editer

Steps to run this program--
1.Open miniconda prompt initialize following comands
        i. conda create --name myenv python=3.10
        ii. conda activate myenv
        iii. conda install flask
        iv. conda install flask_sqlalchemy
        v. pip install flask-socketio
        vi. pip install flask-jwt-extended
        vii. pip install flask-jwt-extended
        viii. pip install Flask-Mail
        xi. pip install Flask-Migrate Flask-SQLAlchemy
2.Create database. 
3.Downlord zip file from git hub link and  extract it.
4.In db config file update your database username, password, email id& email id app password(createapp password from your respective gmail google account).
5. Then set extract file path in conda promt with your environment 
6. then run the backend program with comand - flask run 
7. simultaniously open terminal for frontend ans set the path, then install following comands
                    i. npm install socket.io-client@4.8.1
8. then run frontend with comand - npm start
