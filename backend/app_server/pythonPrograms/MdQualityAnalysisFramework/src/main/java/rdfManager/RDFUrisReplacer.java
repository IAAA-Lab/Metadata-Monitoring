package rdfManager;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Property;
import org.apache.jena.rdf.model.ResIterator;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.rdf.model.Statement;


/**
 * dado un modelo, permite cambiar uis de recursos y propiedades y namespaces, por otras. de forma global (base uri)
 * o de forma individual (ocurrencias deuna propiedad o recurso
 */
public class RDFUrisReplacer {

	//propiedades de rdf
	private final Property owlSameAsProp = RDFPropertyManager.owlSameAsProp;
	private final Property dctIdentiferProp = RDFPropertyManager.dctIdentiferProp;
	private final Property dctReferencesProp = RDFPropertyManager.dctReferencesProp;
	private final String dctNsPrefix= RDFPropertyManager.dctNsPrefix;
	private final String dctBaseUri = RDFPropertyManager.dctBaseUri;
	
	/******************************************************************************/
	/**
	 * dado un modelo, cambia el contenido del namespace indicado, por el valor indicado
	 * crea copia modelo. no destructiva)
	 */
	public Model replaceNamespace (Model modelo, String nsName, String destNsVal){
		Model transfModel = ModelFactory.createDefaultModel();
		transfModel.add(modelo);
		transfModel.removeNsPrefix(nsName);
		transfModel.setNsPrefix(nsName, destNsVal);
		return transfModel;
	}
	
	/******************************************************************************/
	/**
	 * dado un modelo, cambia la uriindicada por otra diferente
	 * en todos los recursos con esa uri. (crea copia modelo. no destructiva)
	 */
	public Model replaceConceptUri(String sourceUri, String destUri, Model modelo){
		//usa el de base uri pero pasandole una uri entera. funciona igual.
		return replaceBaseConceptUri( sourceUri,  destUri,  modelo);
	}
	
	/******************************************************************************/
	/**
	 * dado un modelo, cambia la uri base indicada (de las propiedades) por otra diferente
	 * en todas las propiedades con esa uri base. (crea copia modelo. no destructiva)
	 */
	public Model replacePropUri(String sourceBaseUri, String destBaseUri, Model modelo){
		//usa el de base uri pero pasandole una uri entera. funciona igual.
		return replaceBasePropUri( sourceBaseUri, destBaseUri, modelo);
	}
	
	/******************************************************************************/
	/**
	 * dado un modelo, cambia la uri base indicada (de los recursos) por otra diferente
	 * en todos los recursos con esa uri base. (crea copia modelo. no destructiva)
	 * si se pasa una propiedad adicional la uri original la a�ade como propiedad
	 * del recurso
	 */
	public Model replaceBaseConceptUri(String sourceBaseUri, String destBaseUri, Model modelo){
		return replaceLDExistentBaseConceptUri( sourceBaseUri,  destBaseUri,  modelo, false);
	}
	
	/*****************************************************************************/
	/**
	 * reemplaza la uri base de un tesauro y a�ade uan refernecia a la original como linked data
	 */
	public Model replaceLDExistentBaseConceptUri(String sourceBaseUri, String destBaseUri, Model modelo, boolean addReference){
		//creamos el nuemo modelo
		Model transfModel = ModelFactory.createDefaultModel();
		//trasladamos los statements cambiando las uris donde toque
		for (Statement st:modelo.listStatements().toList()){
			//traducimos el subject
			Resource translRes = transfModel.createResource(st.getSubject().getURI().replace(sourceBaseUri, destBaseUri));
			if(addReference){ 			
					translRes.addProperty(owlSameAsProp, st.getSubject());
			}
			
			//si el object es recurso lo traducimos y creamos el nuevo statement
			if(st.getObject().isResource()){
				//traducimos el object
				String newObjUri = st.getResource().getURI().replace(sourceBaseUri, destBaseUri);
				Resource translObj = transfModel.createResource(newObjUri);
				//creamos el statement
				transfModel.add(translRes, st.getPredicate(), translObj);
			}else{//creamos el nuevo statement directamente sin mas proceso
				transfModel.add(translRes, st.getPredicate(), st.getObject());
			}
			
		}
		//copiamos los namespaces al nuevo modelo
		transfModel.setNsPrefixes(modelo.getNsPrefixMap());
		return transfModel; 
	}
	
	/*****************************************************************************/
	/**
	 * reemplaza la uri base de un tesauro y a�ade uan refernecia a la original como linked data
	 */
	public Model replaceNonLDExistentBaseConcept(String sourceBaseUri, String destBaseUri, Model modelo, Property sourceUriProp, String repPattern){
		Model transfModel = ModelFactory.createDefaultModel();
		//trasladamos los statements cambiando las uris donde toque
		for (Statement st:modelo.listStatements().toList()){
			//traducimos el subject
			Resource translRes = transfModel.createResource(st.getSubject().getURI().replace(sourceBaseUri, destBaseUri));
			
			//a�adimos la uri original como literal
			String uriOrig= st.getSubject().getURI();
			translRes.addProperty(dctIdentiferProp, transfModel.createLiteral(uriOrig));
			
			//generamos la uri que es visible en la web	
			if(sourceUriProp!=null && st.getSubject().hasProperty(sourceUriProp)){
				uriOrig = st.getSubject().getProperty(sourceUriProp).getString();
			}	
			String replacementUri = repPattern.replace("**", uriOrig);
			translRes.addProperty(dctReferencesProp, transfModel.createResource(replacementUri));
			
			//si el object es recurso lo traducimos y creamos el nuevo statement
			if(st.getObject().isResource()){
				//traducimos el object
				String newObjUri = st.getResource().getURI().replace(sourceBaseUri, destBaseUri);
				Resource translObj = transfModel.createResource(newObjUri);
				//creamos el statement
				transfModel.add(translRes, st.getPredicate(), translObj);
			}else{//creamos el nuevo statement directamente sin mas proceso
				transfModel.add(translRes, st.getPredicate(), st.getObject());
			}
			
		}
		//copiamos los namespaces al nuevo modelo
		transfModel.setNsPrefixes(modelo.getNsPrefixMap());
		transfModel.setNsPrefix(dctNsPrefix, dctBaseUri);
		return transfModel; 
	}
	
	/******************************************************************************/
	/**
	 * dado un modelo, cambia la uri base indicada (de las propiedades) por otra diferente
	 * en todas las propiedades con esa uri base. (crea copia modelo. no destructiva)
	 */
	public Model replaceBasePropUri(String sourceBaseUri, String destBaseUri, Model modelo){
		//creamos el nuemo modelo
		Model transfModel = ModelFactory.createDefaultModel();
		//trasladamos los statements cambiando las uris donde toque
		for (Statement st:modelo.listStatements().toList()){
			//traducimos la propiedad
			Property translProp = transfModel.createProperty(st.getPredicate().getURI().replace(sourceBaseUri, destBaseUri));
			
			//creamos el nuevo statement directamente sin mas proceso
			transfModel.createStatement(st.getSubject(), translProp, st.getObject());
				
		}
		
		//copiamos los namespaces al nuevo modelo
		transfModel.setNsPrefixes(modelo.getNsPrefixMap());
		return transfModel;
	}
	
	/******************************************************************************/
	/**
	 * coge todas las uris del modelo y cambia la parte corresponiente al concepto
	 * por un identificador numérico. Ahora mismo es no destructivo, pero muy
	 * lento. para cada concepto que reemplaza hace una copia del model
	 */
	public Model replaceUrisConceptComponentByNumericId(String sourceBaseUri, Model modelo){
		int indexResComp=1;
		ResIterator it = modelo.listSubjects();
		while (it.hasNext()){
		    Resource res = it.next();
			String concUri=res.getURI();
			if(concUri.startsWith(sourceBaseUri)){
				modelo = replaceBaseConceptUri(concUri,  sourceBaseUri+Integer.toString(indexResComp),  modelo);
			}
		}
		return modelo;
	}	
}
