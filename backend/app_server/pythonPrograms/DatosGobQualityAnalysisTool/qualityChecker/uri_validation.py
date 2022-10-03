#######################################################
#Realiza la validación de las uris
#######################################################

from qualityChecker import *
import time, urllib.parse
from ftfy import fix_encoding

mimetypesFile = "data/input/mimetypes.txt"

#######################################################
# Realiza el checkeo de las uris proporcionadas en un vector
#######################################################
def validateGenericUrisExistence (uris):
    #count =0
    urisReport = []
    count=0
    for uri in uris:
        print(count, uri)
        urlReport = URL(urllib.parse.quote(uri, ':/?=&%@*_+-.'), offline=False, timeout=10)
        urisReport.append(UriInfo(uri, urlReport.isValid(), urlReport.isAccesible(), urlReport.getType()))
        time.sleep(.500)
        #if count ==100: break
        count+=1
    return urisReport


#######################################################
# Realiza el checkeo de las uris proporcionadas en un vector
#######################################################
def validateGenericUrisExistenceText (uris, fileOut, createNew =False):
    os.makedirs(os.path.dirname(fileOut), exist_ok=True)
    #si el fichero de resutlados existe, miramos por donde continuar
    start = 0; mode = "w"
    if (not createNew) and os.path.isfile(fileOut):
        mode = "a+"
        with open(fileOut, "r") as text_file:
            linea =""
            for line in text_file: linea=line
            start = int(line.split("\t")[0])
        start+=1
    print("Primer registro procesado:",start)

    #leemos los datos indicados desde el inicial
    with open(fileOut, mode) as text_file:
        count = start
        for x in range(start, len(uris)):
            uri = uris[x]
            urlReport = URL(urllib.parse.quote(uri, ':/?=&%@*_+-.'), offline=False, timeout=10)
            text_file.write(str(count)+"\t"+str(urlReport)+"\n")
            count=count+1
            time.sleep(.500)

#######################################################
# Realiza el checkeo de las uris proporcionadas en un vector
#######################################################
def validateGenericUrisExistenceLimit (uris, init,end):
    #count =0
    urisReport = []
    for x in range(init, end):
        uri = uris[x]
        print(x)
        #print(uri)
        urlReport = URL(urllib.parse.quote(uri, ':/?=&%@*_+-.'))
        urisReport.append(UriInfo(uri, urlReport.isValid(), urlReport.isAccesible(), urlReport.getType()))
        time.sleep(.500)
        #if count ==100: break
        #count+=1
    return urisReport

#######################################################
# Guarda en una cadena de texto el report de la calidad de una uri
#######################################################
def analyzeUriQuality (sFile, classe, prop):
    urisValidas = 0; urisAccesibles = 0
    errors = ""; result = classe+" | "+prop+"\n"
    with open(sFile, 'r') as fp:
        count =0
        for line in fp:
            count +=1
            componentesLinea = line.split("\t")
            valid = componentesLinea[2]
            accesible = componentesLinea[5]

            #miramos si es una uri valida
            if valid == "True" :
                urisValidas += 1
                if accesible =="True":  urisAccesibles +=1
                else: errors += line
            else: errors += line
        result += "totalUris: " + str(count) +", validUris: "+str(urisValidas)+ ", accesibleUris: "+str(urisAccesibles)+" \n"
    return result, errors


#######################################################
# Guarda en una cadena de texto el report de la calidad de una uri
#######################################################
def analyzeUriQualityOld (uriRefs, property):
    #contamos el numero de uris validas
    urisValidas = 0
    errors=""
    for uri in uriRefs:
        if(uri.isValid()): urisValidas +=1
        else: errors+="No valida | "+uri.uri +"\n"

    #contamos el numero de uris accesibles
    urisAccesibles = 0
    for uri in uriRefs:
        if(uri.isAccesible()): urisAccesibles +=1
        else: errors+="No accesible | " + str(uri.accesible.status) +" | " + str(uri.accesible.reason) +" |" + str(uri.accesible.sslError) +" |" + uri.uri +"\n"

    #generamos el report
    #print(property, str(len(uriRefs)),str(urisValidas),str(urisAccesibles))
    result = property+"\n"
    result += "totalDistinctUris: " + str(len(uriRefs)) +", validUris: "+str(urisValidas)+ ", accesibleUris: "+str(urisAccesibles)+" \n"
    return result, errors

#######################################################
# Realiza la comprobación de los formatos
#######################################################
'''
def coherentFormat(magic, http,extension, formatInfo, mimes):
    #pasamos toda la info a mayusculas para facilitar la comparacion
    label = formatInfo[labelProp].lower()
    value = formatInfo[valueProp].lower()
    url = formatInfo[accessUrlProp]

    if label in mimes.keys():
        mime = mimes[label]
        if mime in value:
            magic =magic.lower()
            http = http.lower()
            extension = extension.lower()
            # miramos la coherencia entre la info de formato de los metadatos
            if label not in magic and label not in http and label not in extension and mime not in http:
                #print("Incoherent data-metadata format:", label, type.http, type.extension, type.magic, url)
                return False, "Incoherent data-metadata format:"+ label +" | http: "+http+" | extension: "+ extension+" | magic: "+ magic +" | " + url
            return True, ""
        else:
            return False, "Incoherent metadata-format:" + label +" | mime: "+value
    else:
        return False, "Non-mime format: " + label +" | mime: "+value
'''
#######################################################
# Realiza la comprobación de los formatos
#######################################################
def analyzeFormatQuality(formatUrls, formInfo):
    mimes = loadMimeTypes()

    formatValido = 0; correlacionFormato = 0;
    ferrorReport = "";
    #miramos cada descripcion del formato y la info de la uri de acceso asociada para ver si hay coherencia entre toda la info
    for num, form in enumerate(formInfo):
        #correlacion label value del format, saver si es mime y el label esta bien
        label = form[labelProp].lower()
        value = form[valueProp].lower()
        url = form[accessUrlProp]
        if value not in mimes.values():
            ferrorReport += url + "\tLa etiqueta en el formato no es un tipo mime\t" + label + "\t" + value + "\n"
        elif label not in value:
            ferrorReport += url + "\tSin correlación entre propiedades label-value en el formato\t" + label + "\t" + value + "\n"
        else:
            formatValido+=1
            line = formatUrls[num]
            componentesLinea = line.split("\t")
            accesible = componentesLinea[5]
            magic = componentesLinea[7]
            http = componentesLinea[8]
            extension = componentesLinea[9]
            if label not in magic and label not in http and label not in extension:
                ferrorReport += url + "\tSin correlación entre formato indicado y real del fichero\t" + label + "\t" + value + "\t" + magic + "\t" + http + "\t" + extension + "\n"
            else:
                correlacionFormato += 1
    result = "Analisis correlación formato dentro del nodo rdf y respecto al formato del fichero\n"
    result += "Total formatos analizados: "+ str(len(formInfo)) + ", Num propiedades con formato valido (corr etiqueta-valor): " + str(formatValido) +", Num props con correlacion propiedad-formato validas: " + str(correlacionFormato)
    return result, ferrorReport

#######################################################
# Cargar mimetypes
#######################################################
def loadMimeTypes():
    mimes = dict()
    with open(mimetypesFile, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            extension = row[0].replace(".","")
            mimitype = row[1]
            mimes[extension]=mimitype
    return mimes


#######################################################
# clase para almacenar la informacion de una uri
#######################################################
class UriInfo:
    def __init__(self, uri, valid, accesible, type):
        self.uri=uri
        self.valid=bool(valid)
        self.accesible= accesible
        self.type = type
    def isValid(self): return self.valid
    def isAccesible(self): return self.accesible.isAccesible
    def getType(self): return self.type