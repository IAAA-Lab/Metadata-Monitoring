# Software utilizado
- Ubuntu 20.04
- Node.js v16.16.0
- Python3 (se utiliza un entorno virtual, por lo que la versión concreta no es relevante)
- MongoDB 4.4.5
- Fuseki

# Instalación de dependencias
## Node.js
Para instalar las dependencias necesarias se debe ubicar en la carpeta 'backen' o 'frontend' para cada caso y ejecutar en una terminal:
```
npm install
```

# Ejecución
## MongoDB
MongoDB debe estar ejecutandose para que la aplicación funcione correctamente, para esto, se puede ejecutar sobre una terminal:
```
service mongod start
```
Igualmente podrá deternerse cuando sea necesario mediante:
```
service mongod stop
```

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