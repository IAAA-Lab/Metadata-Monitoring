package rdfManager;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Property;
import org.apache.jena.rdf.model.Resource;

/**
 * proporciona acceso a las propiedades rdf normalmente usadas
 * de forma centralizada
 */
public class RDFPropertyManager {
	//modelo temporal usado para construir las propiedades
	public static final Model tempModel = ModelFactory.createDefaultModel();
	
	// propiedades usadas de xml
	public static final String xmlsBaseUri = "http://www.w3.org/2001/XMLSchema#";
	public static final Resource xmlDecimalDataProp = tempModel.createResource(xmlsBaseUri+"decimal");
	public static final Property xmlDateDataProp = tempModel.createProperty(xmlsBaseUri+"date");
	
	//propiedades de rdf usadas
	public static final String rdfBaseUri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
	public static final String rdfTypeUri = rdfBaseUri+"type";
	public static final Property rdfTypeProp = tempModel.createProperty(rdfTypeUri);
	
	//propiedades usadas de rdfs
	public static final String rdfsBaseUri = "http://www.w3.org/2000/01/rdf-schema#";
	public static final Property rdfsSubclassOfProp = tempModel.createProperty(rdfsBaseUri+"subClassOf");
	public static final Property rdfsSubPropOfProp = tempModel.createProperty(rdfsBaseUri+"subPropertyOf");
	public static final Property rdfsDomainProp = tempModel.createProperty(rdfsBaseUri+"domain");
	public static final Property rdfsRangeProp = tempModel.createProperty(rdfsBaseUri+"range");
	public static final Property rdfsLabelProp = tempModel.createProperty(rdfsBaseUri+"label");
	public static final Property rdfsCommentProp = tempModel.createProperty(rdfsBaseUri+"comment");
	
	
	//propiedades usadas de rdfs extended
	public static final String rdfseNsPrefix="rdfse";
	public static final String rdfseBaseUri = "http://www.w3.org/2000/01/rdf-schemaExt#";
	public static final Property rdfseSuperclassOfProp = tempModel.createProperty(rdfseBaseUri+"superClassOf");
	
	//propiedades de dublinCoreusadas
	
	public static final String dcBaseUri = "http://purl.org/dc/elements/1.1/";
	public static final Property dcDescriptionProp = tempModel.createProperty(dcBaseUri+"description");
	public static final Property dcSubjectProp = tempModel.createProperty(dcBaseUri+"subject");
	public static final Property dcTitleProp = tempModel.createProperty(dcBaseUri+"title");
	public static final Property dcSourceProp = tempModel.createProperty(dcBaseUri+"source");
	public static final Property dcCreatorProp = tempModel.createProperty(dcBaseUri+"creator");
	public static final Property dcCoverageProp = tempModel.createProperty(dcBaseUri+"coverage");
	public static final Property dcDateProp = tempModel.createProperty(dcBaseUri+"date");
	public static final Property dcTypeProp = tempModel.createProperty(dcBaseUri+"type");
	public static final Property dcRelationProp = tempModel.createProperty(dcBaseUri+"relation");
	
	public static final String dctNsPrefix="dcterm";
	public static final String dctBaseUri = "http://purl.org/dc/terms/";
	public static final Property dctDescriptionProp = tempModel.createProperty(dctBaseUri+"description");
	public static final Property dctSubjectProp = tempModel.createProperty(dctBaseUri+"subject");
	public static final Property dctAbstractProp = tempModel.createProperty(dctBaseUri+"abstract");
	public static final Property dctIdentifierProp = tempModel.createProperty(dctBaseUri+"identifier");
	public static final Property dctTitleProp = tempModel.createProperty(dctBaseUri+"title");
	public static final Property dctLanguageProp = tempModel.createProperty(dctBaseUri+"language");
	public static final Property dctCreatedProp = tempModel.createProperty(dctBaseUri+"created");
	public static final Property dctPublishedProp = tempModel.createProperty(dctBaseUri+"published");
	public static final Property dctCoverageProp = tempModel.createProperty(dctBaseUri+"coverage");
	public static final Property dctIdentiferProp = tempModel.createProperty(dctBaseUri+"identifier");
	public static final Property dctReferencesProp = tempModel.createProperty(dctBaseUri+"references");
	public static final Property dctProvenanceProp = tempModel.createProperty(dctBaseUri+"provenance");
	public static final Property dctSpatialToProp = tempModel.createProperty(dctBaseUri, "spatial");
	public static final Property dctSourceProp = tempModel.createProperty(dctBaseUri, "source");
	public static final Property dctHasPartProp = tempModel.createProperty(dctBaseUri, "hasPart");
	public static final Property dctIsPartOfProp = tempModel.createProperty(dctBaseUri, "isPartOf");
	public static final Property dctLocationProp = tempModel.createProperty(dctBaseUri, "location");
	
	
	public static final String dceNsPrefix="dcext";
	public static final String dcExtBaseUri = "http://purl.org/dc/terms/ext/";
	public static final String dcExtScaleBaseUri = dcExtBaseUri+"eqScale/";
	public static final Property dcExtDateProp = tempModel.createProperty(dcExtBaseUri+"date");
	public static final Property dcExtScaleProp = tempModel.createProperty(dcExtBaseUri+"scale");
	public static final Property dcExtEqScaleProp = tempModel.createProperty(dcExtBaseUri+"eqScale");
	public static final Property dcExtProyProp = tempModel.createProperty(dcExtBaseUri+"projection");
	
	public static final Resource dcExtRSIDentRes = tempModel.createResource(dcExtBaseUri+"RS_Identifier");;
	public static final Property dcExtRSIProp = tempModel.createProperty(dcExtBaseUri+"rsi");
	public static final Property dcExtAuthorityProp = tempModel.createProperty(dcExtBaseUri+"authority");
	public static final Property dcExtCodeProp = tempModel.createProperty(dcExtBaseUri+"code");;
	
	
	public static final Property dcExtValueScaleProp =  tempModel.createProperty(dcExtScaleBaseUri+"value");
	public static final Property dcExtUnitScaleProp =  tempModel.createProperty(dcExtScaleBaseUri+"unitOfMeasure");
	public static final Property dcExtDenomScaleProp =  tempModel.createProperty(dcExtScaleBaseUri+"denominator");
	public static final Resource dcExtDistanceScaleRes =  tempModel.createResource(dcExtScaleBaseUri+"Distance");
	public static final Resource dcExtFractionScaleRes =  tempModel.createResource(dcExtScaleBaseUri+"Fraction");
	
	//propiedades de skos
	public static final String skosNsPrefix="skos";
	public static final String skosBaseUri = "http://www.w3.org/2004/02/skos/core#";
	public static final Property skosPrefLabelProp = tempModel.createProperty(skosBaseUri+"prefLabel");
	public static final Property skosAltLabelProp = tempModel.createProperty(skosBaseUri+"altLabel");
	public static final Property skosRelatedProp = tempModel.createProperty(skosBaseUri+"related");
	public static final Property skosDefinitionProp = tempModel.createProperty(skosBaseUri+"definition");	
	public static final Property skosScopeNoteProp = tempModel.createProperty(skosBaseUri+"scopeNote");	
	public static final Property skosPrefSymbolProp = tempModel.createProperty(skosBaseUri+"prefSymbol");		
	public static final Property skosHasTopConcProp = tempModel.createProperty(skosBaseUri+"hasTopConcept");
	public static final Property skosTopConcOfProp = tempModel.createProperty(skosBaseUri+"topConceptOf");
	public static final Property skosNarrowerProp = tempModel.createProperty(skosBaseUri+"narrower");
	public static final Property skosBroaderProp = tempModel.createProperty(skosBaseUri+"broader");
	public static final Property skosInSchemeProp = tempModel.createProperty(skosBaseUri+"inScheme");
	public static final Property skosNotationProp = tempModel.createProperty(skosBaseUri+"notation");	
	public static final Property skosMemberProp = tempModel.createProperty(skosBaseUri+"member");	
	public static final Resource skosCollectionRes = tempModel.createResource(skosBaseUri+"Collection");
	public static final Resource skosConceptRes = tempModel.createResource(skosBaseUri+"Concept");
	public static final Resource skosConceptSchemeRes = tempModel.createResource(skosBaseUri+"ConceptScheme");	
	//public static final String skosxlBaseUri = "http://www.w3.org/2008/05/skos-xl#";
	//public static final Property skosxlAltLabelProp = tempModel.createProperty(skosxlBaseUri+"altLabel");
	//public static final Property skosxlLiteralFormProp = tempModel.createProperty(skosxlBaseUri+"literalForm");
	
	public static final String skosXlUri = "http://www.w3.org/2008/05/skos-xl#";
	public static final Property skosXlPrefLabProp = tempModel.createProperty(skosXlUri+"prefLabel");
	public static final Property skosXlAltLabProp = tempModel.createProperty(skosXlUri+"altLabel");
	public static final Property skosXllitFormProp = tempModel.createProperty(skosXlUri+"literalForm");
	
	//propiedades de mapping usadas
	public static final String mapBaseUri = "http://www.w3c.rl.ac.uk/2003/11/21-skos-mapping#";
	public static final Property mapMajorMatchProp = tempModel.createProperty(mapBaseUri+"majorMatch");
	public static final Property mapMinorMatchProp = tempModel.createProperty(mapBaseUri+"minorMatch");
	public static final Property iaaaProbabilityProp = tempModel.createProperty("http://iaaa.cps.unizar.es#probability");
	
	//propiedades usadas de owl
	public static final String owlBaseUri = "http://www.w3.org/2002/07/owl#";
	public static final Property owlSameAsProp = tempModel.createProperty(owlBaseUri+"sameAs");
	public static final Property owlInverseOfProp = tempModel.createProperty(owlBaseUri+"inverseOf");
	public static final Property owlObjectPropTypeProp = tempModel.createProperty(owlBaseUri+"ObjectProperty");
	public static final Property owlDataPropTypeProp = tempModel.createProperty(owlBaseUri+"DatatypeProperty");
	public static final Resource owlClassRes = tempModel.createResource(owlBaseUri+"Class");
	
	//time ontology
	public static final String timeNsPrefix="time";
	public static final String timeBaseUri="http://www.w3.org/2006/time#";
	public static final Property timeYearProp = tempModel.createProperty(timeBaseUri+"year");
	public static final Resource timeDateTimeRes = tempModel.createProperty(timeBaseUri+"DateTimeDescription");
	
	//propiedades usadas de dolce
	public static final String dolceNsPrefix="dolce";
	public static final String dolceSrNsPrefix="dolceSr";
	public static final String dolceIONsPrefix="dolceIO";
	public static final String dolceDnsNsPrefix="dolceDns";
	public static final String dolceFunNsPrefix="dolceFun";
	public static final String dolceCSMNsPrefix="dolceCsm";

	//propiedades de dolce
	public static final String dolceBaseUri ="http://www.loa-cnr.it/ontologies/";
	public static final String dolcePubbyBaseUri= "http://www.eukn.org/eukn/thesaurus/dolceEq#";
	public static final String dolceSRelBaseUri= dolceBaseUri+"SpatialRelations.owl#";
	public static final String dolceLiteBaseUri= dolceBaseUri+"DOLCE-Lite.owl#";
	public static final String dolceInfObjBaseUri = dolceBaseUri+"InformationObjects.owl#";
	public static final String dolceExtDnsBaseUri = dolceBaseUri+"ExtendedDnS.owl#";	
	public static final String dolceFunBaseUri= dolceBaseUri+"FunctionalParticipation.owl#";
	public static final String dolceSocUnitBaseUri = dolceBaseUri+"SocialUnits.owl#";	
	public static final String dolceCSMBaseUri = dolceBaseUri+"CommonSenseMapping.owl#";	
	
	public static final Resource dolceParticularRes = tempModel.createResource(dolceLiteBaseUri+"particular");
	public static final Resource dolcePerdurantRes = tempModel.createResource(dolceLiteBaseUri+"perdurant");
	public static final Resource dolceOrganizationRes = tempModel.createResource(dolceSocUnitBaseUri+"organization");
	public static final Resource dolcePoliticalGeoObjRes = tempModel.createResource(dolceCSMBaseUri+"political-geographic-object");
	public static final Resource dolceInformationObjRes = tempModel.createResource(dolceExtDnsBaseUri+"information-object");
	public static final Resource dolceTimeIntervalRes = tempModel.createResource(dolceLiteBaseUri+"time-interval");
	
	public static final Property dolceGenericTargetOfProp = tempModel.createProperty(dolceFunBaseUri+"generic-target-of");
	public static final Property dolceInstrumentProp = tempModel.createProperty(dolceFunBaseUri+"instrument");
	public static final Property dolcePerformedByProp = tempModel.createProperty(dolceFunBaseUri+"performed-by");
	public static final Property dolceProductProp = tempModel.createProperty(dolceFunBaseUri+"product");
	public static final Property dolceResultProp = tempModel.createProperty(dolceFunBaseUri+"result");
	public static final Property dolcePerformsProp = tempModel.createProperty(dolceFunBaseUri+"performs");
	public static final Property dolceHasQualityProp = tempModel.createProperty(dolceLiteBaseUri+"has-quality");
	public static final Property dolceInherentInProp = tempModel.createProperty(dolceLiteBaseUri+"inherent-in");
	public static final Property dolceRegionProp = tempModel.createProperty(dolceLiteBaseUri+"region");
	public static final Property dolcePhisicalObjectProp = tempModel.createProperty(dolceLiteBaseUri+"physical-object");
	public static final Property dolceIdentifiesProp = tempModel.createProperty(dolceInfObjBaseUri+"identifies");
	public static final Property dolceIdentifiedByProp = tempModel.createProperty(dolceInfObjBaseUri+"identified-by");
	public static final Property dolcePartOfProp = tempModel.createProperty(dolceLiteBaseUri+"part-of");
	public static final Property dolcePartProp = tempModel.createProperty(dolceLiteBaseUri+"part");
	public static final Property dolceExpandsProp = tempModel.createProperty(dolceExtDnsBaseUri+"expands");
	public static final Property dolceAdoptedByProp = tempModel.createProperty(dolceExtDnsBaseUri+"adopted-by");
	public static final Property dolceAboutProp = tempModel.createProperty(dolceExtDnsBaseUri+"about");
	public static final Property dolceExpresedByProp = tempModel.createProperty(dolceExtDnsBaseUri+"expressed-by");
	public static final Property dolceActivityProp = tempModel.createProperty(dolceExtDnsBaseUri+"activity");
	public static final Property dolceOriginOfProp = tempModel.createProperty(dolceSRelBaseUri+"origin-of");
	public static final Property dolceDurationProp = tempModel.createProperty(dolceCSMBaseUri+"duration");
	public static final Property dolcedurationOfProp = tempModel.createProperty(dolceCSMBaseUri+"duration-of");
	public static final Property dolceCountedByProp = tempModel.createProperty(dolceCSMBaseUri+"counted-by");

	//propiedades usadas de iaaa
	public static final String metadataNsPrefix="mdata";
	public static final String metadataBaseUri = "http://iaaa.cps.unizar.es/metadata#";
	public static final Resource metadataMdRes = tempModel.createResource(metadataBaseUri+"Metadata");
	
	//uris de tesauros usados comunmente
	public static final String euknBaseUri = "http://www.eukn.org/eukn/";
	
	/********************************************************************************/
	/**
	 * metodo general de creacion de propiedades para cuando no exista la necesaria
	 */
	public static Property createProperty(String uri){
		return tempModel.createProperty(uri);
	}	
	
	/*****************************************************************/
	/**
	 * Metodo para obtener una propuedade de un recurso o null si no existe
	 */
	public static  String getProperty(Resource res, Property prop){
		try{return res.getProperty(prop).getString();}catch (Exception er){};
		return null;
	}
	
	
	/*****************************************************************/
	/**
	 * Metodo para añadir propiedad textual en un idioma a un recurso, si dicha propiedad
	 * no existe añade null
	 */
	public static void addProperty(Resource res, Property prop, String lang, String value){
		if(value !=null && res !=null && prop !=null && lang !=null){
			res.addProperty(prop, res.getModel().createLiteral(value.trim(), lang));
		}
	}
	
}
