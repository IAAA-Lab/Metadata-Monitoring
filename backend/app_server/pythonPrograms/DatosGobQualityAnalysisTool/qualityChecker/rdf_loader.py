#######################################################
# Lee los metadatos del fichero indicado y obtiene todos valores de la propiedad deseada
#######################################################

import sys
from rdflib import Graph, URIRef

#clases del modelo
datasetClass = "http://www.w3.org/ns/dcat#Dataset"
distributionClass = "http://www.w3.org/ns/dcat#Distribution"

#propiedades a leer de spatial
spatialProp = "http://purl.org/dc/terms/spatial"
descriptionProp ="http://purl.org/dc/terms/description"
titleProp ="http://purl.org/dc/terms/title"

#propiedades a leer de uri
conformsProp ="http://purl.org/dc/terms/conformsTo"
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

#######################################################
# Lee el grafo rdf en un modelo en memoria
#######################################################
def loadRdfFile(sourceFile):
    # leemos el grafo del rdf, desactivamos la salida de error para que no molesten los warnings
    rdfModel = Graph()
    error_out = sys.stderr;
    #sys.stderr = None
    rdfModel.load(sourceFile)
    #sys.stderr = error_out
    return rdfModel

#######################################################
# Lee ungrafo en memoria a partir de un conjunto de ficheros
#######################################################
def loadRdfFiles(sourceFiles):
    # leemos el grafo del rdf, desactivamos la salida de error para que no molesten los warnings
    rdfModel = Graph()
    for sourF in sourceFiles:
        rdfModel.load(sourF)
    return rdfModel

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

#######################################################
# obtiene varias propiedades de un nodo
#######################################################
def getMultiplePropertyValues(rdfModel, type, propertyList):
    #obtenemos todos los recursos que tengan la primera propiedad
    resources = []
    rows = rdfModel.query('select distinct ?x where { ?x <' + propertyList[0] + '> ?y . ?x <'+rdfTypeProp+'> <' + type + '>}')

    #añadimos juntas las propiedades relacionadas que deseamos obtener
    result = []
    for row in rows:
        resultRes = dict()
        resultRes["uri"] = row.x
        for prop in propertyList:
            resultRes[prop]=list(x for x in rdfModel.objects(URIRef(row.x), URIRef(prop)))
        result.append(resultRes)
    return result


#######################################################
# obtiene la informacion de una popiedad de un nodo determinado
#######################################################
def getPropertyValue (rdfModel, node, property):
    return rdfModel.objects(node, property)

#######################################################
# obtiene la informacion de la propiedad de formato con sus subnodos
#######################################################

def getFormatInfo (rdfModel):
    resources = []
    rows = rdfModel.query('select distinct ?x where { ?x <' + accessUrlProp + '> ?y. ?x <' + rdfTypeProp + '> <' + distributionClass + '>}')
    result = []
    for row in rows:
        resultRes = dict()
        resultRes[accessUrlProp] = list(x for x in rdfModel.objects(URIRef(row.x), URIRef(accessUrlProp)))[0].value
        resultRes[labelProp] = None
        resultRes[valueProp] = None
        formatSubnore = list(x for x in rdfModel.objects(URIRef(row.x), URIRef(formatProp)))
        if formatSubnore is not None:
            resultRes[labelProp] = list(x for x in rdfModel.objects(URIRef(formatSubnore[0]), URIRef(labelProp)))[0].value.lower()
            resultRes[valueProp] = list(x for x in rdfModel.objects(URIRef(formatSubnore[0]), URIRef(valueProp)))[0].value.lower()
        result.append(resultRes)
    return result




