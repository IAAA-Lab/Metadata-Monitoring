package metadataValidation;

import org.springframework.batch.core.launch.support.CommandLineJobRunner;

/**
 * Landa el proceso de validacion d e emtadatos de postgres
 */
public class IDEEMdDic2015InspireValidationLauncher {

	// trabajo de spring a ejecutar
	private static final String[] job = { "metadataValidation/IDEEMdDic2015InspireValidationJob.xml", "metadataValidationJob" };

	/*****************************************************************/
	/**
	 * Lanzador del programa de enriquecimiento de las descripciones de
	 * servicios obtenidas en el crawler
	 */
	public static void main(String[] args) throws Exception {
		CommandLineJobRunner.main(job);
	}
}