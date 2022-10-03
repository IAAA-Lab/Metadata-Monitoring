package spatialQualityAnalysis;

import java.util.List;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.Property;
import org.apache.jena.rdf.model.RDFNode;
import org.apache.jena.rdf.model.Statement;
import org.geotools.geometry.jts.JTSFactoryFinder;
import org.springframework.batch.item.ItemProcessor;

import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.Polygon;
import com.vividsolutions.jts.io.WKTReader;

import rdfManager.MdQualityAnalysisRDFPropertyManager;
import rdfManager.RDFPropertyManager;

/**
 * valida que el bounding box cumple todos los requisitos
 */
public class ItemProcessor_BoundingBoxAnalysis implements ItemProcessor<Model, Model> {

	// propiedades usadas
	private final Property bbAnalysysResult = MdQualityAnalysisRDFPropertyManager.bbAnalysysResult;
    
	//lector de WKT
	private WKTReader reader = null;

	/************************************************************/
	/**
	 * constructor. inicializamos la base de datos y la factoria de geometrias
	 */
	public ItemProcessor_BoundingBoxAnalysis() {
		reader = new WKTReader(JTSFactoryFinder.getGeometryFactory(null));
	}

	/************************************************************/
	/**
	 * coge los recursos del modelo, y genera otro con la misa informaci�n pero
	 * cambiando las coordenadas a epsg 4326
	 */
	public Model process(Model item) throws Exception {
		List<Statement> conc = item.listStatements(null, RDFPropertyManager.rdfTypeProp, (RDFNode) null).toList();
		List<Statement> it = conc.get(0).getSubject().listProperties(MdQualityAnalysisRDFPropertyManager.boundingBox)
				.toList();

		// comprobamos que solo hay un bounding box
		if (it.size() == 0) {
			conc.get(0).getSubject().addProperty(bbAnalysysResult, "Incorrect: No BB field");
			return item;
		} else if (it.size() > 1) {
			conc.get(0).getSubject().addProperty(bbAnalysysResult, "Incorrect: Multiple BB");
			return item;
		}

		// comprobamos que el bounding box tiene contenido
		double[] coords;
		try {
			coords = getWKTCoordinates(it.get(0).getString());
		} catch (Exception er) {
			conc.get(0).getSubject().addProperty(bbAnalysysResult, "Incorrect: Empty BB field");
			return item;
		}
		
		// comprobamos que el bounding box es un rectangulo valido
		double norte = coords[1]; double sur = coords[3];
		double oeste = coords[2]; double este = coords[0];
		if (norte <= sur || este <= oeste) {
			conc.get(0).getSubject().addProperty(bbAnalysysResult, "Incorrect: BB is not a valid rectangle");
			return item;
		} else if (norte > 90 || sur < -90 || oeste < -180 || este > 180) {
			conc.get(0).getSubject().addProperty(bbAnalysysResult, "Incorrect: BB is not in the value range +-180/90");
			return item;
		}

		// si ha pasado todos los test, el bounding box es sintacticamente valido
		it.get(0).getSubject().addProperty(bbAnalysysResult, "Correct");
		return item;
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
		coords[0] = polcoor[2].x; coords[1] = polcoor[2].y; coords[2] = polcoor[0].x; coords[3] = polcoor[0].y;
		return coords;
	}

}
