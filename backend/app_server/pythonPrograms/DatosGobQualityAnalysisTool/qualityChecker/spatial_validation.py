###############################################
# Analiza la calidad de la información espacial
###############################################
import csv, os, spacy
from qualityChecker import *
from qualityChecker.file_manager import save_data_file, load_data_file
from shapely.geometry import Point, Polygon
import shapely.wkt
import unidecode


#Fucheros de datos necesitados por las funciones de validacióne spacial
geonamesFile = "data/input/geonamesSpain.txt"
jdoAdminFile =  "data/input/spainJdoAdminComp.owl"
jdoSpatialFile = "data/input/spainJdoGeoComp.owl"

#propiedades a rdf del modelo jdo a mirar
tipoProvClass = "http://www.jurisdictionalDomain.org/spainJurisdictionalDomain.owl#provincia"
tipoCCAAClass = "http://www.jurisdictionalDomain.org/spainJurisdictionalDomain.owl#comunidad-autonoma"
identifiesDProp = "http://www.loa-cnr.it/ontologies/InformationObjects.owl#identifies"
realizedbyDProp = "http://www.loa-cnr.it/ontologies/ExtendedDnS.owl#realized-by"
prefLabelProp = "http://www.w3.org/2004/02/skos/core#prefLabel"


###############################################
# generamos un map con la info del fichero de long lat de los lugares en geonames
###############################################
def loadGeonamesPlaces():
    coordStore = dict()
    with open(geonamesFile, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            punto = Point(float(row[5]),float(row[4]))
            masnombres = row[3].split(",")
            masnombres.append(row[1])
            for nombre in masnombres:
                nombre = unidecode.unidecode(nombre.strip().lower())
                if nombre in coordStore.keys():
                    coordStore[nombre].append(punto)
                else:
                    coordStore[nombre]= [punto]
    return coordStore

###############################################
# carga los nombres de lugar con sus poligonos y selecciona aquellos que no son municipios
###############################################
def loadJurisdictionalOntology():
    rdfModel = loadRdfFiles([jdoAdminFile,jdoSpatialFile])
    #obtenemos los recursos con uris a procesar
    query = 'select ?x ?y where {{?x <'+rdfTypeProp+'> <' + tipoProvClass + '>} union {?x <'+rdfTypeProp+'> <' + tipoCCAAClass + '>}}'
    rows = rdfModel.query(query)
    resources = [];
    for row in rows:
        resources.append(row.x)

    # adjuntamos sus coordenadas espaciales
    mapaEsp = dict()
    for res in resources:
        if res.endswith("ESP010") or res.endswith("ESP015") or res.endswith("ES"):continue
        coordsOb = list(x for x in rdfModel.objects(URIRef(res), URIRef(identifiesDProp)))[0]
        coords = list(x for x in rdfModel.objects(URIRef(coordsOb), URIRef(realizedbyDProp)))[0]
        label = list(x for x in rdfModel.objects(URIRef(res), URIRef(prefLabelProp)))[0]
        mapaEsp[unidecode.unidecode(str(label).lower())]=str(coords)
    return mapaEsp

###############################################
# inicializa los modelos de necesarios para comparar, lo guarda en variables globales
###############################################
geonames = None; jdocoords = None; nlp = None
def initSpatialModels():
    global geonames
    global jdocoords
    global nlp
    #geonames = loadGeonamesPlaces()
    #save_data_file("data/temp/geonames.bin", geonames)
    geonames = load_data_file("data/temp/geonames.bin")

    #jdocoords = loadJurisdictionalOntology()
    #save_data_file("data/temp/jdocoords.bin", jdocoords)
    jdocoords = load_data_file("data/temp/jdocoords.bin")

    nlp = spacy.load('es_core_news_sm')

###############################################
# realiza el analisis de la informacion espacial
###############################################

def analyzeSpatialQuality(dsSpatialAllRefs):
    #inicializamos los contadores de calidad
    correctSpRef=0;unknownSpRef=0;totalSpRef=len(dsSpatialAllRefs)
    errorMd = ""

    #miramos la info espacial de todos los metadatos
    for ref in dsSpatialAllRefs:
        #obtenemos la info extraida de los metadatos
        #nos quedamos solo con las etituetas en español
        uri = ref["uri"]
        spatial = ref[spatialProp]
        titlees =""
        for tit in ref[titleProp]:
            if tit.language == "es": titlees = tit.value
        descres =""
        for des in ref[descriptionProp]:
            if des.language == "es": descres = des.value

        #obtenemos los nombres de lugar de los sitios a los que se refiere el metadato e identificamos su poligono
        onlySpainRef = False
        spatialPol =[]
        spatialPolName = []
        for nameuri in spatial:
            #sacamos el nombre de la uri de la propiedad espacial
            name = corrigeProvNames(os.path.basename(str(nameuri)).lower())

            #si el nombre es españa y no hay mas nombres consideramso ls referencia correcta, si no nos la saltamos
            if name == "españa":
                if len(spatial)==1:
                    onlySpainRef=True
                continue

            #en otro caso buscamos el poligono asociado al nombre
            if name in jdocoords.keys():
                geom = jdocoords[name]
                polygon = shapely.wkt.loads(geom)
                spatialPol.append(polygon)
                spatialPolName.append(name)
            else:
                print ("no encontrado ", name)

        #las referencias de españa siempre estan bien
        if onlySpainRef:
            correctSpRef += 1
            continue


        #obtenemos las coordenadas de los nonbres en los metadatos
        doc = nlp(titlees+" . "+descres)
        coordNames = []
        nameNames = []
        for ent in doc.ents:
            if(ent.label_ == "LOC"):
                name = unidecode.unidecode(ent.text.strip().lower())
                if name not in geonames.keys():
                    subnames = name.split(" ")
                    for sn in subnames:
                        if sn in geonames.keys():
                            coordNames.extend(geonames[sn])
                            nameNames.append(sn)
                else:
                    coordNames.extend(geonames[name])
                    nameNames.append(name)

        # si no hay info spacial, la marcamos como no detectada
        if len(spatialPol)==0 or len(coordNames)==0:
            unknownSpRef +=1
        else: #miramos si al menos una de las coordenadas esta dentro de los poligonos del espatial
            foundCoord=False
            for coord in coordNames:
                for polygon in spatialPol:
                    if polygon.contains(coord):
                        foundCoord = True
                        correctSpRef +=1
                        break
                if foundCoord: break
            #si la info espacial es mala, nos guardamos el lugar y los terminos
            if not foundCoord:
                errorMd+=str(uri)+ " | "+ str(spatialPolName) + " | " + str(nameNames)  + "\n"

    #print(totalSpRef,correctSpRef,unknownSpRef)

    # generamos el report
    result = spatialProp + "\n"
    result += "totalDistinctSpRefs: " + str(totalSpRef) + ", validSpRefs: " + str(correctSpRef) + ", unknownSpRefs: " + str(unknownSpRef) + " \n"
    return result, errorMd

def corrigeProvNames(name):
    if name == "valencia" : return "valencia/valencia"
    if name == "comunitat-valenciana": return "comunidad valenciana"
    if name == "a-coruna": return "a coruna"
    if name == "la-rioja": return "la rioja"
    if name == "comunidad-madrid": return "madrid"
    if name == "principado-asturias": return "principado de asturias "
    if name == "la-palmas": return "palmas, las"
    if name == "las-palmas": return "palmas, las"
    if name == "cataluna": return "cataluna/catalunya"
    if name == "illes-balears": return "illes balears"
    if name == "ceuta": return "ciudad de ceuta"
    if name == "melilla": return "ciudad de melilla"
    if name == "region-murcia": return "murcia"
    if name == "pais-vasco": return "pais vasco/euskadi"
    if name == "castilla-la-mancha": return "castilla-la mancha"
    if name == "castilla-leon": return "castilla y leon"
    if name == "comunidad-foral-navarra": return "comunidad foral de navarra"
    if name == "ciudad-real": return "ciudad real"
    if name == "castellon": return "castello/castellon"
    if name == "santa-cruz-tenerife": return "santa cruz de tenerife"
    if name == "alicante": return "alacant/alicante"
    return name


###############################################
# Clase para almacenar las coordenadas x e y de un lugar
###############################################
class Coordinates:
    def __init__(self, Lat, Long):
        self.Latitude=Lat
        self.Longitude=Long