package spatialQualityAnalysis;

import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Set;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.Property;
import org.apache.jena.rdf.model.RDFNode;
import org.apache.jena.rdf.model.Statement;
import org.springframework.batch.item.ItemProcessor;

import rdfManager.MdQualityAnalysisRDFPropertyManager;
import rdfManager.RDFPropertyManager;

/**
 * analiza la calidad de las palabras clave de lugar, mira si existen o no
 * en caso de que existan mira a ver si estan en el tesauro de unidades administrativas (o el que se le pase por configuracion)
 * de momento no usa la salida del paso 3 (el gazetter de geonames), pero en el futuro debería usar tambien el gazetter para ampliar las etiquetas de lugar que reconoce -->				
 */
public class ItemProcessor_PlaceKeywordAnalysis implements ItemProcessor<Model, Model> {

	// propiedades usadas
	private final Property placeAnalysisResult = MdQualityAnalysisRDFPropertyManager.placeAnalysisResult;
	private final Property placeKeywordProp = MdQualityAnalysisRDFPropertyManager.placeKeyword;
	private final Property placeJdoUri = MdQualityAnalysisRDFPropertyManager.placeJdoUri;

	//almacena los pares nombre de lugar, conceptos del tesauro con ese nombre 
	//los nombres de lugares se repiten en varios sitios
	private HashMap<String, Set<String>> locationHash = null;

	/************************************************************/
	/**
	 * coge los recursos del modelo, y genera otro con la misa informaci�n pero
	 * cambiando las coordenadas a epsg 4326
	 */
	public Model process(Model item) throws Exception {
		//obtenemos el unico recurso del modelo
		List<Statement> conc = item.listStatements(null, RDFPropertyManager.rdfTypeProp, (RDFNode) null).toList();
		
		// miramos si el recurso tiene nombres de lugar en las palabras clave del metadato (las originales)
		// si no tiene indicamos que no tiene ninguna palabra clave de lugar explicita
		List<Statement> places = item.listStatements(null, placeKeywordProp, (RDFNode) null).toList();
		if (places.size() == 0) {
			conc.get(0).getSubject().addProperty(placeAnalysisResult, "Incorrect: No place names");
			return item;
		}

		//aquellos nombres de lugar encontrados en el campo de palabras clave los buscamos en el tesauro
		//si no los encuentra, nos apuntamos que no son validos, si los encuentra apuntamos todas sus uris
		int invalidos = 0;
		List<String> locationUris = new ArrayList<String>();
		for (Statement st : places) {
			String place = st.getString().toLowerCase();
			if (!locationHash.containsKey(place)) {
				invalidos++;
			} else {
				locationUris.addAll(locationHash.get(place));
			}
		}

		// si todos los nombres son validos, marcamos la entrada como correcta (y guardamos la equivalencia)
		// si no, ponemos la proporcion
		if (invalidos != 0) {
			conc.get(0).getSubject().addProperty(placeAnalysisResult,
					"Incorrect: " + invalidos + " de " + places.size() + " nombres incorrectos");
		} else {
			conc.get(0).getSubject().addProperty(placeAnalysisResult, "Correct");
			for (String locU : locationUris) {
				conc.get(0).getSubject().addProperty(placeJdoUri, item.createResource(locU));
			}
		}

		return item;
	}

	/*************************************************************************/
	// parametros del tasklet
	//carga el fichero con pares nombre de lugar, conceptos de jdo con ese nombre
	public void setLocationSourceHashFile(String locationHashfile) {
		try {
			ObjectInputStream oos = new ObjectInputStream(new FileInputStream(locationHashfile));
			@SuppressWarnings("unchecked")
			HashMap<String, Set<String>> hash = (HashMap<String, Set<String>>) oos.readObject();
			oos.close();
			this.locationHash = hash;
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}
}
