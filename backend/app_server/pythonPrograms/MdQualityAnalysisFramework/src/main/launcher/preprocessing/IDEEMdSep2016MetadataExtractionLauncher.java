package preprocessing;

import org.springframework.batch.core.launch.support.CommandLineJobRunner;

/**
 * Landa el proceso de extracciónd e emtadatos de postgres
 */
public class IDEEMdSep2016MetadataExtractionLauncher {

	// trabajo de spring a ejecutar
	private static final String[] job = { "preprocessing/IDEEMdSep2016MetadataExtractionJob.xml",
			"metadataExtractionJob" };

	/*****************************************************************/
	/**
	 * Lanzador del programa de enriquecimiento de las descripciones de
	 * servicios obtenidas en el crawler
	 */
	public static void main(String[] args) throws Exception {
		CommandLineJobRunner.main(job);
	}
}