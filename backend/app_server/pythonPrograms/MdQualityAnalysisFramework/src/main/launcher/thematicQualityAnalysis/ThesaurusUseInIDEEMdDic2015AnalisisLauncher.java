package thematicQualityAnalysis;


import org.springframework.batch.core.launch.support.CommandLineJobRunner;

/**
 * Obtiene el uso de los tesauros en la colección de la idee de dic2015 100000 md
 */
public class ThesaurusUseInIDEEMdDic2015AnalisisLauncher {
	//trabajo de spring a ejecutar
	private static final String[] job = {
		"thematicQualityAnalysis/thesaurusUseInIDEEMdDic2015AnalysisJob.xml",
		"gemetThemeAnalisisJob"
	};
	/*****************************************************************/
	/**
	 * Obtiene el uso de los tesauros en la colección de la idee de dic2015 100000 md
	 */
	public static void main(String[] args) throws Exception{
		CommandLineJobRunner.main(job);
	}
}
