package preprocessing;

import java.io.File;
import java.io.FileOutputStream;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.Property;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;

import rdfManager.JenaModelManager;
import rdfManager.RDFUrisReplacer;

/******************************************************
 * convierte un tesauro con uris referenciables en su version de linked data
 * usable para mapas de topicos
 * Cambia las uris de un espacio de nombres a otro
 */
public class Tasklet_ConceptUris_To_ProxyUris implements Tasklet {
	// properties del bean
	private String sourThesFile = null, destThesFile = null;
	private String sourBaseUri = null, destBaseUri = null, repPattern = null, sourceUriProp = null;

	/****************************************************************************/
	/**
	 * ejecuta la conversion de la uri de linked data a la uri local con la
	 * referencia adecuada
	 */
	public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {

		// cargamos lel modelo fuente
		Model source = JenaModelManager.loadJenaModel(sourThesFile);

		// convertimos el modelo
		RDFUrisReplacer urisRep = new RDFUrisReplacer();
		Model destino = null;
		if (repPattern == null) {
			destino = urisRep.replaceLDExistentBaseConceptUri(sourBaseUri, destBaseUri, source, true);
		} else if (sourceUriProp != null) {
			Property prop = source.getProperty(sourceUriProp);
			destino = urisRep.replaceNonLDExistentBaseConcept(sourBaseUri, destBaseUri, source, prop, repPattern);
		} else {
			destino = urisRep.replaceNonLDExistentBaseConcept(sourBaseUri, destBaseUri, source, null, repPattern);
		}

		// guardamos el modelo y lo cerramos (crea la ruta)
		File destFile = new File(destThesFile);
		destFile.getParentFile().mkdirs();
		destino.write(new FileOutputStream(destFile));
		destino.close();
		return RepeatStatus.FINISHED;
	}

	/***********************************************************************/
	/**
	 * obtenemos los valores de las propiedades
	 */
	public void setSourThesFile(String sourThesFile) {
		this.sourThesFile = sourThesFile;
	}

	public void setDestThesFile(String destThesFile) {
		this.destThesFile = destThesFile;
	}

	public void setSourBaseUri(String sourBaseUri) {
		this.sourBaseUri = sourBaseUri;
	}

	public void setDestBaseUri(String destBaseUri) {
		this.destBaseUri = destBaseUri;
	}

	public void setReplacementPattern(String repPattern) {
		this.repPattern = repPattern;
	}

	public void setSourceUriProp(String sourceUriProp) {
		this.sourceUriProp = sourceUriProp;
	}
}
