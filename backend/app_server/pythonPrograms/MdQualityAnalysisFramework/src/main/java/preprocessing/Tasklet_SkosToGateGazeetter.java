package preprocessing;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.ObjectOutputStream;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.Property;
import org.apache.jena.rdf.model.RDFNode;
import org.apache.jena.rdf.model.Statement;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;

import rdfManager.JenaModelManager;
import rdfManager.RDFPropertyManager;
import textManager.TextFileManager;

/**
 * Procesa un rdf para extraer sus etiquetas y generalas en formato de gate
 */
public class Tasklet_SkosToGateGazeetter implements Tasklet {
	// propiedades de rdf usadas
	private static final Property skosPrefLabelProp = RDFPropertyManager.skosPrefLabelProp;
	private static final Property skosAltLabelProp = RDFPropertyManager.skosAltLabelProp;

	// parametros que necesita el tasklet
	private String rdfSource; //tesauro de lugar
	private String destFile, destHashFile = null; //se guarda el gazetter y un hash label-uris
	private Set<String> termExceptions = null; //excepciones de nombres que no deben ir en el gazetter
	private List<String> langsToProcess = null; //idiomas a procesar, cero implica todo lo que haya
	private boolean quitarPlurales = false; //indicamos si se quitan plurales

	/************************************************************************/
	/**
	 * Procesa un rdf para extraer sus etiquetas y generalas en formato de gate
	 */
	public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
		extractLabelsFromSKOS(rdfSource, destFile, langsToProcess);
		return RepeatStatus.FINISHED;
	}

	/************************************************************************************/
	/**
	 * coje un fichero de skos, y genera un fichero de texto con todas sus
	 * prefLabels /altLabels en el conjunto de idiomas deseado el formato de
	 * salida es un elemento por fila (usado en gate) ordenado alfabeticamente
	 * si no se le pasan idiomas, es todos.
	 */

	public void extractLabelsFromSKOS(String sourceSKOS, String destFile, List<String> langs) throws Exception {
		// obtenemos todas las etiquetas preferidas y alternativas del tesauro
		//los nombres se repiten, puede haber una etiqueta en muchos conceptos
		//guardamos pares etiqueta-lista de uris
		Set<String> labels = new HashSet<String>();
		HashMap<String, Set<String>> labelUris = new HashMap<String, Set<String>>();
		Model skosModel = JenaModelManager.loadJenaModel(sourceSKOS);
		labels.addAll(getLabelsFromProperty(skosPrefLabelProp, langs, skosModel, labelUris));
		labels.addAll(getLabelsFromProperty(skosAltLabelProp, langs, skosModel, labelUris));

		// ordenamos la lista de etiquetas por orden alfabetico
		List<String> result = new ArrayList<String>(labels);
		Collections.sort(result);

		// guardamos la lista en el destino en formato para GATE (1 elemento por
		// fila)
		TextFileManager.saveTextFile(destFile, result);

		// guardamos el hashmap con los pares etiqueta reursos que la contienen
		//los nombres se repiten, puede haber una etiqueta en muchos conceptos
		if (destHashFile != null) {
			File destHF = new File(destHashFile);
			destHF.getParentFile().mkdirs();
			ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(destHF));
			oos.writeObject(labelUris);
			oos.close();
		}
	}

	/*********************************************************************************/
	/**
	 * devuelve las etiquetas en un conjunto de idiomas de una propiedad dada
	 * del modelo si no hay idiomas devuelve todos
	 */
	private Set<String> getLabelsFromProperty(Property prop, List<String> langs, Model skosModel,
			HashMap<String, Set<String>> labelUris) {
		Set<String> labels = new HashSet<String>();

		// generamos las etiquetas del tesauro en gate en multiples variantes
		// (acentos, mayusculas)
		for (Statement node : skosModel.listStatements(null, prop, (RDFNode) null).toList()) {
			if (langs == null || langs.size() == 0 || langs.contains(node.getLanguage())) {
				// a�adimos versiones de las etiquetas con y sin acentos
				String label = node.getString();
				labels.addAll(getLabelsFromProperty(label, node.getSubject().getURI(), labelUris));
				label = correctLabels(label);
				labels.addAll(getLabelsFromProperty(label, node.getSubject().getURI(), labelUris));
			}
		}

		// borramos plurales
		if (quitarPlurales) {
			Set<String> labels2 = new HashSet<String>();
			for (String label : labels) {
				labels2.add(label);
				if (label.endsWith("es")) {
					String label2 = label.substring(0, label.length() - 2);
					labels2.add(label2);
					labelUris.put(label2, labelUris.get(label));

				}
				if (label.endsWith("s")) {
					String label2 = label.substring(0, label.length() - 1);
					labels2.add(label2);
					labelUris.put(label2, labelUris.get(label));
				}
			}
			labels = labels2;
		}

		// borramos exceptiones de variaciones conflictivos con palabras comunes
		// (e.g., plan);
		if (termExceptions != null) {
			Set<String> labels2 = new HashSet<String>();
			for (String label : labels) {
				if (!termExceptions.contains(label)) {
					labels2.add(label);
				}
			}
			labels = labels2;
		}

		return labels;
	}

	/**
	 * generamos versiones de una etiqueta como soluciones, en minusculas, sin
	 * parentesis, y partida adem�s si se indica que quite plurales los quita
	 */
	private Set<String> getLabelsFromProperty(String slabel, String URI, HashMap<String, Set<String>> labelUris) {
		Set<String> labels = new HashSet<String>();
		// pasamos a minusculas
		String label = slabel.toLowerCase();
		labels.add(label);
		addLabelUriPairToLabelUrisHash(label, URI, labelUris);

		// si tiene parentesis y demas cosas, generamos una version simplificada
		label = replacePattern(label, "(\\(|\\-|\")[a-zA-Z ]+(\\)|\\-|\")", "").replaceAll(" +", " ");
		labels.add(label);
		addLabelUriPairToLabelUrisHash(label, URI, labelUris);

		// si tiene / lo separamos y a�adimos cada parte por separado
		if (label.contains("/")) {
			String[] partes = label.split("/");
			for (String parte : partes) {
				labels.add(parte);
				addLabelUriPairToLabelUrisHash(parte, URI, labelUris);
			}
		}
		return labels;
	}

	/***********************************************************************************/
	/**
	 * a�ade un par, etiqueta concepto-uri concepto que representa esa etiqueta
	 */
	private static void addLabelUriPairToLabelUrisHash(String labelConcept, String uriConcept,
			HashMap<String, Set<String>> labelUris) {
		if (!labelUris.containsKey(labelConcept)) {
			labelUris.put(labelConcept, new HashSet<String>());
		}
		labelUris.get(labelConcept).add(uriConcept);
	}

	/***********************************************************************************/
	/**
	 * aplica un patron de reemplazo en un texto
	 */
	private static String replacePattern(String labelConcept, String pattern, String replacement) {
		StringBuffer sb = new StringBuffer();
		Matcher m = Pattern.compile("(\\(|\\-|\")[a-zA-Z ]+(\\)|\\-|\")").matcher(labelConcept);
		while (m.find()) {
			m.appendReplacement(sb, Matcher.quoteReplacement(""));
		}
		m.appendTail(sb);
		return sb.toString().trim();

	}

	/*********************************************************************************/
	/**
	 * quita de los nombres acentos y �s y lo pasa a minuscula para que sea mas
	 * facil de comparar
	 */
	private static String correctLabels(String label) {
		// eliminamos acentos y tildes que dan problemas al buscar
		return label.toLowerCase().replaceAll("�", "a").replaceAll("�", "e").replaceAll("�", "i").replaceAll("�", "o")
				.replaceAll("�", "u").replaceAll("�", "n").replaceAll("�", "a").replaceAll("�", "e")
				.replaceAll("�", "i").replaceAll("�", "o").replaceAll("�", "u");
	}

	/*******************************************************/
	/**
	 * fija los parametros del tasklet
	 */
	public void setRdfSource(String rdfSource) {
		this.rdfSource = rdfSource;
	}

	public void setExceptionsFile(String exFile) throws Exception {
		termExceptions = new HashSet<String>();
		BufferedReader exread = new BufferedReader(new FileReader(exFile));
		String except = exread.readLine();
		while (except != null) {
			termExceptions.add(except);
			except = exread.readLine();
		}
		exread.close();
	}

	public void setDestFile(String destFile) {
		this.destFile = destFile;
	}

	public void setDestHashFile(String destHashFile) {
		this.destHashFile = destHashFile;
	}

	public void setLangsToProcess(List<String> langsToProcess) {
		this.langsToProcess = langsToProcess;
	}

	public void setPluralRemoval(boolean pluralRemoval) {
		this.quitarPlurales = pluralRemoval;
	}
}
