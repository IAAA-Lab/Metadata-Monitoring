package spatialQualityAnalysis;

import java.io.File;
import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.rdf.model.Statement;
import org.springframework.batch.item.ItemProcessor;

import gate.AnnotationSet;
import gate.Corpus;
import gate.Document;
import gate.Factory;
import gate.Gate;
import gate.creole.ANNIEConstants;
import gate.creole.SerialAnalyserController;
import gate.util.persistence.PersistenceManager;
import rdfManager.MdQualityAnalysisRDFPropertyManager;

/**
 * Identifica nombres de lugar de españa (geonames)
 */
public class ItemProcessor_PlaceTextDetection implements ItemProcessor<Model, Model> {

	// analizadores y corpus de gate usados (solo 1 corpus) 1 si no ocupa mucha memoria
	private SerialAnalyserController annieController;
	private Corpus corpus = null;
	
	// listado de nombres sacados de geonames con sus coordenadas
	HashMap<String, List<List<Double>>> geonamesNameCoordMap = new HashMap<String, List<List<Double>>>();

	/**
	 * Identifica nombres de lugar de españa (geonames)
	 */
	public Model process(Model item) throws Exception {
		//obtenemos el único recurso del modelo que describe un metadato
		Resource res = item.listSubjects().toList().get(0);
		
		//obtiene todo el texto que puede contener información de lugar y lo procesa con gate (annie)
		Document taggedDoc = Factory.newDocument(new String(getLocationText(res)));
		corpus.add(taggedDoc); annieController.setCorpus(corpus); annieController.execute();

		//obtiene todos los lugares del texto que estan en el gazeter de lugar (geonames)
		Set<String> places = getTermsInGazetter(taggedDoc, "places");

		//si tenemos en el map alguna coordenada para ese nombre las guardamos en el modelo
		//puede haber multiples coordenadas para un nombre ya que hay lugares con el mismo nombre
		for (String place : places) {
			List<List<Double>> c = geonamesNameCoordMap.get(place);
			if (c == null) {continue;}
			for (List<Double> coord : c) {
				String placet = place + "|" + coord.get(0) + "|" + coord.get(1);
				res.addProperty(MdQualityAnalysisRDFPropertyManager.placeGateKeyword, placet);
			}
		}

		//limpiamos las estructuras de gate
		corpus.clear(); annieController.cleanup(); Factory.deleteResource(taggedDoc);
		return item;
	}

	/**************************************************************************/
	/**
	 * obtiene en un metadato todo el texto que puede contener localizaciones de lugar
	 * es decir titulos, resumen y palabras clave de lugar
	 */
	private String getLocationText(Resource res) {
		String title = "", altTitle = "", astract = "", key = "";
		if (res.hasProperty(MdQualityAnalysisRDFPropertyManager.title)) {
			title = res.getProperty(MdQualityAnalysisRDFPropertyManager.title).getString();
		}
		if (res.hasProperty(MdQualityAnalysisRDFPropertyManager.alttitle)) {
			altTitle = res.getProperty(MdQualityAnalysisRDFPropertyManager.alttitle).getString();
		}
		if (res.hasProperty(MdQualityAnalysisRDFPropertyManager.astract)) {
			astract = res.getProperty(MdQualityAnalysisRDFPropertyManager.astract).getString();
		}
		for (Statement st : res.listProperties(MdQualityAnalysisRDFPropertyManager.placeKeyword).toList()) {
			key = key + ". " + st.getString();
		}
		String toVerify = title + ". " + altTitle + ". " + astract + ". " + key;
		// String toVerify= title;
		toVerify = toVerify.replaceAll("\"", " ");
		return toVerify;
	}

	/**********************************************************************************/
	/**********************************************************************************/
	/**
	 * obtiene los terminos contenidos en un gazetter de cierto tipo que ocurren en el texto
	 */
	private Set<String> getTermsInGazetter(Document processedDocument, String selGazetter) throws Exception {
		// obtenemos las anotaciones del tipo gazeter y mayorTye el que nos
		// interesa
		AnnotationSet annotsOfGazetter = processedDocument.getAnnotations().get("Lookup");
		Set<String> propVal = new HashSet<String>();
		for (gate.Annotation annotation : annotsOfGazetter) {
			if (annotation.getFeatures().get("majorType").equals(selGazetter)) {
				propVal.add(processedDocument.getContent()
						.getContent(annotation.getStartNode().getOffset(), annotation.getEndNode().getOffset())
						.toString());
			}
		}
		return propVal;
	}

	/*************************************************************************/
	// parametros del tasklet
	@SuppressWarnings("unchecked")
	public void setLocationHashFile(String locationHashFile) throws Exception {
		FileInputStream fin = new FileInputStream(locationHashFile);
		ObjectInputStream ois = new ObjectInputStream(fin);
		geonamesNameCoordMap = (HashMap<String, List<List<Double>>>) ois.readObject();
		ois.close();
		loadKnowledgeModels();
	}

	public void loadKnowledgeModels() throws Exception {
		// inicializamos gate al cargar la classe
		if (!Gate.isInitialised()) {
			Gate.setGateHome(new File("."));
			Gate.setUserConfigFile(new File("gate.xml"));
			Gate.setUserSessionFile(new File("gate.sesion"));
			Gate.init();
		}
		// cargamos annie para encontrar las localizaciones
		annieController = (SerialAnalyserController) PersistenceManager.loadObjectFromFile(
				new File(new File(Gate.getPluginsHome(), ANNIEConstants.PLUGIN_DIR), "ANNIE_gazetteer.gapp"));
		corpus = Factory.newCorpus("Location finder");
		annieController.setCorpus(corpus);
	}
}
