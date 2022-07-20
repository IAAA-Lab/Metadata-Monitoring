# Modificaciones sobre el código python
- Los imports estilo "from mqa_sparql.MQAevaluate import MQAevaluate" se cambian por "from MQAevaluate import MQAevaluate"
- Se añade en las primeras lineas del main() lo siguiente para cambiar el working directory a la ubicación del propio archivo y que funcionen las rutas relativas:
```
# Change the working directory to the file location
abspath = os.path.abspath(__file__)<br>
dname = os.path.dirname(abspath)<br>
os.chdir(dname)
```
- Se debe indicar en el código del backend, que el python que ejecuta el fichero es el disponible en el entorno virtual, en este caso:
```
./app_server/pythonPrograms/my-environment/bin/python3
```