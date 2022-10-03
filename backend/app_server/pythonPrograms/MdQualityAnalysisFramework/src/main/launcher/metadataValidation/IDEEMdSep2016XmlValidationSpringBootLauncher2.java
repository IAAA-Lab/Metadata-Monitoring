package metadataValidation;

import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.PropertySource;

/**
 * Lanza el proceso de validacion d e emtadatos de postgres definiendo el proceso con spring boot
 */
@SpringBootApplication
@EnableBatchProcessing
@PropertySource("classpath:metadataValidation/IDEEMdSep2016XmlValidationSpringBootLauncher2.properties")
public class IDEEMdSep2016XmlValidationSpringBootLauncher2 {
		
	/******************************************************************************************/
	/**
	 * Lanza el proceso de validacion d e emtadatos de postgres definiendo el proceso con spring boot
	 */
	public static void main(String[] args) throws Exception {
		System.exit(SpringApplication.exit(SpringApplication.run(IDEEMdSep2016XmlValidationSpringBootLauncher2.class, args)));
	}
}
