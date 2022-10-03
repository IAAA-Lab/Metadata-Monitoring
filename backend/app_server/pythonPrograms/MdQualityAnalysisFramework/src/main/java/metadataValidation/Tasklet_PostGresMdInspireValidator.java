package metadataValidation;

import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Resource;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;

import metadataValidation.tools.InspireValidatorClient;
import preprocessing.Tasklet_PostGresMdExtractor;
import preprocessing.util.Xpath_ISO_19115;
import rdfManager.JenaModelManager;
import rdfManager.MdQualityAnalysisRDFPropertyManager;

/**
 * Extrae los metadatos de una base de datos de postgres y los valida de acuerdo a inspire
 */
public class Tasklet_PostGresMdInspireValidator extends Tasklet_PostGresMdExtractor implements Tasklet {

	/************************************************************/
	/**
	 * Extrae los metadatos de una base de datos de postgres y los valida de acuerdo a inspire
	 */

	public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
		// creamos el modelo destino
		Model model = ModelFactory.createDefaultModel();

		// nos conectamos a la base de datos
		Class.forName("org.postgresql.Driver").newInstance();
		String url = "jdbc:postgresql://" + dbhost + ":" + dbport + "/" + dbname;
		Connection conn = DriverManager.getConnection(url, dbuser, dbpass);
		conn.setAutoCommit(false);

		URL inspireResourceTesterURL = new URL(
				"http://inspire-geoportal.ec.europa.eu/GeoportalProxyWebServices/resources/INSPIREResourceTester");
		InspireValidatorClient validator = new InspireValidatorClient(inspireResourceTesterURL);

		// lector de xml;
		DocumentBuilder builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();

		// obtenemos todos los metadatos
		Statement st = conn.createStatement();
		st.setFetchSize(50);
		ResultSet r = st.executeQuery("SELECT data from metadata");
		int i=0;
		while (r.next()) {
			i++;
			String md = new String(r.getString(1).getBytes(StandardCharsets.UTF_8));
			Resource res;
			if (md.contains(Xpath_ISO_19115.md)) {
				res = addResource(md, mdt, model, builder);
			} else {
				res = addResource(md, mds, model, builder);
			}
			String val = validator.getValidation(validator.validate(md));
			if (val != null) {
				res.addProperty(MdQualityAnalysisRDFPropertyManager.xmlValidationErrors, val);
			}
		}
		System.out.println(i);
		conn.close();
		
		//guarda el resultado de la validación
		model.setNsPrefix("qvoc", MdQualityAnalysisRDFPropertyManager.validationVocBaseUri);
		JenaModelManager.saveJenaModel(model, destinationFile);
		return RepeatStatus.FINISHED;
	}

}
