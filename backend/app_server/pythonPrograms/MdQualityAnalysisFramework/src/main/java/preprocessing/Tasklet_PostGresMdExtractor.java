package preprocessing;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathFactory;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Property;
import org.apache.jena.rdf.model.Resource;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import preprocessing.util.Xpath_ISO_19115;
import rdfManager.JenaModelManager;
import rdfManager.MdQualityAnalysisRDFPropertyManager;
import rdfManager.RDFPropertyManager;

/**
 * Extrae los metadatos de una base de datos de postgres
 */
public class Tasklet_PostGresMdExtractor implements Tasklet {

	// fichero fuente
	protected String destinationFile;

	// database connection
	protected String dbname, dbuser, dbpass, dbhost, dbport;

	// lector de xml y consultas a hacer
	protected XPath xpath = XPathFactory.newInstance().newXPath();

	protected Xpath_ISO_19115 mdt = new Xpath_ISO_19115(true);
	protected Xpath_ISO_19115 mds = new Xpath_ISO_19115(false);

	/************************************************************/
	/**
	 * aplica tecnicas de inferencia para enriquecer la informacion de los
	 * servicios con la de las capas y viceversa
	 */

	public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
		// creamos el modelo destino
		Model model = ModelFactory.createDefaultModel();

		// nos conectamos a la base de datos
		Class.forName("org.postgresql.Driver").newInstance();
		String url = "jdbc:postgresql://" + dbhost + ":" + dbport + "/" + dbname;
		Connection conn = DriverManager.getConnection(url, dbuser, dbpass);
		conn.setAutoCommit(false);

		// lector de xml;
		DocumentBuilder builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();

		// leemos todos los metadatos
		Statement st = conn.createStatement();
		st.setFetchSize(50);
		ResultSet r = st.executeQuery("SELECT data from metadata");
		int i=0;
		while (r.next()) {
			i++;
			String md = new String(r.getString(1).getBytes(StandardCharsets.UTF_8));
			if (md.contains(Xpath_ISO_19115.md)) {
				addResource(md, mdt, model, builder);
			} else {
				addResource(md, mds, model, builder);
			}
		}
		System.out.println(i);
		conn.close();
		//guardamos el con los metadatos extraidos
		model.setNsPrefix("qvoc", MdQualityAnalysisRDFPropertyManager.validationVocBaseUri);
		JenaModelManager.saveJenaModel(model, destinationFile);
		return RepeatStatus.FINISHED;
	}

	/**************************************************************************/
	/**
	 * Estrae del metadato todo lo que nos interesa almacenar y lo guarda en un modelo dejena
	 */
	protected Resource addResource(String md, Xpath_ISO_19115 type, Model model, DocumentBuilder builder)
			throws Exception {
		Document doc = builder.parse(new ByteArrayInputStream(md.getBytes(StandardCharsets.UTF_8)));
		String identifier = xpath.compile(type.exprId).evaluate(doc);
		Resource res = model.createResource(MdQualityAnalysisRDFPropertyManager.validationColBaseUri + identifier);
		res.addProperty(RDFPropertyManager.rdfTypeProp, "metadataFromIdee");
		addProperty(res, MdQualityAnalysisRDFPropertyManager.fileIdentifier, doc, type.exprId, identifier);
		addProperty(res, MdQualityAnalysisRDFPropertyManager.parentIdentifier, doc, type.exprPar, identifier);

		addProperty(res, MdQualityAnalysisRDFPropertyManager.title, doc, type.exprTitle, identifier);
		addProperty(res, MdQualityAnalysisRDFPropertyManager.alttitle, doc, type.exprAltTitle, identifier);
		addProperty(res, MdQualityAnalysisRDFPropertyManager.astract, doc, type.exprAbstract, identifier);

		addProperty(res, MdQualityAnalysisRDFPropertyManager.aggregateDataSetName, doc, type.exprAgrName, identifier);
		addProperty(res, MdQualityAnalysisRDFPropertyManager.aggregateDataSetIdentifier, doc, type.exprAgrId,
				identifier);
		addSpatialProperty(res, MdQualityAnalysisRDFPropertyManager.boundingBox, doc, type.exprBB);
		addProperty(res, MdQualityAnalysisRDFPropertyManager.language, doc, type.exprLan, identifier);
		addAtrProperty(res, MdQualityAnalysisRDFPropertyManager.hierarchyLevel, doc, type.exprHier, "codeListValue",
				identifier);
		addPlaceKeyProperty(res, MdQualityAnalysisRDFPropertyManager.placeKeyword, doc, type.exprPlace,
				"codeListValue");
		res.addProperty(MdQualityAnalysisRDFPropertyManager.mdType, type.getType());
		return res;
	}

	/***************************************************************/
	/**
	 * Añade al recurso en la propiedad indicada el valor sacado del atributo
	 * del xpath indicado
	 */
	protected void addAtrProperty(Resource res, Property prop, Document doc, String path, String atr, String mdId)
			throws Exception {
		NodeList nodeList = (NodeList) xpath.compile(path).evaluate(doc, XPathConstants.NODESET);
		try {
			for (int i = 0; i < nodeList.getLength(); i++) {
				Node nod = nodeList.item(i);
				if (nod.getAttributes().getNamedItem(atr) != null) {
					res.addProperty(prop, nod.getAttributes().getNamedItem(atr).getNodeValue());
				} else {
					res.addProperty(prop, nod.getFirstChild().getNodeValue());
				}
			}
		} catch (Exception er) {
			System.out.println("Error leyendo:" + mdId + " " + prop.getLocalName());
		}
	}

	/**
	 * Añade al recurso en la propiedad indicada el valor sacado de las palabras
	 * clave de lugar
	 */
	protected void addPlaceKeyProperty(Resource res, Property prop, Document doc, String path, String atr)
			throws Exception {
		String keyword = "*[local-name()='keyword']/*[local-name()='CharacterString']";
		NodeList nodeList = (NodeList) xpath.compile(path).evaluate(doc, XPathConstants.NODESET);
		for (int i = 0; i < nodeList.getLength(); i++) {
			String value = nodeList.item(i).getAttributes().getNamedItem(atr).getNodeValue();
			if (value.equals("place")) {
				Node baseK = nodeList.item(i).getParentNode().getParentNode();
				NodeList nodeListK = (NodeList) xpath.evaluate(keyword, baseK, XPathConstants.NODESET);
				for (int j = 0; j < nodeListK.getLength(); j++) {
					res.addProperty(prop, nodeListK.item(j).getFirstChild().getNodeValue());
				}
			}
		}
	}

	/**
	 * Añade al recurso en la propiedad indicada el valor sacado del xpath
	 * indicado
	 */
	protected void addProperty(Resource res, Property prop, Document doc, String path, String mdId) throws Exception {
		NodeList nodeList = (NodeList) xpath.compile(path).evaluate(doc, XPathConstants.NODESET);
		try {
			for (int i = 0; i < nodeList.getLength(); i++) {
				res.addProperty(prop, nodeList.item(i).getFirstChild().getNodeValue());
			}
		} catch (Exception er) {
			System.out.println("Error leyendo:" + mdId + " " + prop.getLocalName());
		}
	}

	/**
	 * Añade al recurso el bounding box, se pasa el path base y a partir de el
	 * saca las 4 coordenadas
	 */
	protected void addSpatialProperty(Resource res, Property prop, Document doc, String path) throws Exception {
		String north = "*[local-name()='northBoundLatitude']/*[local-name()='Decimal']";
		String south = "*[local-name()='southBoundLatitude']/*[local-name()='Decimal']";
		String west = "*[local-name()='westBoundLongitude']/*[local-name()='Decimal']";
		String east = "*[local-name()='eastBoundLongitude']/*[local-name()='Decimal']";
		NodeList nodeList = (NodeList) xpath.compile(path).evaluate(doc, XPathConstants.NODESET);
		for (int i = 0; i < nodeList.getLength(); i++) {
			Node nod = nodeList.item(i);
			String norte = xpath.evaluate(north, nod);
			String sur = xpath.evaluate(south, nod);
			String oeste = xpath.evaluate(west, nod);
			String este = xpath.evaluate(east, nod);
			String wkt = "POLYGON ((" + oeste + " " + sur + "," + oeste + " " + norte + "," + este + " " + norte + ","
					+ este + " " + sur + "," + oeste + " " + sur + "))";
			res.addProperty(prop, wkt);
			res.addProperty(res.getModel().createProperty(prop.getURI() + "_alt"),
					"N:" + norte + "S:" + sur + "E:" + este + "O:" + oeste);
		}
	}

	/***************************************************************/
	/**
	 * Propiedades del tasklet
	 */
	public void setDestinationFile(String destinationFile) {
		this.destinationFile = destinationFile;
	}

	public void setDbname(String dbname) {
		this.dbname = dbname;
	}

	public void setDbuser(String dbuser) {
		this.dbuser = dbuser;
	}

	public void setDbpass(String dbpass) {
		this.dbpass = dbpass;
	}

	public void setDbhost(String dbhost) {
		this.dbhost = dbhost;
	}

	public void setDbport(String dbport) {
		this.dbport = dbport;
	}
}
