package metadataValidation;

import java.io.File; // if you use File
import java.io.StringReader;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.List;

import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;

import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

import preprocessing.util.Xpath_ISO_19115;

/**
 * valida un conjunto de XMLs
 */
public class Tasklet_PostGresMdXmlValidator implements Tasklet {

	//conexion a la base de datos
	private JdbcTemplate jdbcConnection;
	private String schemaFile;

	public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
		// contruimos el validador de xml
		URL schemaFil = new File(schemaFile).toURI().toURL();
		SchemaFactory schemaFactory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
		
		// configuramoe el validador para capturar todas las excepciones
		Validator validator = schemaFactory.newSchema(schemaFil).newValidator();
		final List<SAXParseException> exceptions = new LinkedList<SAXParseException>();
		validator.setErrorHandler(new ErrorHandler() {
			@Override
			public void warning(SAXParseException exception) throws SAXException {exceptions.add(exception);}
			@Override
			public void fatalError(SAXParseException exception) throws SAXException {exceptions.add(exception);}
			@Override
			public void error(SAXParseException exception) throws SAXException {exceptions.add(exception);}
		});

		//medidas queremos recopilar
		int incorrectMdData = 0, incorrectMdService = 0;
		int conceptualConsistencyErrData = 0, conceptualConsistencyErrServ = 0;
		int completenesOmissionErrData = 0, completenesOmissionErrServ = 0;
		int domainConsistencyErrData = 0, domainConsistencyErrServ = 0;
		int completenessCommisionErrData = 0, completenessCommisionErrServ = 0;
		int datmd=0, svmd=0;
		// obtenemos todos los metadatos y los validamos y tomamos las medidas
		String SQL = "SELECT data from metadata";
		List<String> metadataList = jdbcConnection.query(SQL, new MetadataMapper());
		for (String md : metadataList) {
			validator.validate(new StreamSource(new StringReader(md)));
			int incorredmd = 0, conceptualConsistencyErr = 0, completenesOmissionErr = 0, domainConsistencyErr = 0,
					completenessCommisionErr = 0;
			for (SAXParseException s : exceptions) {
				if (s.toString().contains("There are multiple occurrences")) {
					incorredmd = 1;
					completenessCommisionErr = 1;
				} else if (s.toString().contains("is not complete.")
						|| s.toString().contains("must appear on element")) {
					incorredmd = 1;
					completenesOmissionErr = 1;
				} else if (s.toString().contains("Invalid content was found")
						|| s.toString().contains(
								"must have no character or element information item [children], because the type's")
						|| s.toString().contains("is a simple type, so it cannot have attributes")
						|| s.toString().contains("is not allowed to appear in element")
						|| s.toString().contains("cannot have character [children], because the type's content type")
						|| s.toString().contains("it must have no element information item")) {
					incorredmd = 1;
					conceptualConsistencyErr = 1;
				} else if ((s.toString().contains("The value") && s.toString().contains("of element")
						&& s.toString().contains("is not valid")) || s.toString().contains("is not a valid value")
						|| s.toString().contains("is not facet-valid")
						|| s.toString().contains("the value must be valid")
						|| s.toString().contains("is not valid with respect to its type")) {
					incorredmd = 1;
					domainConsistencyErr = 1;
				} else {
					System.out.println(s);
				}
			}

			if (md.contains(Xpath_ISO_19115.md)) {
				incorrectMdData += incorredmd; datmd++; 
				completenessCommisionErrData += completenessCommisionErr;
				completenesOmissionErrData += completenesOmissionErr;
				conceptualConsistencyErrData += conceptualConsistencyErr;
				domainConsistencyErrData += domainConsistencyErr;
			} else {
				incorrectMdService += incorredmd; svmd++;
				completenessCommisionErrServ += completenessCommisionErr;
				completenesOmissionErrServ += completenesOmissionErr;
				conceptualConsistencyErrServ += conceptualConsistencyErr;
				domainConsistencyErrServ += domainConsistencyErr;
			}

			exceptions.clear();
		}

		System.out.println("-------------------------");
		System.out.println("Data metadata" + datmd);
		System.out.println("incorrectMdData=" + incorrectMdData);
		System.out.println("completenessCommisionErrData=" + completenessCommisionErrData);
		System.out.println("completenesOmissionErrData=" + completenesOmissionErrData);
		System.out.println("conceptualConsistencyErrData=" + conceptualConsistencyErrData);
		System.out.println("domainConsistencyErrData=" + domainConsistencyErrData);

		System.out.println("-------------------------");
		System.out.println("Service metadata" + svmd);
		System.out.println("incorrectMdService=" + incorrectMdService);
		System.out.println("completenessCommisionErrServ=" + completenessCommisionErrServ);
		System.out.println("completenesOmissionErrServ=" + completenesOmissionErrServ);
		System.out.println("conceptualConsistencyErrServ=" + conceptualConsistencyErrServ);
		System.out.println("domainConsistencyErrServ=" + domainConsistencyErrServ);

		System.out.println("-------------------------");

		return RepeatStatus.FINISHED;
	}

	/*************************************************************************************/
	/**
	 * Clase que modela el resultado de la consulta SQL
	 */
	public class MetadataMapper implements RowMapper<String> {
		public String mapRow(ResultSet rs, int rowNum) throws SQLException {
			return new String(rs.getString(1).getBytes(StandardCharsets.UTF_8));
		}
	}

	/***************************************************************/
	/**
	 * Propiedades del tasklet
	 */
	public void setJdbcConnection(JdbcTemplate jdbcConnection) {	
		this.jdbcConnection = jdbcConnection;
	}

	public void setSchemaFile(String schemaFile) {
		this.schemaFile = schemaFile;
	}
	
	
	
}
