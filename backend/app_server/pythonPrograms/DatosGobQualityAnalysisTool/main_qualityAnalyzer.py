#######################################################
# Realiza la validación completa de los metadatos
#######################################################

from qualityChecker import *


#fichero con los metadatos a cargar
sourceFile = "data/input/datosgobes20190612.rdf"
destFile = "data/output/qualityReport.txt"
outDir = "data/output"
tempDir = "data/temp"

#nombres de ficheros donde almacenar el report de las uris
dsConformsUriReportFile = "dsConformslUriReport.txt"
dsSpatialUriReportFile = "dsSpatialUriReport.txt"
dsThemeUriReportFile = "dsThemeUriReport.txt"
dsIdentifierUriReportFile = "dsIdentifierUriReport.txt"
dsDistributionUriReportFile = "dsDistriburionUriReport.txt"
dsPublisherUriReportFile = "dsPublisherUriReport.txt"
dsReferencesUriReportFile = "dsReferencesUriReport.txt"
dsLicenseUriReportFile = "dsLicenseUriReport.txt"
diIdentifierUriReportFile = "diIdentifierUriReport.txt"
diReferencesUriReportFile = "diReferencesUriReport.txt"
diFormatUriReportFile = "diFormatUriReport.txt"
diAccessUriReportFile = "diAccessUriReport.txt"
diLicenseUriReportFile ="diLicenseUriReport.txt"

#fichero para almacenar si las referencias espaciales tienen contenido correcto o no  segun el titulo y descripcion
dsSpatialContentCorrectnessReportFile = tempDir + "/" + "dsSpatialContentCorrecnessReport.bin"
diAccessFormatReportFile = tempDir + "/" + "diAccessFormatReport.bin"
dsSpatialContentCorrectnessErrorFile = outDir + "/" + "dsSpatialContentCorrecnessErrorReport.txt"
diAccessFormatErrorFile = outDir + "/" + "diAccessFormatErrortReport.txt"

################################################
# cargamos el modelo rdf de un rdf o de un fichero de pickle
################################################
def loadRDFModel():
    # rdfModel = loadRdfFile(sourceFile)
    # save_data_file(tempDir + "/rdfModel.bin", rdfModel)
    return load_data_file(tempDir + "/rdfModel.bin")

################################################
# Comprueba las uris de las propiedades del experimento, guarda el resultado en ficheros en el directorio indicado
################################################
def getAndSavePropertyReports(rdfModel):
    print("--- Accediendo a las uris del campo license en distribution")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, distributionClass, licenseProp),tempDir + "/" + diLicenseUriReportFile)
    '''
    print("--- Accediendo a las uris del campo conforms to")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, datasetClass, conformsProp), tempDir + "/" + dsConformsUriReportFile)
    print("--- Accediendo a las uris del dataset de referencia espacial")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, datasetClass, spatialProp), tempDir + "/" + dsSpatialUriReportFile)
    print("--- Accediendo a las uris del dataset de tema")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, datasetClass, themeProp), tempDir + "/" + dsThemeUriReportFile)
    print("--- Accediendo a las uris del dataset de identificador")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, datasetClass, identifierProp), tempDir + "/" + dsIdentifierUriReportFile)
    print("--- Accediendo a las uris del dataset de distribucion")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, datasetClass, distributionProp), tempDir + "/" + dsDistributionUriReportFile)
    print("--- Accediendo a las uris del dataset de publicador")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, datasetClass, publisherProp), tempDir + "/" + dsPublisherUriReportFile)
    print("--- Accediendo a las uris del dataset de referencias")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, datasetClass, referencesProp), tempDir + "/" + dsReferencesUriReportFile)
    print("--- Accediendo a las uris del dataset de licencia")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, datasetClass, licenseProp), tempDir + "/" + dsLicenseUriReportFile)
    print("--- Accediendo a las uris de la distribución de identificador")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, distributionClass, identifierProp), tempDir + "/" + diIdentifierUriReportFile)
    print("--- Accediendo a las uris de la distribución de referencia")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, distributionClass, referencesProp), tempDir + "/" + diReferencesUriReportFile)
    print("--- Accediendo a las uris de la distribución de formato")
    validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, distributionClass, formatProp), tempDir + "/" + diFormatUriReportFile)

    print("--- Accediendo a las uris de acceso al fichero de datos")
    formInfo = getFormatInfo(rdfModel)
    save_data_file(diAccessFormatReportFile, formInfo)
    formatUrls = []
    for est in formInfo:
        formatUrls.append(est[accessUrlProp])
    validateGenericUrisExistenceText(formatUrls, tempDir + "/" +diAccessUriReportFile)

    # identificamos las referencias espaciales correctas e incorrectas segun el titulo y resumen
    print("Accediendo a la info para calcular la correlación espacial con titulo y descripción")
    dsSpatialAllRefs = getMultiplePropertyValues(rdfModel, datasetClass, [spatialProp, descriptionProp, titleProp])
    save_data_file(dsSpatialContentCorrectnessReportFile, dsSpatialAllRefs)

    '''

################################################
# Comprueba las uris de las propiedades del experimento, guarda el resultado en ficheros en el directorio indicado
################################################
def generateUriQualityProp(sFile, prop, classe):
    qr, error = analyzeUriQuality(tempDir + "/" + sFile, classe, prop)
    save_text_file(outDir + "/" + sFile, error)
    return qr

def generateAndSaveQualitySummary():
    qualityReport =""

    '''
    #sumary de la coherencia espacial
    dsSpatialAllRefs = load_data_file(dsSpatialContentCorrectnessReportFile)
    initSpatialModels()
    qr, error = analyzeSpatialQuality(dsSpatialAllRefs)
    qualityReport+=qr
    save_text_file(dsSpatialContentCorrectnessErrorFile, error)
'''
    #sumary de las calidades de las uris
    qualityReport += generateUriQualityProp(dsConformsUriReportFile, datasetClass, conformsProp)
    qualityReport += generateUriQualityProp(diLicenseUriReportFile, distributionClass, licenseProp)
    qualityReport += generateUriQualityProp(diAccessUriReportFile, distributionClass, accessUrlProp)
    '''
    qualityReport += generateUriQualityProp(dsSpatialUriReportFile, datasetClass, spatialProp)
    qualityReport += generateUriQualityProp(dsThemeUriReportFile, datasetClass, themeProp,)
    qualityReport += generateUriQualityProp(dsIdentifierUriReportFile, datasetClass, identifierProp)
    qualityReport += generateUriQualityProp(dsDistributionUriReportFile, datasetClass, distributionProp)
    qualityReport += generateUriQualityProp(dsPublisherUriReportFile, datasetClass, publisherProp)
    qualityReport += generateUriQualityProp(dsReferencesUriReportFile, datasetClass, referencesProp)
    qualityReport += generateUriQualityProp(dsLicenseUriReportFile, datasetClass, licenseProp)
    qualityReport += generateUriQualityProp(diIdentifierUriReportFile, distributionClass, identifierProp)
    qualityReport += generateUriQualityProp(diReferencesUriReportFile, distributionClass, referencesProp)
    qualityReport += generateUriQualityProp(diFormatUriReportFile, distributionClass, formatProp)
    

    #summary de la coherencia campo formato y formato uri acceso
    dsAccessRefs = load_text_file(tempDir + "/" + diAccessUriReportFile)
    formInfo = load_data_file(diAccessFormatReportFile)
    qr, formatErrorReport = analyzeFormatQuality(dsAccessRefs, formInfo)
    qualityReport += qr
    save_text_file(diAccessFormatErrorFile, formatErrorReport)
'''
    #guardamos el report resumido
    save_text_file(destFile, qualityReport)


#######################################################
# Inicio del programa principal
#######################################################
if __name__ == "__main__":
    #cargamos el modelo
    print("Cargando el modelo rdf a procesar")
    #rdfModel = loadRDFModel()

    #descargamos y guardamos en ficheros la el report de acceso de las uris de todas las propiedades
    print("Generando los reports de cada una de las propiedades propiedades")
    #getAndSavePropertyReports(rdfModel)

    #generamos el resumen de todas las propiedades analizadas
    print("Generando el resumen de la calidad de los campos")
    generateAndSaveQualitySummary()



    '''
    #comprobación correctitud espacial
    print("Verificando correctitud refs espaciales")
    dsSpatialAllRefs = getMultiplePropertyValues(rdfModel, datasetClass, [spatialProp, descriptionProp, titleProp])
    save_data_file(tempDir + "/spatialAllRefs.bin", dsSpatialAllRefs)
    dsSpatialAllRefs = load_data_file(tempDir + "/spatialAllRefs.bin")
    initSpatialModels()
    qualityReport, error = analyzeSpatialQuality(dsSpatialAllRefs)
    save_text_file(outDir + "/spatialCoherenceErrorReport.txt", error)
    

    #comprobación correctitud uris de los dataset
    print("Verificando correctitud uris ref espacial")
    dsSpatialRefs = validateGenericUrisExistence(getAllPropertyValues(rdfModel, datasetClass, spatialProp))
    save_data_file(tempDir + "/dsSpatialRefs.bin", dsSpatialRefs)
    dsSpatialRefs = load_data_file(tempDir + "/dsSpatialRefs.bin")
    qr, error = analyzeUriQuality(dsSpatialRefs, spatialProp)
    qualityReport += qr
    save_text_file(outDir+"/spatialUriErrorReport.txt", error)
   
    print("Verificando correctitud uris tema")
    dsThemeRefs = validateGenericUrisExistence(getAllPropertyValues (rdfModel, datasetClass, themeProp))
    save_data_file(tempDir + "/dsThemeRefs.bin", dsThemeRefs)
    dsThemeRefs = load_data_file(tempDir + "/dsThemeRefs.bin")
    qr, error = analyzeUriQuality(dsThemeRefs, themeProp)
    qualityReport += qr
    save_text_file(outDir + "/themeUriErrorReport.txt", error)
    
    print("Verificando correctitud uris identificador")
    dsIdentifierRefs = validateGenericUrisExistence(getAllPropertyValues(rdfModel, datasetClass, identifierProp))
    save_data_file(tempDir + "/dsIdentifierRefs.bin", dsIdentifierRefs)
    dsIdentifierRefs = load_data_file(tempDir + "/dsIdentifierRefs.bin")
    qr, error = analyzeUriQuality(dsIdentifierRefs, identifierProp)
    qualityReport += qr
    save_text_file(outDir + "/identifierUriErrorReport.txt", error)
    
    print("Verificando correctitud uris distribucion")
    uris = getAllPropertyValues(rdfModel, datasetClass, distributionProp)
    #dsDistributionRefs  = validateGenericUrisExistenceLimit(uris, 0, 55000)
    #save_data_file(tempDir + "/dsDistributionRefsP1.bin", dsDistributionRefs)
    #dsDistributionRefs  = validateGenericUrisExistenceLimit(uris, 55000, len(uris))
    #save_data_file(tempDir + "/dsDistributionRefsP2.bin", dsDistributionRefs)
    dsDistributionRefs1 = load_data_file(tempDir + "/dsDistributionRefsP1.bin")
    dsDistributionRefs2 = load_data_file(tempDir + "/dsDistributionRefsP2.bin")
    dsDistributionRefs = dsDistributionRefs1 + dsDistributionRefs2
    qr, error = analyzeUriQuality(dsDistributionRefs, distributionProp)
    qualityReport += qr
    save_text_file(outDir + "/distribUriErrorReport.txt", error)
    
    print("Verificando correctitud uris publicador")
    dsPublisherRefs = validateGenericUrisExistence(getAllPropertyValues(rdfModel, datasetClass, publisherProp))
    save_data_file(tempDir + "/dsPublisherRefs.bin", dsPublisherRefs)
    dsPublisherRefs = load_data_file(tempDir + "/dsPublisherRefs.bin")
    qr, error = analyzeUriQuality(dsPublisherRefs, publisherProp)
    qualityReport += qr
    save_text_file(outDir + "/publisherUriErrorReport.txt", error)
    
    print("Verificando correctitud uris referencias")
    dsReferencesRefs = validateGenericUrisExistence(getAllPropertyValues(rdfModel, datasetClass, referencesProp))
    save_data_file(tempDir + "/dsReferencesRefs.bin", dsReferencesRefs)
    dsReferencesRefs = load_data_file(tempDir + "/dsReferencesRefs.bin")
    qr, error = analyzeUriQuality(dsReferencesRefs, referencesProp)
    qualityReport += qr
    save_text_file(outDir + "/referencesUriErrorReport.txt", error)
    
    print("Verificando correctitud uris licencia")
    dsLicenseRefs = validateGenericUrisExistence(getAllPropertyValues(rdfModel, datasetClass, licenseProp))
    save_data_file(tempDir + "/dsLicenseRefs.bin", dsLicenseRefs)
    dsLicenseRefs = load_data_file(tempDir + "/dsLicenseRefs.bin")
    qr, error = analyzeUriQuality(dsLicenseRefs, licenseProp)
    qualityReport += qr
    save_text_file(outDir + "/licenseUriErrorReport.txt", error)
    
    # comprobación correctitud uris de las distribuciones
    print("Verificando correctitud uris identifier distrib")
    #print(len(getAllPropertyValues(rdfModel, distributionClass, identifierProp)))
    diIdentifierRefs = validateGenericUrisExistenceText(getAllPropertyValues(rdfModel, distributionClass, identifierProp), tempDir + "/diIdentifierRefs.txt")
    #save_data_file(tempDir + "/diIdentifierRefs.bin", diIdentifierRefs)
    #diIdentifierRefs = load_data_file(tempDir + "/diIdentifierRefs.bin")
    #qr, error = analyzeUriQuality(diIdentifierRefs,identifierProp)
    #qualityReport += qr
    #save_text_file(outDir + "/distidentUriErrorReport.txt", error)
    
    print("Verificando correctitud uris reference distrib")
    diReferencesRefs = validateGenericUrisExistence(getAllPropertyValues(rdfModel, distributionClass, referencesProp))
    save_data_file(tempDir + "/diReferencesRefs.bin", diReferencesRefs)
    diReferencesRefs = load_data_file(tempDir + "/diReferencesRefs.bin")
    qr, error = analyzeUriQuality(diReferencesRefs, referencesProp)
    qualityReport += qr
    save_text_file(outDir + "/distrefUriErrorReport.txt", error)

    print("Verificando correctitud uris format distr")
    dsFormatRefs = validateGenericUrisExistence(getAllPropertyValues(rdfModel, distributionClass, formatProp))
    save_data_file(tempDir + "/dsFormatRefs.bin", dsFormatRefs)
    dsFormatRefs = load_data_file(tempDir + "/dsFormatRefs.bin")
    qr, error = analyzeUriQuality(dsFormatRefs, formatProp)
    qualityReport += qr
    save_text_file(outDir + "/spatialUriErrorReport.txt", error)
    
    print("Verificando correctitud uris access format distr")
    formInfo = getFormatInfo(rdfModel)
    formatUrls = []
    for est in formInfo:
        formatUrls.append(est[accessUrlProp])
    dsAccessRefs =  validateGenericUrisExistence(formatUrls)
    save_data_file(tempDir + "/dsAccessRefs.bin", dsAccessRefs)
    save_data_file(tempDir + "/formInfo.bin", formInfo)
    dsAccessRefs = load_data_file(tempDir + "/dsAccessRefs.bin")
    formInfo = load_data_file(tempDir + "/formInfo.bin")
    qr, formatErrorReport = analyzeFormatQuality(dsAccessRefs, formInfo)
    qualityReport += qr
    save_text_file(outDir+"/formatErrorReport.txt", formatErrorReport)
    '''

    #guardamos el report de calidad del resultado
    #save_text_file(destFile,qualityReport)




