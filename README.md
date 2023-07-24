# Software requirements
- Ubuntu 22.04
- Node.js v16.x
- Python3
- MongoDB 6.0
- Fuseki

# Installation and execution on Ubuntu 22.04
## 1. Installation of Node.js v16
We need to install specifically version 16, as this is required for the client implemented with Angular.
First, we need to install curl if not previously installed:
```
sudo apt-get install curl
```
Then, we download the specfic version of node.js and we install it:
```
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```
The version installed should be v16. In can be checked with the following command:
```
node-v
```
## 2. Installation of dependencies in the backend and front end
First, we need to install depedencies at the backend from a terminal
```
cd backend
npm install
```
Probably, npm nodemon is also required:
```
npm install nodemon --save-dev
```
Second, we need to install the dependecies at the frontend:
```
cd frontend
npm install
```
## 3. Installation and launch of MongoDB service
For the installation of the MongoDB database, we can follow the instructions from https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/

```
sudo apt-get install gnupg curl

curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
   --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

sudo apt-get update

sudo apt-get install -y mongodb-org
```
The MongoDB service can be started on a terminal with the following command: 
```
service mongod start
```
The service should be started at this connection URL: mongodb://localhost:27017
If necessary, the service can be stopped with the following command:
```
service mongod stop
```
## 4. Creation of the MongoDB database
The MongoDB database can be administered with Studio 3T application.
The instllation of this application is explained at https://studio3t.com/knowledge-base/articles/how-to-install-studio-3t-on-linux/ . After donwloading the installation compressed, file, we need to unzip:
```
tar -xvzf studio-3t-linux-x64.tar.gz
```
and execute the installation:
```
sh studio-3t-linux-x64.sh
```
Then, we start Studio 3T and we establish a connection with the MongoDB service (localhost, port: 27017). After having established the connection, we need to create two databases: 'results' and 'agenda'.
Within 'results' database, we need to create the collection 'admins' with the information of two users. These two users can be created executing the following instructions through Studio 3T:
```
db.admins.insert({ username: "user", password: "user" })
db.admins.insert({ username: “admin”, password: “admin” })
```
If we want an enhanced security for the  login of users, we can modify 'scquema.js' (admin_schema) to use comparisons with encrypting function.

## 5. Start the backend and frontend
If we are using an IDE for the development like Webstorm, we can start directly the backend and frontend from this IDE. Otherwise, we can start them from a terminal with 'npm'. In the case of the backend, we would execute the following:
```
cd backend
npm start
```
In the case of the frontend, it would be similar:
```
cd frontend
npm start
```
Then, the frontend should be accessible from a browser at http://localhost:4200/

The execution of backend and frontend can be stopped with Ctrl+C.

## 6. Intallation and launch of Fuseki
If the evaluation of an Open Data portal is performed locally with a copy of the metadata contents, we need a triple-store to save temporally the metadata and query it with SPARQL. For the deployment of this triple-store we have decided to use a Docker container with Fuseki technology. The installation and execution of the container just requires the execution of the following command:
```
docker run -d -p 3030:3030 -e ADMIN_PASSWORD=pass123 stain/jena-fuseki
```
This will download the neccessary software (if not performed previously) and will start the Fuseki web portal at  http://localhost:3030. 

The first time we access the portal, we need to login as 'admin' with passwork 'pass123'. In case of not specifying a password with the docker command, this password is auto-generated. In case of autogeneration, we need to check the logs (using 'docker logs') or directly the output if the -d option was not used.

More information at: https://hub.docker.com/r/stain/jena-fuseki/ 

# Modificaciones sobre el código python
- Se añade en las primeras lineas del main() lo siguiente para cambiar el working directory a la ubicación del propio archivo y que funcionen las rutas relativas:
```
# Change the working directory to the file location
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
```
- Se debe indicar en el código del backend, que el python que ejecuta el fichero es el disponible en el entorno virtual, en este caso:
```
./app_server/pythonPrograms/my-environment/bin/python3
```
