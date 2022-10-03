package reportGeneration;

import org.springframework.batch.core.launch.support.CommandLineJobRunner;

/**
 * Landa el proceso de extracciónd e emtadatos de postgres
 */
public class IDEEMdDic2015QualityReportGenLauncher {

	// trabajo de spring a ejecutar
	private static final String[] job = { "reportGeneration/IDEEMdDic2015QualityReportGenJob.xml",
			"qualityReportGenerationJob" };

	/*****************************************************************/
	/**
	 * Lanzador del programa de enriquecimiento de las descripciones de
	 * servicios obtenidas en el crawler
	 */
	public static void main(String[] args) throws Exception {
		CommandLineJobRunner.main(job);
	}
}
