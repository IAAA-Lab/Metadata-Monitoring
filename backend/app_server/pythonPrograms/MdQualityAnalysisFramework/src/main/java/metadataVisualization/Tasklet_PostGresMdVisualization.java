package metadataVisualization;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.List;

import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;

/**
 * Muestra un conjunto de metadatos de la base de datos.
 *
 */
public class Tasklet_PostGresMdVisualization implements Tasklet {

	// database connection
	private String dbname, dbuser, dbpass, dbhost, dbport;

	// metadatos a visualizar
	private List<String> metadataIds;

	/************************************************************/
	/**
	 * muestra por pantalla los metadatos indicados en la configuracion
	 */
	public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
		// nos conectamos a la base de datos
		Class.forName("org.postgresql.Driver").newInstance();
		String url = "jdbc:postgresql://" + dbhost + ":" + dbport + "/" + dbname;
		Connection conn = DriverManager.getConnection(url, dbuser, dbpass);
		conn.setAutoCommit(false);

		// hacemos la consulta

		Statement st = conn.createStatement();
		st.setFetchSize(50);
		for (String id : metadataIds) {
			ResultSet r = st.executeQuery("SELECT data from metadata where data LIKE '%" + id + "%'");
			while (r.next()) {
				System.out.println(r.getString(1));
			}
			System.out.println("----------------------------------------------");
		}
		conn.close();

		return RepeatStatus.FINISHED;
	}

	/***************************************************************/
	/**
	 * Propiedades del tasklet
	 */
	public void setDbname(String dbname) {
		this.dbname = dbname;
	}

	public void setDbuser(String dbuser) {
		this.dbuser = dbuser;
	}

	public void setDbpass(String dbpass) {
		this.dbpass = dbpass;
	}

	public void setDbhost(String dbhost) {
		this.dbhost = dbhost;
	}

	public void setDbport(String dbport) {
		this.dbport = dbport;
	}

	public void setIdOfmetadataToVisualize(List<String> metadataIds) {
		this.metadataIds = metadataIds;
	}

}
