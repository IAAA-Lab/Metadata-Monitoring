package metadataValidation;

import org.springframework.batch.core.launch.support.CommandLineJobRunner;

/**
 * Landa el proceso de validacion d e emtadatos de postgres
 */
public class IDEEMdSep2016XmlValidationLauncher {

	// trabajo de spring a ejecutar
	private static final String[] job = { "metadataValidation/IDEEMdSep2016XmlValidationJob.xml",
			"metadataValidationJob" };

	/*****************************************************************/
	/**
	 * Lanzador del programa de enriquecimiento de las descripciones de
	 * servicios obtenidas en el crawler
	 */
	public static void main(String[] args) throws Exception {
		CommandLineJobRunner.main(job);
	}
}
