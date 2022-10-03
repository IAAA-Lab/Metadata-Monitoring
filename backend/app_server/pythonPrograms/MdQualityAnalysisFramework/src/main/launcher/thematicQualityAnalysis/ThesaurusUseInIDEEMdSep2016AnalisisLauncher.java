package thematicQualityAnalysis;


import org.springframework.batch.core.launch.support.CommandLineJobRunner;

/**
 * Obtiene el uso de los tesauros en la colección de la idee de sep2016 4800 md
 */
public class ThesaurusUseInIDEEMdSep2016AnalisisLauncher {
	//trabajo de spring a ejecutar
	private static final String[] job = {
		"thematicQualityAnalysis/thesaurusUseInIDEEMdSep2016AnalysisJob.xml",
		"thesaurusUseAnalisisJob"
	};
	/*****************************************************************/
	/**
	 * Obtiene el uso de los tesauros en la colección de la idee de sep2016 4800 md
	 */
	public static void main(String[] args) throws Exception{
		CommandLineJobRunner.main(job);
	}
}
