package preprocessing;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.ObjectOutputStream;
import java.io.PrintStream;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;

/**
 * Procesa el un fichero de geonames (ej: españa) para generar un gazeter de gate en base a los nombres
 * y un mpa de nombre - coordenadas
 */
public class Tasklet_GeonamesToGateGazetteer implements Tasklet {

	// fichero fuente y destino
	private String sourceFile;
	private String destinationFile;
	private String destinationHash;

	/************************************************************/
	/**
	 * * Procesa el un fichero de geonames (ej: españa) para generar un gazeter de gate en base a los nombres
     * y un mpa de nombre - coordenadas
	 */

	public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
		HashMap<String, List<List<Double>>> map = new HashMap<String, List<List<Double>>>();

		try {
			InputStream fis = new FileInputStream(sourceFile);
			InputStreamReader isr = new InputStreamReader(fis, Charset.forName("UTF-8"));
			BufferedReader br = new BufferedReader(isr);
			PrintStream ps = new PrintStream(destinationFile);
			ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(destinationHash));
			String line;
			List<String> placeList = new ArrayList<String>();
			while ((line = br.readLine()) != null) {
				String[] parts = line.split("\t");
				double latitud = 999, longitud = 999;
				String base = parts[1];
				for (int i = 2; i < parts.length; i = i + 1) {
					if (parts[i].length() > 0 && Character.isDigit(parts[i].charAt(0))
							&& Character.isDigit(parts[i].charAt(parts[i].length() - 1))) {
						latitud = Double.parseDouble(parts[i]);
						longitud = Double.parseDouble(parts[i + 1]);
						break;
					}
				}

				base = correct(base);

				List<Double> coord = new ArrayList<Double>();
				coord.add(latitud);
				coord.add(longitud);
				if (map.containsKey(base)) {
					map.get(base).add(coord);
				} else {
					map.put(base, new ArrayList<List<Double>>());
					map.get(base).add(coord);
				}
				if (!placeList.contains(base)) {
					placeList.add(base);
				}

			}

			Collections.sort(placeList);
			for (String base : placeList) {
				ps.println(base);
			}

			oos.writeObject(map);
			oos.close();
			ps.close();
			isr.close();
		} catch (Exception er) {
			er.printStackTrace();
		}

		return RepeatStatus.FINISHED;
	}

	private String correct(String base) {
		base = base.replaceAll(":*", "");
		return base;
	}

	/***************************************************************/
	/**
	 * Propiedades del tasklet
	 */
	public void setDestinationFile(String destinationFile) {
		this.destinationFile = destinationFile;
	}

	public void setDestinationHash(String destinationHash) {
		this.destinationHash = destinationHash;
	}

	public void setSourceFile(String sourceFile) {
		this.sourceFile = sourceFile;
	}
}
