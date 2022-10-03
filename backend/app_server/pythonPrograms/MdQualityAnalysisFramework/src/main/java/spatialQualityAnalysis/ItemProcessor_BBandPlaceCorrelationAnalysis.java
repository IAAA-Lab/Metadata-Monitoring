package spatialQualityAnalysis;

import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.List;
import java.util.Set;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.Property;
import org.apache.jena.rdf.model.RDFNode;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.rdf.model.Statement;
import org.geotools.geometry.jts.JTSFactoryFinder;
import org.springframework.batch.item.ItemProcessor;

import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.Polygon;
import com.vividsolutions.jts.io.WKTReader;

import rdfManager.MdQualityAnalysisRDFPropertyManager;
import rdfManager.RDFPropertyManager;
import spatialQualityAnalysis.util.ReverseGeocoder3;

/**
 * analiza la correlación entre nombres de lugar y bounding box
 */
public class ItemProcessor_BBandPlaceCorrelationAnalysis implements ItemProcessor<Model, Model> {

	// database connection
	private String dbname, dbuser, dbpass, dbhost, dbport;

	// geocoder inverso del tesauro de unidades administrativas
	private ReverseGeocoder3 revGeo = null;

	// lector de wkt
	private WKTReader reader = null;

	// almacena los pares nombre de lugar, conceptos del tesauro con ese nombre
	// los nombres de lugares se repiten en varios sitios
	HashMap<String, Set<String>> locationHash = null;

	// propiedades rdf usadas
	private final Property bbAnalysysResult = MdQualityAnalysisRDFPropertyManager.bbAnalysysResult;
	private final Property placeAnalysisResult = MdQualityAnalysisRDFPropertyManager.placeAnalysisResult;
	private final Property bbPlaceCorrelationAnalysisResult = MdQualityAnalysisRDFPropertyManager.bbPlaceCorrelationAnalysisResult;
	private final Property bbPlaceTextCorrelationAnalysisResult = MdQualityAnalysisRDFPropertyManager.bbPlaceTextCorrelationAnalysisResult;
	private final Property textPlacesFound = MdQualityAnalysisRDFPropertyManager.textPlacesFound;
	private final Property placeJdoUri = MdQualityAnalysisRDFPropertyManager.placeJdoUri;
	private final Property textPlaceKeywordProp = MdQualityAnalysisRDFPropertyManager.placeGateKeyword;

	/************************************************************/
	/**
	 * constructor. inicializamos la base de datos y la factoria de geometrias
	 */
	public ItemProcessor_BBandPlaceCorrelationAnalysis() {
		reader = new WKTReader(JTSFactoryFinder.getGeometryFactory(null));
	}

	/************************************************************/
	/**
	 * coge los recursos del modelo, y genera otro con la misa informaci�n pero
	 * cambiando las coordenadas a epsg 4326
	 */
	public Model process(Model item) throws Exception {

		// en el primer metadato inicializamos un reverse geocoder
		// esto se puede arreglar configurando un beforeProcees pero no recuerdo
		// como
		if (revGeo == null) {
			revGeo = new ReverseGeocoder3(dbname, dbuser, dbpass, dbhost, dbport);
		}

		// obtenemos el recurso del modelo (el unico) para validar la
		// correlacion poligono, nombre
		List<Statement> concept = item.listStatements(null, RDFPropertyManager.rdfTypeProp, (RDFNode) null).toList();
		Resource res = concept.get(0).getSubject();

		// si el recurso no tiene el bounding box correcto, lo marcamos y
		// dejamos de procesar
		String bbqa = res.getProperty(bbAnalysysResult).getString();
		if (!bbqa.equalsIgnoreCase("Correct")) {
			res.addProperty(bbPlaceCorrelationAnalysisResult, "NA");
			res.addProperty(bbPlaceTextCorrelationAnalysisResult, "NA");
			return item;
		}

		// obtenemos el bounding box original
		String bb = res.getProperty(MdQualityAnalysisRDFPropertyManager.boundingBox).getString();
		double[] bbcoords = getWKTCoordinates(bb);

		// obtenemos todas las localizaciones del JDO que interseccionan con el
		// bounding box
		List<String> locations = getAllAdministrativeDivisionFromBoundingBox(bbcoords);

		// Correlacion con JDO, ES MUY RESTRICTIVO, si no tiene todos los
		// nombres de lugar bien, dejamos de analizar la correlacion
		// solo se analiza la correlacion con las palabras clave de lugar
		String plaa = res.getProperty(placeAnalysisResult).getString();
		if (!(plaa.equalsIgnoreCase("Correct"))) {
			res.addProperty(bbPlaceCorrelationAnalysisResult, "NA");
		} else {
			// contamos los lugares del metadato que no estan dentro de los que
			// el geocoder inv dice que estan en el bb
			int invalidos = 0;
			List<Statement> locsSt = res.listProperties(placeJdoUri).toList();
			for (Statement st : locsSt) {
				String locationUri = st.getResource().getURI();
				locationUri = locationUri.replace("http://iaaa.cps.unizar.es/location/spainJurisdictionalDomain.owl#",
						"http://www.jurisdictionalDomain.org/spainJurisdictionalDomain.owl#");
				if (!locations.contains(locationUri)) {
					invalidos++;
				}
			}

			// si hay algun nombre de lugar en el metadato que no esta entre los
			// del geocoder dentro del bb, es incorrecto
			if (invalidos != 0) {
				res.addProperty(bbPlaceCorrelationAnalysisResult,
						"Incorrect: " + invalidos + " de " + locsSt.size() + " nombres no correlados con BB");
			} else {
				res.addProperty(bbPlaceCorrelationAnalysisResult, "Correct");
			}
		}

		// Correlacion con Geonames, ES POCO RESTRICTIVO.
		// analizamos los lugares sacados del texto con geonames (gate) a ver si alguno de los sitios está dentro del bounding box
		List<Statement> placesText = item.listStatements(null, textPlaceKeywordProp, (RDFNode) null).toList();
		//si no hay nombres de lugar de gate no se puede saber si hay correlacion
		if (placesText.size() == 0) {
			res.addProperty(bbPlaceTextCorrelationAnalysisResult, "Unknowkn");
		} else {
			
			//nos apuntamos todos los nombres de lugar del metadato en geonames, lo comprimimos en 1 solo campo
			String allFoundPlaces = "";
			for (Statement st : placesText) {
				allFoundPlaces += " % " + st.getString();
			}
			res.addProperty(textPlacesFound, allFoundPlaces);
			
			//buscamos a ver si al menos un nombre encontrado en geonames esta dentro del bounding box
			boolean suitablebb = false;
			for (Statement st : placesText) {
				String location[] = st.getString().split("\\|");
				double latitud = Double.parseDouble(location[1]);
				double longitud = Double.parseDouble(location[2]);
				if (contained(latitud, longitud, bbcoords)) {
					suitablebb = true;
				}
			}

			//si al menos un nombre de lugar del metadato alineado con geonames está dentro del bounding box
			//consideramos el metadato correcto
			if (suitablebb) {
				res.addProperty(bbPlaceTextCorrelationAnalysisResult, "Correct");
			} else {
				boolean bbinAreaOfText = false;
				//para algunas unidades administrativas representarlas con un punto puede hacer que caiga fuera de bb
				//aunque intersecciona, por ello se alinea cada nombre con la JDO para ver si ese nombre
				//está entre los que interseccionan con el BB
				for (Statement st : placesText) {
					String location[] = st.getString().split("\\|");
					String loc = location[0].toLowerCase().trim();
					Set<String> possibleLocs = locationHash.get(loc);
					if (possibleLocs != null) {
						for (String pl : possibleLocs) {
							String[] p = pl.split("\\#");
							pl = "http://www.jurisdictionalDomain.org/spainJurisdictionalDomain.owl#" + p[1];
							if (locations.contains(pl)) {
								bbinAreaOfText = true;
							}
						}
					}
				}

				//si alguno de los nombres alineado con el JDO intersecciona con el BB entonces se considera correcto
				if (bbinAreaOfText) {
					res.addProperty(bbPlaceTextCorrelationAnalysisResult, "Correct");
				} else {
					res.addProperty(bbPlaceTextCorrelationAnalysisResult, "Incorrect");
				}
			}
		}

		return item;
	}

	/********************************************************/
	/**
	 * dice si un punto está en un bounding box
	 */
	private boolean contained(double latitud, double longitud, double bbcoords[]) {
		if (longitud <= bbcoords[0] && longitud >= bbcoords[2] && latitud <= bbcoords[1] && latitud >= bbcoords[3]) {
			return true;
		}
		return false;
	}

	/*************************************************************************/
	/**
	 * Dado wkt genera un array con coordenadas mx, my, ix, iy,
	 */
	private double[] getWKTCoordinates(String boundBox) throws Exception {
		// eliminamos el srs que hay al principio
		Polygon pol = (Polygon) reader.read(boundBox);

		// obtenemos las coordenadas de las esquinas del bb
		double[] coords = new double[4];
		Coordinate[] polcoor = pol.getCoordinates();
		coords[0] = polcoor[2].x; coords[1] = polcoor[2].y;
		coords[2] = polcoor[0].x; coords[3] = polcoor[0].y;
		return coords;
	}

	/*************************************************************************/
	/**
	 * Obtenemos todas las unidades administrativas contenidas en un bounding
	 * box dado usando un reverse geocoder
	 */
	private List<String> getAllAdministrativeDivisionFromBoundingBox(double[] coords) {
		Hashtable<String, Double> locationNames = revGeo.getReverseGeocoder(coords[2], coords[3], coords[0], coords[1]);
		List<String> result = new ArrayList<String>();
		result.addAll(locationNames.keySet());
		return result;
	}

	/***************************************************************/
	/**
	 * Propiedades del tasklet
	 */
	public void setDbname(String dbname) {this.dbname = dbname;}
	public void setDbuser(String dbuser) {this.dbuser = dbuser;}
	public void setDbpass(String dbpass) {this.dbpass = dbpass;}
	public void setDbhost(String dbhost) {this.dbhost = dbhost;}
	public void setDbport(String dbport) {this.dbport = dbport;}

	// carga el fichero con pares nombre de lugar, conceptos de jdo con ese
	// nombre
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