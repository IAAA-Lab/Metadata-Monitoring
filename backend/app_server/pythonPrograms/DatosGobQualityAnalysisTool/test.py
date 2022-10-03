
import pickle, os

#clases del modelo
datasetClass = "http://www.w3.org/ns/dcat#Dataset"
distributionClass = "http://www.w3.org/ns/dcat#Distribution"

#propiedades a leer de spatial
spatialProp = "http://purl.org/dc/terms/spatial"
descriptionProp ="http://purl.org/dc/terms/description"
titleProp ="http://purl.org/dc/terms/title"

#propiedades a leer de uri
themeProp = "http://www.w3.org/ns/dcat#theme"
identifierProp = "http://purl.org/dc/terms/identifier"
distributionProp ="http://www.w3.org/ns/dcat#distribution"
publisherProp = "http://purl.org/dc/terms/publisher"
referencesProp = "http://purl.org/dc/terms/references"
licenseProp = "http://purl.org/dc/terms/license"
formatProp = "http://purl.org/dc/terms/format"
accessUrlProp = "http://www.w3.org/ns/dcat#accessURL"
formatProp = "http://purl.org/dc/terms/format"
labelProp ="http://www.w3.org/2000/01/rdf-schema#label"
valueProp ="http://www.w3.org/1999/02/22-rdf-syntax-ns#value"
rdfTypeProp="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

dirTemp = "data/temp"

################################################
# Carga los datos de un fichero y los devuelve tal cual, sin modificar nada
################################################
def load_data_file(file):
    with open(file, 'rb') as fp: return pickle.load(fp)

################################################
# Guarda una cadena de texto en fichero de texto
################################################
def save_text_file(fileOut, data):
    os.makedirs(os.path.dirname(fileOut), exist_ok=True)
    with open(fileOut, "w") as text_file:
        for uri in uris:
            print(uri)
            text_file.write(str(uri.encode("utf-8"))+"\n")


#######################################################
# obtiene todos los valores de una propiedad, cor restricciones del tipo de nodo en la que esta
#######################################################
def getAllPropertyValues(rdfModel, type, property):
    # obtenemos todos los recursos que tengan la primera propiedad
    resources = []
    rows = rdfModel.query(
        'select distinct ?y where { ?x <' + property + '> ?y . ?x <' + rdfTypeProp + '> <' + type + '>}')

    # añadimos las propiedades
    result = []
    for row in rows:
        result.append(str(row.y))
    return result


rdfModel = load_data_file(dirTemp + "/rdfModel.bin")

#uris = getAllPropertyValues(rdfModel, distributionClass, identifierProp)
uris = getAllPropertyValues(rdfModel, datasetClass, distributionProp)


save_text_file(dirTemp + "/uris2.txt", uris)




