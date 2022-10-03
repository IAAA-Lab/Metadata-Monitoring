package rdfManager;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Paths;
import java.util.Properties;

import org.apache.commons.io.FileUtils;
import org.apache.jena.atlas.lib.FileOps;
import org.apache.jena.query.Dataset;
import org.apache.jena.query.ReadWrite;
import org.apache.jena.query.text.EntityDefinition;
import org.apache.jena.query.text.TextDatasetFactory;
import org.apache.jena.query.text.TextIndex;
import org.apache.jena.query.text.TextIndexConfig;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.RDFReader;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.RDFFormat;
import org.apache.jena.tdb.TDBFactory;
import org.apache.jena.vocabulary.RDFS;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

/**
 * clase de utilidad que proporciona lectura y Escritura de un modelo de Jena
 */
public class JenaModelManager {

	/*******************************************************************/
	/**
	 * carga el tesaruo indicado en un modelo de Jena, con la uri base del modelo
	 */
	public static Model loadJenaModel(String thes)throws Exception{
		return loadJenaModel(thes, null);
	}
	
	/*******************************************************************/
	/**
	 * carga el tesaruo indicado en un modelo de Jena, con la uri base del modelo
	 */
	public static Model loadJenaModel(String sourceFile, String uri)throws Exception{
		Model model = ModelFactory.createDefaultModel();
		loadJenaModel(model,sourceFile,uri);
		return model;
	}
	
	/*******************************************************************/
	public static void loadJenaModel(Model model, String sourceFile, String uri)throws Exception{
		try{	
			InputStream in = new FileInputStream((new File(sourceFile)).getAbsolutePath());
			model.read(in, uri);
		}catch (Exception er){
			System.err.println(er.getMessage());
			System.err.println("reintentando con un parser laxo");
			RDFReader r = model.getReader("RDF/XML");
			r.setProperty("iri-rules", "iri");
			InputStream in = new FileInputStream((new File(sourceFile)).getAbsolutePath());
			r.read(model,in, uri);
		}
	}
	
	/*******************************************************************/
	public static Model loadJenaModelN3(Model model, String sourceFile, String uri){
		try{
			InputStream in = new FileInputStream((new File(sourceFile)).getAbsolutePath());
			model.read(in, uri,"N3");
		}catch (Exception er){
			er.printStackTrace();
		}
		return model;
	}
	
	/*******************************************************************/
	/**
	 * Coje un modelo de rdf partido en varios ficheros en un mismo
	 * directorio y lo carga todo
	 */
	public static Model loadJenaMultipleModel(String sourceDir)throws Exception{
		return loadJenaMultipleModel(sourceDir, null);
	}
	
	/*******************************************************************/
	/**
	 * Coje un modelo de rdf partido en varios ficheros en un mismo
	 * directorio y lo carga todo
	 */
	public static Model loadJenaMultipleModel(String sourceDir, String uri)throws Exception{
		Model model = ModelFactory.createDefaultModel();
		File[] files=(new File(sourceDir)).listFiles();
		for (File fich: files){
			if(!fich.isDirectory()){
				Model partModel = loadJenaModel(fich.getAbsolutePath(), uri);
				model.add(partModel);
				model.setNsPrefixes(partModel.getNsPrefixMap());
			}
		}
		return model;
	}
	
	/*******************************************************************/
	/**
	 * Coje un modelo de rdf partido en varios ficheros en un mismo
	 * directorio y lo carga todo
	 */
	public static Model loadJenaModelInDatasetDefRDFCol(Dataset reposit, String sourceFile)throws Exception{
		Model model = reposit.getDefaultModel();
		File[] files=(new File(sourceFile)).listFiles();
		for (File fich: files){
			if((!fich.isDirectory()) && (fich.getName().endsWith(".owl") || fich.getName().endsWith(".rdf"))){
				System.out.println(fich.getAbsolutePath());
				loadJenaModel(model,fich.getAbsolutePath(),null);
			}
		}
		return model;
	}
	
	/*******************************************************************/
	/**
	 * Coje un modelo de rdf partido en varios ficheros en un mismo, 
	 * directorio y lo carga todo en un tdb en el directorio indicado. Si se dice, borra primero el tdb
	 */
	public static Dataset loadJenaModelInDatasetDefRDFCol(String sourceFileDir,String repositDir)throws Exception{
		FileOps.clearDirectory(repositDir) ;
		Dataset dataset = TDBFactory.createDataset(repositDir);
		loadJenaModelInDatasetDefRDFCol(dataset,sourceFileDir);
		return dataset;
	}
	
	/*******************************************************************/
	/**
	 * guarda el tesaruo indicado en un modelo de Jena
	 * @throws IOException 
	 */
	public static void saveJenaModel(Model modelToWrite, String destFile) throws IOException{	
		    File destF = new File(destFile); destF.getParentFile().mkdirs();	
		    FileOutputStream fos = new FileOutputStream(destFile);
		    RDFDataMgr.write(fos, modelToWrite, RDFFormat.RDFXML_PLAIN) ;
	}
	/*******************************************************************/
	/**
	 * guarda el tesaruo indicado en un modelo de Jena en el formato indicado
	 * @throws IOException 
	 */
	public static void saveJenaModel(Model modelToWrite,String destFile, RDFFormat format) throws IOException{	
		    File destF = new File(destFile); destF.getParentFile().mkdirs();	
		    FileOutputStream fos = new FileOutputStream(destFile);
		    RDFDataMgr.write(fos, modelToWrite, format) ;
	}
	
	/*******************************************************************/
	/**
	 * crea un modelo tdb de jena en el directorio indicado
	 */
	public static Dataset createTDBRepository(String dirTDB, boolean reset){
		if(FileOps.exists(dirTDB) && reset){
			FileOps.clearDirectory(dirTDB) ;
		}
		File dir = new File(dirTDB); dir.mkdirs();
		return TDBFactory.createDataset(dirTDB);
	}
	
	/*******************************************************************/
	/**
	 * devuelve un modelo tdb de jena existente en el directorio indicado
	 */
	public static Dataset getTDBRepository(String dirTDB){
		return TDBFactory.createDataset(dirTDB);
	}
	
	/*******************************************************************/
	/**
	 * carga un modelo de jena en un dataset tdb
	 */
	public static void loadJenaModelInDataset(Dataset reposit, String sourceFile, String uri)throws Exception{
		Model model = reposit.getNamedModel(uri);
		loadJenaModel(model,sourceFile,uri);
	}
	
	/*******************************************************************/
	/**
	 * carga un modelo de jena en un dataset tdb
	 */
	public static void loadJenaModelInDatasetDef(Dataset reposit, String sourceFile)throws Exception{
		Model model = reposit.getDefaultModel();
		loadJenaModel(model,sourceFile,null);
	}
	
	/**
	 * carga un modelo de jena en un dataset tdb fuente en n3
	 */
	public static void loadJenaModelInDatasetDefN3(Dataset reposit, String sourceFile){
		Model model = reposit.getDefaultModel();
		loadJenaModelN3(model,sourceFile,null);
	}
	
	
	/*******************************************************************/
	/**
	 * exporta un modelo de jena que esta en un dataset
	 * @throws IOException 
	 */
	public static void saveJenaModelInDataset(Dataset reposit, String destFile, String uri) throws IOException{
		Model model = reposit.getNamedModel(uri);
		saveJenaModel(model,destFile);
	}
	
	/*******************************************************************/
	/**
	 * obtiene el modelo de dentro de un dataset
	 */
	public static Model getModelFromDataset(Dataset reposit, String uri){
		return reposit.getNamedModel(uri);
	}
	
	public static Model getModelFromDataset(Dataset reposit){
		return reposit.getDefaultModel();
	}
	
	/*******************************************************************/
	/**
	 * reescribe un modelo de jena (objetivo, dejarlo formato recursos enlazados)
	 * @throws IOException 
	 */
	public static void rewriteJenaModel(String file) throws Exception{
		saveJenaModel(loadJenaModel(file), file);
	}
	
	
	/*******************************************************************/
	/**
	 * a�ade al modelo los namespaces indicados en un fichero de propiedades

	 */
	public static void setNamespacesToModel(String nameSpacesFile, Model modelo) throws FileNotFoundException, IOException{
		setNamespacesToModel(nameSpacesFile,modelo);
	}
	/*******************************************************************/
	/**
	 * a�ade al modelo los namespaces indicados en un fichero de propiedades
	 * borra los anteriores si se indica que lo haga 
	 */
	public static void setNamespacesToModel(String nameSpacesFile, Model modelo, boolean deleteExistentOnes) throws FileNotFoundException, IOException{
		//borramos los prefijos viejos
		if(deleteExistentOnes){
			for (String nsId:modelo.getNsPrefixMap().keySet()){
				modelo.removeNsPrefix(nsId);
			}
		}
		
		//a�adimos los nuevos
		Properties properties = new Properties();
		properties.load(new FileInputStream(nameSpacesFile));
		for (Object nsId:properties.keySet()){
			String nsURI = properties.getProperty((String)nsId);
			modelo.setNsPrefix((String)nsId,nsURI);
		}
	}
	
	/*******************************************************************/
	/**
	 * crea un dataset con indice de texto
	 */
	public static Dataset loadRDFIntoLuceneTDBDataset(String repositoryDir, String rdfFile){
		try{
			//creo el dataset tdb en disco
			Dataset dat = JenaModelManager.createTDBRepository(repositoryDir+"/tdb", true);
			
			//creo el indice lucene
			FileUtils.deleteDirectory(new File(repositoryDir+"/lucene"));
		    Directory indexdir =  FSDirectory.open(Paths.get(repositoryDir+"/lucene"));
		    EntityDefinition entDef = new EntityDefinition("uri", "text", RDFS.label) ;	    		
		    TextIndex index = TextDatasetFactory.createLuceneIndex(indexdir, new TextIndexConfig(entDef));			 
		    
		    //enlazo el dataset y el indice en un textdataset		    
			Dataset ds = TextDatasetFactory.create(dat, index) ;
			
			//relleno el dataset con datos
			ds.begin(ReadWrite.WRITE);
		    RDFDataMgr.read(ds.getDefaultModel(), rdfFile) ;
		    ds.commit() ;
		    ds.end();
		    		   
		    return ds;
		}catch (Exception er){}
		return null;
	}
	
	/*******************************************************************/
	/**
	 * carga un dataset con indice de texto
	 */
	public static Dataset loadLuceneTDBDataset (String repositoryDir){
		try{
			//obtengo el dataset tdb
			Dataset dat = JenaModelManager.getTDBRepository(repositoryDir+"/tdb");
			//obtengo el indice en disco
			EntityDefinition entDef = new EntityDefinition("uri", "text", RDFS.label) ;	  
			Directory indexdir =  FSDirectory.open(Paths.get(repositoryDir+"/lucene"));
			TextIndex index = TextDatasetFactory.createLuceneIndex(indexdir, new TextIndexConfig(entDef));			 
			//devuelvo el dataset cargado en modo lectura
			Dataset ds = TextDatasetFactory.create(dat, index) ;
			ds.begin(ReadWrite.READ);		
			return ds;
		}catch (Exception er){er.printStackTrace();}
		return null;
	}
	
	public static Dataset loadLuceneTDBDatasetOld (String repositoryDir){
		try{
			//obtengo el dataset tdb
			Dataset dat = JenaModelManager.getTDBRepository(repositoryDir+"/tdb");			
			dat.begin(ReadWrite.READ);		
			return dat;
		}catch (Exception er){er.printStackTrace();}
		return null;
	}
	
}
