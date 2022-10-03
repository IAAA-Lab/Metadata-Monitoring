package spatialQualityAnalysis;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.rdf.model.Statement;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;

import rdfManager.JenaModelManager;
import rdfManager.MdQualityAnalysisRDFPropertyManager;

/****************************************************************/
/**
 * Utiliza el servicio de PERDIDO para identificar nobres de lugar en un metadato
 * El resultado lo muestra por pantalla
 * @deprecated
 */
public class Tasklet_LocationIdentificationWithPERDIDO implements Tasklet {

	// fichero fuente y destino
	private String sourceFile;
	
	/****************************************************************/
	/**
	 * Utiliza el servicio de PERDIDO para identificar nobres de lugar en un metadato
	 * El resultado lo muestra por pantalla
	 */
	public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
		Model model = JenaModelManager.loadJenaModel(sourceFile);

		for (Resource res : model.listSubjects().toList()) {
			if (!res.hasProperty(MdQualityAnalysisRDFPropertyManager.placeText)) {
				String title = "", altTitle = "", astract = "", key = "";
				if (res.hasProperty(MdQualityAnalysisRDFPropertyManager.title)) {
					title = res.getProperty(MdQualityAnalysisRDFPropertyManager.title).getString();
				}
				if (res.hasProperty(MdQualityAnalysisRDFPropertyManager.alttitle)) {
					altTitle = res.getProperty(MdQualityAnalysisRDFPropertyManager.title).getString();
				}
				if (res.hasProperty(MdQualityAnalysisRDFPropertyManager.astract)) {
					astract = res.getProperty(MdQualityAnalysisRDFPropertyManager.title).getString();
				}
				for (Statement st : res.listProperties(MdQualityAnalysisRDFPropertyManager.placeKeyword).toList()) {
					key = key + ". " + st.getString();
				}
				String toVerify= title+". "+altTitle+". "+astract+". "+key;		
				String verified = getToponyms(toVerify.replaceAll("\"", " "));
				System.out.println("RES: " + verified);
			}
		}

		return RepeatStatus.FINISHED;
	}

	private static final String USER_AGENT = "Mozilla/5.0";

	/****************************************************************/
	/**
	 * Utiliza el servicio de PERDIDO para identificar nobres de lugar en un texto
	 */
	public static String getToponyms(String text) {
		String response = "";
		try {
			
			String thetext = text.replaceAll(" ", "%20");
			System.out.println("\nSending 'GET' request to URL : " + thetext);
			
			URL url = new URL(
					"http://erig.univ-pau.fr/PERDIDO/api/toponyms/xml/?lang=Spanish&api_key=demo&content=" + thetext);

			HttpURLConnection con = (HttpURLConnection) url.openConnection();

			// optional default is GET
			con.setRequestMethod("GET");

			// add request header
			con.setRequestProperty("User-Agent", USER_AGENT);

			int responseCode = con.getResponseCode();
			System.out.println("\nSending 'GET' request to URL : " + url);
			System.out.println("Response Code : " + responseCode);

			BufferedReader ina = new BufferedReader(new InputStreamReader(con.getInputStream()));
			String inputLine;
			StringBuffer responser = new StringBuffer();

			while ((inputLine = ina.readLine()) != null) {
				responser.append(inputLine);
			}
			ina.close();

			// print result
			System.out.println(responser.toString());

		} catch (IOException e) {
			e.printStackTrace();
		}
		return response;
	}

	/***************************************************************/
	/**
	 * Propiedades del tasklet
	 */

	public void setSourceFile(String sourceFile) {
		this.sourceFile = sourceFile;
	}

}
