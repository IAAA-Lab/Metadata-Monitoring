package spatialQualityAnalysis;

import org.springframework.batch.core.launch.support.CommandLineJobRunner;

/**
 * realiza el analisis de las propiedades espaciales de los metadatos
 */
public class IDEEMdDic2015QualityReportGenLauncher {

	// trabajo de spring a ejecutar
	private static final String[] job = { "spatialQualityAnalysis/IDEEMdDic2015QualityReportGenJob.xml",
			"spatialQualityAnalysisJob" };

	/*****************************************************************/
	/**
	 * Lanzador del programa de enriquecimiento de las descripciones de
	 * servicios obtenidas en el crawler
	 */
	public static void main(String[] args) throws Exception {
		CommandLineJobRunner.main(job);
	}
}
