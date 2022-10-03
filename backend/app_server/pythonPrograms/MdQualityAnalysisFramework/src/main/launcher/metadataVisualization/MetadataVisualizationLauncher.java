package metadataVisualization;

import org.springframework.batch.core.launch.support.CommandLineJobRunner;

/**
 * visualiza los metadatos indicados en configuración de posgres en pantalla
 */
public class MetadataVisualizationLauncher {

	// trabajo de spring a ejecutar
	private static final String[] job = { "metadataVisualization/metadataVisualizationJob.xml",
			"metadataVisualizationJob" };

	/*****************************************************************/
	/**
	 * Lanzador del programa de enriquecimiento de las descripciones de
	 * servicios obtenidas en el crawler
	 */
	public static void main(String[] args) throws Exception {
		CommandLineJobRunner.main(job);
	}
}
