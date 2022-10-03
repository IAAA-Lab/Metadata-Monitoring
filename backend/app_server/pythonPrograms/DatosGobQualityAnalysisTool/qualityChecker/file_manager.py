################################################
# CFunciones para cargar y guardar ficheros
################################################
import pickle, os

################################################
# Carga los datos de un fichero y los devuelve tal cual, sin modificar nada
################################################
def load_data_file(file):
    with open(file, 'rb') as fp: return pickle.load(fp)

################################################
# Carga los datos de un fichero de texto y los devuelve tal cual, sin modificar nada
################################################
def load_text_file(file):
    lineas = []
    with open(file, "r") as text_file:
        for line in text_file: lineas.append(line)
    return lineas

################################################
# Guarda una variable en un fichero sin tocarla para nada
################################################
def save_data_file(fileOut, data):
    os.makedirs(os.path.dirname(fileOut), exist_ok=True)
    with open(fileOut, 'wb') as fp: pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)


################################################
# Guarda una cadena de texto en fichero de texto
################################################
def save_text_file(fileOut, data):
    os.makedirs(os.path.dirname(fileOut), exist_ok=True)
    with open(fileOut, "w", encoding="utf-8") as text_file: text_file.write(data)