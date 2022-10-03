package thematicQualityAnalysis;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathFactory;

import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;

/**
 * Obtiene el uso de los tesaruos en una coleccion de metadatos separando datos y servicios  
 */
public class Tasklet_ThesaurusUseInMdAnalysis implements Tasklet {
		//database connection
		private String dbname, dbuser, dbpass, dbhost, dbport;
		
		//lector de xml y consultas a hacer
		private XPath xpath = XPathFactory.newInstance().newXPath();
		
		//listado de me
		private String exprDataKwrds = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/"
				+ "*[local-name()='MD_DataIdentification']/*[local-name()='descriptiveKeywords']/"
				+ "*[local-name()='MD_Keywords']/*[local-name()='thesaurusName']/*[local-name()='CI_Citation']/"
				+ "*[local-name()='title']/*[local-name()='CharacterString']";
		
		private String exprServKwrds = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/"
				+ "*[local-name()='SV_ServiceIdentification']/*[local-name()='descriptiveKeywords']/"
				+ "*[local-name()='MD_Keywords']/*[local-name()='thesaurusName']/*[local-name()='CI_Citation']/"
				+ "*[local-name()='title']/*[local-name()='CharacterString']";
		
		private String exprData = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/"
				+ "*[local-name()='MD_DataIdentification']";
		private String exprServ = "/*[local-name()='MD_Metadata']/*[local-name()='identificationInfo']/"
				+ "*[local-name()='SV_ServiceIdentification']";
		
		   
		/************************************************************/
		/**
		 * Obtiene el uso de los tesaruos en una coleccion de metadatos separando datos y servicios  
		 */	
		public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {			
			//nos conectamos a la base de datos
			Class.forName("org.postgresql.Driver").newInstance();
			String url = "jdbc:postgresql://" + dbhost + ":" + dbport + "/" + dbname;
			Connection conn = DriverManager.getConnection(url, dbuser, dbpass);
			conn.setAutoCommit(false);
			
			//mostramos los usos del tesauro en los datos
			HashMap<String, Integer> agrega = obtainThesaurusOccurrences(conn, exprDataKwrds, exprData);
			System.out.println("----------------------------------------------");
			System.out.println("Uso de los tesauros en los metadatos de datos");
			System.out.println("----------------------------------------------");
			for(String t: agrega.keySet()){
				System.out.println(t+" | "+ agrega.get(t));
			}
			System.out.println("----------------------------------------------");
					
			//mostramos los usos del tesauro en los servicios
			agrega = obtainThesaurusOccurrences(conn, exprServKwrds, exprServ);
			System.out.println("----------------------------------------------");
			System.out.println("Uso de los tesauros en los metadatos de servicios");
			System.out.println("----------------------------------------------");
			for(String t: agrega.keySet()){
				System.out.println(t+" | "+ agrega.get(t));
			}
			System.out.println("----------------------------------------------");
			
			conn.close();		
			return RepeatStatus.FINISHED;
		}	
				
		/**********************************************************/
		/**
		 * Cuenta las ocurrencias de un tesauro en un tipo de metadato en concreto
		 */
		private HashMap<String, Integer> obtainThesaurusOccurrences(Connection conn, String keywordField, String xpathType) throws Exception{
			//lector de xml;
			DocumentBuilder builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
			
			//seleccionamos todos los metadatos
			Statement st = conn.createStatement(); st.setFetchSize(50);	
			ResultSet r = st.executeQuery("SELECT id, data from metadata"); 
			Statement st2 = conn.createStatement(); st2.setFetchSize(50);
			
			//contamos las ocurrencias de cada tesauro en cada mentadato
			//solo se cuenta una ocurrencia del tesauro por metadato
			HashMap<String, Integer> agrega = new HashMap<String,Integer>();	
			while (r.next()){	
				Document doc = builder.parse(new ByteArrayInputStream(r.getString(2).getBytes(StandardCharsets.UTF_8)));
				
				//si el metadato es del tipo incorrecto data vs service lo ignoramos
				if(!hasXMLNode(xpathType,doc)){continue;}
					
				//nos guardamos los tesauros diferentes usados en cada metadato
				NodeList nodeList = (NodeList) xpath.compile(keywordField).evaluate(doc, XPathConstants.NODESET);
				Set<String> res = new HashSet<String>();	
				for (int i = 0; i < nodeList.getLength(); i++) {
					if(nodeList.item(i)!=null && nodeList.item(i).getFirstChild()!=null){
						String thesName= nodeList.item(i).getFirstChild().getNodeValue();
						if(thesName!=null){
							res.add(thesName);							
						}
					}
				}
				
				//en una copia de los resultados quitamos los tesauros de lugar y de temas de inspire
				//si no quedan tesauros nos lo apuntamos
				Set<String> resNoPlaceInsp =removePlaceThesaurusFromSet(res);
				resNoPlaceInsp = removeInspireThesaurusFromSet(res);
				if(resNoPlaceInsp.size()==0){
					addEntryToHashTable(agrega,"NO THESAURUS (EXCLUDING PLACE AND INSPIRE THEMES)");	
				}
				
				//en una copia de los resultados quitamos todos los tesauros que no sean agrovoc, eurovoc y gemet
				//si no quedan tesauros nos lo apuntamos
				Set<String> resJustGemAgroEuro =removeNonGemetAgrovocEurovocThesaurusFromSet(res);		
				if(resJustGemAgroEuro.size()==0){
					addEntryToHashTable(agrega,"NO THESAURUS (EXCLUDING ALL BUT GEMET, AGROVOC, AND EUROVOC)");	
				}
				
				//contamos cuantos tienen algo de temas de inspire
				Set<String> resInspireThemes =removeNonInspireThemesThesaurusFromSet(res);		
				if(resInspireThemes.size()==0){
					addEntryToHashTable(agrega,"NO THESAURUS (EXCLUDING ALL BUT INSPIRE THEMES)");	
				}
								
				//añadimos los tesauros usados al contador de uso de cada tesauro
				//si no hay entradas, lo cuenta como sin tesauros
				if(res.size()==0){
					addEntryToHashTable(agrega,"NO THESAURUS AT ALL");
				}else{
					for(String s: res){
						addEntryToHashTable(agrega,s);
					}
				}
			}
			
			return agrega;
			
			
		}
		
		/*********************************************************************/
		/**
		 * añade una ocurrencia del tipo indicado a la hashtable
		 */
		private void addEntryToHashTable(HashMap<String, Integer> agrega, String entry){
			if (agrega.containsKey(entry)){
				agrega.put(entry, agrega.get(entry)+1);
			}else{
				agrega.put(entry, 1);
			}
		}
		
		/*********************************************************************/
		/**
		 * detecta si el metadato tiene el nodo indicado
		 * se usa para determinar si el metadato es de datos o de servicio
		 */
		private boolean hasXMLNode(String xpathType, Document doc) throws Exception{
			NodeList nodeList = (NodeList) xpath.compile(xpathType).evaluate(doc, XPathConstants.NODESET);
			if(nodeList==null || nodeList.getLength()==0){
				return false;
			}
			return true;
		}
		
		/*********************************************************************/
		/**
		 * borra las ocurrencias de los tesauros de lugar del set para no contarlos en el analisis
		 */
		private Set<String> removePlaceThesaurusFromSet(Set<String> set){
			Set<String> reducido = new HashSet<String>();
			for(String s: set){
				if(!(s.startsWith("European") || s.startsWith("ISO") || s.startsWith("CEO")
						|| s.startsWith("NOMENCLATOR") || s.startsWith("Nomenclature"))){
					reducido.add(s);
				}
			}
			return reducido;		
		}
		/*********************************************************************/
		/**
		 * borra las ocurrencias de los tesauros de temas de inspire para no contarlos en el analisis
		 */
		private Set<String> removeInspireThesaurusFromSet(Set<String> set){
			Set<String> reducido = new HashSet<String>();
			for(String s: set){
				if(!(s.contains("INSPIRE") || s.contains("Theme") || s.contains("theme"))){
					reducido.add(s);
				}
			}
			return reducido;		
		}
		
		/*********************************************************************/
		/**
		 * borra las ocurrencias de los tesauros que no sean ni gemet, ni agrovoc, ni eurovoc
		 */
		private Set<String> removeNonGemetAgrovocEurovocThesaurusFromSet(Set<String> set){
			Set<String> reducido = new HashSet<String>();
			for(String s: set){
				if(s.startsWith("AGROVOC") || s.startsWith("EURO") || s.startsWith("EuroV") || s.startsWith("GEMET")){
					reducido.add(s);
				}
			}
			return removeInspireThesaurusFromSet(reducido);		
		}
		
		
		/*********************************************************************/
		/**
		 * borra todas las ocurrencias de los tesauros menos las de inspire
		 */
		private Set<String> removeNonInspireThemesThesaurusFromSet(Set<String> set){
			Set<String> reducido =  removeInspireThesaurusFromSet(set);
			Set<String> reducido2 =  new HashSet<String>();
			for(String s: set){
				if(!reducido.contains(s)){
					reducido2.add(s);
				}
			}
			return reducido2;
		}
			
		/***************************************************************/
		/**
		 * Propiedades del tasklet
		 */
		public void setDbname(String dbname) {this.dbname = dbname;}
		public void setDbuser(String dbuser) {this.dbuser = dbuser;}
		public void setDbpass(String dbpass) {this.dbpass = dbpass;}
		public void setDbhost(String dbhost) {this.dbhost = dbhost;}
		public void setDbport(String dbport) {this.dbport = dbport;}
	}
