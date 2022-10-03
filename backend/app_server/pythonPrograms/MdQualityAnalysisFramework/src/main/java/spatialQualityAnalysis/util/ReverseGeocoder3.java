package spatialQualityAnalysis.util;

import java.awt.geom.Rectangle2D;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Hashtable;

/**
 * @author Walter Renteria Agualimpia walra7@gmail.com IAAA-UNIZAR
 */

/*
 * //========== EXAMPLE TO CALL METHOD ===================== //import
 * processing.ReverseGeocoder3; //Hashtable<String, Float>
 * ToponymsReverseGeocoder = new Hashtable<String, Float>(); //String
 * argsIn[]=new String[11]; //ReverseGeocoder2 toponyms = new
 * ReverseGeocoder2(argsIn);
 * //ToponymsReverseGeocoder=toponyms.getReverseGeocoder_BBox4(xmin, ymin, xmax,
 * ymax);
 * //ToponymsReverseGeocoder=ReverseGeocoder3.getReverseGeocoder_BBox4(-0.963,
 * 41.629, -0.853, 41.715); //zaragoza municipio <GADM_Level_3>
 * //ToponymsReverseGeocoder=ReverseGeocoder3.getReverseGeocoder_BBox4(-2.181,
 * 40.984, 0.145, 42.407); //zaragoza provincia <GADM_Level_2>
 * //ToponymsReverseGeocoder=ReverseGeocoder3.getReverseGeocoder_BBox4(-2.031,
 * 40.285, 0.719, 42.713); //arag�n <GADM_Level_1>
 * //ToponymsReverseGeocoder=ReverseGeocoder3.getReverseGeocoder_BBox4(-18.40,
 * 27.60, 3.25, 43.09); //Espa�a <GADM_Level_0> //
 * //System.out.println(" <RESULTADOS>: ");
 * //System.out.println(ToponymsReverseGeocoder.entrySet());
 */


/**
 * A partir de unas coordenadas te da el nombre mas cercano, segun el contenido de la base de datos
 * que contiene el modelo de unidades administrativas
 */
public class ReverseGeocoder3 {
	private java.sql.Connection conn = null;
	Statement s = null;

	/**
	 * creamos la conexion a la base de datos
	 */
	public ReverseGeocoder3(String dbname, String dbuser, String dbpass, String dbhost, String dbport) {
		try {
			Class.forName("org.postgresql.Driver").newInstance();
			String url = "jdbc:postgresql://" + dbhost + ":" + dbport + "/" + dbname;
			conn = DriverManager.getConnection(url, dbuser, dbpass);
			((org.postgresql.PGConnection) conn).addDataType("geometry", Class.forName("org.postgis.PGgeometry"));
			((org.postgresql.PGConnection) conn).addDataType("box3d", Class.forName("org.postgis.PGbox3d"));
			s = conn.createStatement();
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	/**********************************************************************************/
	/**
	 * A partir de unas coordenadas te da el nombre mas cercano
	 */
	public Hashtable<String, Double> getReverseGeocoder(double xmin, double ymin, double xmax, double ymax) {
		Hashtable<String, Double> toponymsBase = new Hashtable<String, Double>();
		try {
			String uri = null;
			double pX1;
			double pY1;
			double pX2;
			double pY2;

			String polygonGeometry = "ST_GeomFromText('POLYGON ((" + xmin + " " + ymin + ", " + xmin + " " + ymax + ", "
					+ xmax + " " + ymax + ", " + xmax + " " + ymin + ", " + xmin + " " + ymin + "))', 4326)";
			String toponymsTable = "esp_all_admin_units3";
		
			String query = "SELECT uri, placename, txmin, tymin, txmax, tymax" + " FROM " + toponymsTable
					+ " WHERE ( area > 0.01*ST_Area(" + polygonGeometry + ") AND ST_Intersects(" + polygonGeometry
					+ " , the_geom) )";

			ResultSet r = s.executeQuery(query);
			while (r.next()) {
				uri = r.getString(1);
				pX1 = r.getDouble(3);
				pY1 = r.getDouble(4);
				pX2 = r.getDouble(5);
				pY2 = r.getDouble(6);

				Rectangle2D p = new Rectangle2D.Double(pX1, pY1, (pX2 - pX1), (pY2 - pY1));
				Rectangle2D q = new Rectangle2D.Double(xmin, ymin, (xmax - xmin), (ymax - ymin));

				double distanceHausdorff = HausdorffDistance.getHausdorffDistanceW(p, q);
				toponymsBase.put(uri, distanceHausdorff);
			}
			r.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return toponymsBase;
	}

}