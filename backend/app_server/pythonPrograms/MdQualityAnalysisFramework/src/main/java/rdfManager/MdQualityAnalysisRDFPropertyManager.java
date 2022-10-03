package rdfManager;

import org.apache.jena.datatypes.BaseDatatype;
import org.apache.jena.datatypes.RDFDatatype;
import org.apache.jena.rdf.model.Property;

/**
 * contiene las propiedades de rdf especificas al procesamiento de los datos del
 * crawler
 */
public class MdQualityAnalysisRDFPropertyManager extends RDFPropertyManager {
	// propiedades del vocabualrio a usar para almacenar los capmpos a los que
	// se les hará el analisis de calidad
	public static final String validationVocBaseUri = "http://iaaa.cps.unizar.es/metadataValidation/vocabulary#";

	public static final Property fileIdentifier = tempModel.createProperty(validationVocBaseUri, "fileIdentifier");
	public static final Property parentIdentifier = tempModel.createProperty(validationVocBaseUri, "parentIdentifier");
	public static final Property referenceSystemInfo = tempModel.createProperty(validationVocBaseUri,
			"referenceSystemInfo");
	public static final Property boundingBox = tempModel.createProperty(validationVocBaseUri,
			"EX_GeographicBoundingBox");
	public static final Property language = tempModel.createProperty(validationVocBaseUri, "language");
	public static final Property hierarchyLevel = tempModel.createProperty(validationVocBaseUri, "hierarchyLevel");
	public static final Property placeKeyword = tempModel.createProperty(validationVocBaseUri, "placeKeyword");
	public static final Property placeText = tempModel.createProperty(validationVocBaseUri, "placeText");
	public static final Property placeGateKeyword = tempModel.createProperty(validationVocBaseUri, "placeGateKeyword");
	public static final Property mdType = tempModel.createProperty(validationVocBaseUri, "resourceType");

	public static final Property title = tempModel.createProperty(validationVocBaseUri, "title");
	public static final Property alttitle = tempModel.createProperty(validationVocBaseUri, "alttitle");
	public static final Property astract = tempModel.createProperty(validationVocBaseUri, "abstract");
	public static final Property aggregateDataSetName = tempModel.createProperty(validationVocBaseUri,
			"aggregateDataSetName");
	public static final Property aggregateDataSetIdentifier = tempModel.createProperty(validationVocBaseUri,
			"aggregateDataSetIdentifier");
	public static final Property xmlValidationErrors = tempModel.createProperty(validationVocBaseUri,
			"xmlValidationErrors");

	// propiedades espaciales
	public static final Property spatialProp = tempModel.createProperty(validationVocBaseUri, "metaEnvelope");
	public static final Property spatialmxProp = tempModel.createProperty(validationVocBaseUri, "maxx");
	public static final Property spatialmyProp = tempModel.createProperty(validationVocBaseUri, "maxy");
	public static final Property spatialixProp = tempModel.createProperty(validationVocBaseUri, "minx");
	public static final Property spatialiyProp = tempModel.createProperty(validationVocBaseUri, "miny");
	public static final Property sdiCrsProp = tempModel.createProperty(validationVocBaseUri, "crs");

	public static final String webServiceTypeUri = validationVocBaseUri + "Service";
	public static final String wmLayerTypeUri = validationVocBaseUri + "NamedLayer";
	public static final String wmCategoryLayerTypeUri = validationVocBaseUri + "CategoryLayer";

	public static final String crs84Uri = "http://www.opengis.net/def/crs/OGC/1.3/CRS84";
	public static final RDFDatatype wktRdfType = new BaseDatatype("http://www.opengis.net/rdf#wktLiteral");

	// propiedades iso19115
	public static final String validationColBaseUri = "http://iaaa.cps.unizar.es/metadataValidation/collection/";

	// quality analysis result
	public static final Property bbAnalysysResult = tempModel.createProperty(validationVocBaseUri,
			"bbQualityAnalysisResult");
	public static final Property placeAnalysisResult = tempModel.createProperty(validationVocBaseUri,
			"placeAnalysisResult");
	public static final Property bbPlaceCorrelationAnalysisResult = tempModel.createProperty(validationVocBaseUri,
			"bbPlaceCorrelationAnalysisResult");
	public static final Property bbPlaceTextCorrelationAnalysisResult = tempModel.createProperty(validationVocBaseUri,
			"bbPlaceTextCorrelationAnalysisResult");
	public static final Property textPlacesFound = tempModel.createProperty(validationVocBaseUri, "textPlacesFound");

	public static final Property placeJdoUri = tempModel.createProperty(validationVocBaseUri, "placeJdoUri");

}
