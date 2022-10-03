package metadataValidation;

import javax.annotation.Resource;
import javax.sql.DataSource;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.configuration.annotation.JobBuilderFactory;
import org.springframework.batch.core.configuration.annotation.StepBuilderFactory;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

/**
 * Define el proceso de validacion de metadatos de postgres definiendo el proceso con spring boot
 */
@Configuration
public class IDEEMdSep2016XmlValidationSpringBoot {
		
	//configuracion del entorno del trabajo
	@Autowired private JobBuilderFactory jobs;
	@Autowired private StepBuilderFactory steps;
	@Resource private Environment env;
	
	/******************************************************************************************/
	/**
	 * configuracion del trabajo de validacion d e emtadatos de postgres definiendo el proceso con spring boot
	 */
	@Bean public Job metadataValidationJob() throws Exception {
		return this.jobs.get("metadataValidationJob_"+System.currentTimeMillis()).start(metadataValidationFromPostGresStep()).build();
	}

	@Bean protected Step metadataValidationFromPostGresStep() throws Exception {
		return this.steps.get("metadataValidationFromPostGresStep").tasklet(prostGresMdXmlValidatorTasklet()).build();
	}
	
	@Bean public Tasklet prostGresMdXmlValidatorTasklet(){
		Tasklet_PostGresMdXmlValidator tpmv = new Tasklet_PostGresMdXmlValidator();
		tpmv.setJdbcConnection(dataSourceJdbc);
		return tpmv;
	} ;
	
	/******************************************************************************************/
	/**
	 * definimos la conexion a la base de datos
	 */
	@Autowired private JdbcTemplate dataSourceJdbc;
	@Bean public DataSource dataSource() {						
	    DriverManagerDataSource dataSource = new DriverManagerDataSource();	  	    
	    dataSource.setDriverClassName(env.getProperty("database.driverClassName"));	   
	    dataSource.setUrl(env.getProperty("database.url"));
	    dataSource.setUsername(env.getProperty("database.username"));
	    dataSource.setPassword(env.getProperty("database.password"));
	    return dataSource;
	}
	
	/******************************************************************************************/
	/**
	 * Lanza el proceso de validacion d e emtadatos de postgres definiendo el proceso con spring boot
	 */
	public static void main(String[] args) throws Exception {
		System.exit(SpringApplication.exit(SpringApplication.run(IDEEMdSep2016XmlValidationSpringBoot.class, args)));
	}
}
