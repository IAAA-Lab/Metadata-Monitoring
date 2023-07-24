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
The version installed should be v16
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


## Frontend y Backend
En caso de no utilizar un IDE que facilite la ejecución de la aplicación web, puede ejecutarse mediante una terminal accediendo a las carpetas 'backend' y 'frontend', en función de qué componente se quiere ejecutar, y para ambos casos utilizar la instrucción:

```
npm start
```

y detener la ejecución mediante Ctrl+C.

## Fuseki
Para la ejecución de un portal local SPARQL se ha utilizado Fuseki mediante Docker, por lo que para ejecutarlo, tan solo es necesario utilizar la instrucción:
```
docker run -d -p 3030:3030 -e ADMIN_PASSWORD=pass123 stain/jena-fuseki
```
Esto descargará (si no se había hecho previamente) e iniciará el portal web de fuseki en http://localhost:3030. La primera vez que se accede al portal tras comenzar su ejecución requiere el acceso de un usuario y contraseña. El usuario es 'admin' y en este caso, la contraseña necesaria será 'pass123'. En caso de no especificar una contraseña, se autogenera una cada vez que se ejecuta el portal, por lo que es necesario mirar los logs mediante 'docker logs' o bien directamente del output si se ha ejecutado sin la opción -d.

Para más información: https://hub.docker.com/r/stain/jena-fuseki/ 

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
