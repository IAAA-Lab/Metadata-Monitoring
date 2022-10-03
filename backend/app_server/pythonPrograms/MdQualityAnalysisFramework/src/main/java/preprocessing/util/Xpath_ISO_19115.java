package preprocessing.util;

/**
 * contiene los xpath para acceder a los campos que deseemos del ISO_19115
 */
public class Xpath_ISO_19115 {
	private boolean isMetadata;
	public static final String md = "MD_DataIdentification";
	public static final String sr = "SV_ServiceIdentification";

	public String exprId = "/*[local-name()='MD_Metadata']/*[local-name()='fileIdentifier']/*[local-name()='CharacterString']";
	public String exprPar = "/*[local-name()='MD_Metadata']/*[local-name()='parentIdentifier']/*[local-name()='CharacterString']";
	public String exprLan = "/*[local-name()='MD_Metadata']/*[local-name()='language']/*[local-name()='CharacterString']";
	public String exprHier = "/*[local-name()='MD_Metadata']/*[local-name()='hierarchyLevel']/*[local-name()='MD_ScopeCode']";
	public String exprBB, exprPlace, exprTitle, exprAltTitle, exprAbstract, exprSerie, exprAgrName, exprAgrId;

	/**
	 * Crea las expresiones xpath necesarias para extraer información de metadatos de datos o de servicios
	 * según sea le parametro del constructor
	 */
	public Xpath_ISO_19115(boolean isMetadata) {
		//nos guardamos el tipo de metadato
		this.isMetadata = isMetadata;
		String type = md; if (!isMetadata) {type = sr;}

		//construimos las expresiones de xpath en función del tipo de metadato
		exprBB = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/" + "*[local-name()='" + type
				+ "']/*[local-name()='extent']/" + "*[local-name()='EX_Extent']/*[local-name()='geographicElement']/"
				+ "*[local-name()='EX_GeographicBoundingBox']";

		exprPlace = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/" + "*[local-name()='" + type
				+ "']/*[local-name()='descriptiveKeywords']/" + "*[local-name()='MD_Keywords']/*[local-name()='type']/"
				+ "*[local-name()='MD_KeywordTypeCode']";

		exprTitle = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/" + "*[local-name()='" + type
				+ "']/*[local-name()='citation']/" + "*[local-name()='CI_Citation']/*[local-name()='title']/"
				+ "*[local-name()='CharacterString']";

		exprAltTitle = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/" + "*[local-name()='"
				+ type + "']/*[local-name()='citation']/"
				+ "*[local-name()='CI_Citation']/*[local-name()='alternateTitle']/"
				+ "*[local-name()='CharacterString']";

		exprAbstract = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/" + "*[local-name()='"
				+ type + "']/*[local-name()='abstract']/" + "*[local-name()='CharacterString']";

		exprSerie = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/" + "*[local-name()='" + type
				+ "']/*[local-name()='citation']/" + "*[local-name()='CI_Citation']/*[local-name()='title']/"
				+ "*[local-name()='CharacterString']";

		exprAgrName = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/" + "*[local-name()='" + type
				+ "']/*[local-name()='aggregationInfo']/"
				+ "*[local-name()='MD_AggregateInformation']/*[local-name()='aggregateDataSetName']/"
				+ "*[local-name()='CI_Citation']/*[local-name()='title']/" + "*[local-name()='CharacterString']";

		exprAgrId = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/" + "*[local-name()='" + type
				+ "']/*[local-name()='aggregationInfo']/"
				+ "*[local-name()='MD_AggregateInformation']/*[local-name()='aggregateDataSetIdentifier']/"
				+ "*[local-name()='RS_Identifier']/*[local-name()='code']/" + "*[local-name()='CharacterString']";
	}

	/****************************************************************************/
	/**
	 * devuelve el nombre del nodo que identifica si el metadato es de datos o servicios
	 */
	public String getType() {
		if (isMetadata) { return md;} else {return sr;}
	}
}
