package spatialQualityAnalysis;

import org.springframework.batch.core.launch.support.CommandLineJobRunner;

/**
 * identifica nombres de lugar de los metadatos usando el software de PERDIDO, es resultado es por pantalla
 * @deprecated
 */
public class LocationIdentificationWithPERDIDO {

	// trabajo de spring a ejecutar
	private static final String[] job = { "spatialQualityAnalysis/locationIdentificationWithPERDIDOJob.xml",
			"locationInTextIdentificationJob" };

	/*****************************************************************/
	/**
	 * Lanzador del programa de enriquecimiento de las descripciones de
	 * servicios obtenidas en el crawler
	 */
	public static void main(String[] args) throws Exception {
		CommandLineJobRunner.main(job);
	}
}
