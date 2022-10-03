package reportGeneration;

import java.io.FileOutputStream;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathFactory;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.Property;
import org.apache.jena.rdf.model.RDFNode;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.rdf.model.Statement;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

import rdfManager.JenaModelManager;
import rdfManager.MdQualityAnalysisRDFPropertyManager;
import rdfManager.RDFPropertyManager;

/**
 * Genera en una excel un resumen de los resultados obtenidos en el analisis
 * calidad espacial y resultado del report de inspire
 */
public class Tasklet_QualityReportGenerator implements Tasklet {

	private String qualityReportOutputFile;
	private String qualityResultRDFFile;
	XPath xpath = XPathFactory.newInstance().newXPath();

	public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {

		// cargamos el modelo a analizar
		Model qreport = JenaModelManager.loadJenaModel(qualityResultRDFFile);
		List<Statement> conc = qreport.listStatements(null, RDFPropertyManager.rdfTypeProp, (RDFNode) null).toList();
		
		// creamos el excel
		Workbook wb = new XSSFWorkbook();

		//hacemos el analisis espacial
		generateSpatialAnalysisResult(wb,conc);
		
		//hacemos el analisis de inspire
		inspireAnalysis(wb,conc);
		
		// guardamos el excel
		FileOutputStream fos = new FileOutputStream(qualityReportOutputFile);
		wb.write(fos);
		fos.close();

		return RepeatStatus.FINISHED;
	}

	/****************************************************************************/
	/**
	 * a partir de los datos hace el analis de la calidad de la información espacial
	 */
	private void generateSpatialAnalysisResult(Workbook wb, List<Statement> conc){
		// lo rellenamos con la información de todos los conceptos
		int i = 0;
		Sheet sheet = wb.createSheet("Quality Result");
		addHeader(sheet.createRow(i++));

		// añadimos el resumen de la calidad espacial
		for (Statement st : conc) {
			Resource res = st.getSubject();
			String type = getProperty(res, MdQualityAnalysisRDFPropertyManager.mdType);
			String identifier = getProperty(res, MdQualityAnalysisRDFPropertyManager.fileIdentifier);
			String title = getProperty(res, MdQualityAnalysisRDFPropertyManager.title);
			String bbqa = getProperty(res, MdQualityAnalysisRDFPropertyManager.bbAnalysysResult);
			String placeqa = getProperty(res, MdQualityAnalysisRDFPropertyManager.placeAnalysisResult);
			String corrqa = getProperty(res, MdQualityAnalysisRDFPropertyManager.bbPlaceCorrelationAnalysisResult);
			String placesText = getProperty(res, MdQualityAnalysisRDFPropertyManager.bbPlaceTextCorrelationAnalysisResult);
			String bb = getProperty(res, MdQualityAnalysisRDFPropertyManager.boundingBox);
			String places = getProperty(res, MdQualityAnalysisRDFPropertyManager.placeKeyword);
			String textPlaces = getProperty(res, MdQualityAnalysisRDFPropertyManager.textPlacesFound);
			Row r = sheet.createRow(i++);
			int j = 0;
			r.createCell(j++).setCellValue(type);
			r.createCell(j++).setCellValue(identifier);
			r.createCell(j++).setCellValue(title);
			r.createCell(j++).setCellValue(bbqa);
			r.createCell(j++).setCellValue(placeqa);
			r.createCell(j++).setCellValue(corrqa);
			r.createCell(j++).setCellValue(placesText);
			r.createCell(j++).setCellValue(bb);
			r.createCell(j++).setCellValue(places);
			r.createCell(j++).setCellValue(textPlaces);
		}
	}
	
	/*********************************************************/
	/**
	 * realiza el analisis de los errores de inspire
	 */
	private void inspireAnalysis(Workbook wb, List<Statement> conc) throws Exception{
		
		//obtenemos la información de validación de los metadatos
		List<InfoMD> infoL = new ArrayList<InfoMD>();
		for (Statement st : conc) {
			Resource res = st.getSubject();
			String type = getProperty(res, MdQualityAnalysisRDFPropertyManager.mdType);
			String title = getProperty(res, MdQualityAnalysisRDFPropertyManager.title);
			String identifier = getProperty(res, MdQualityAnalysisRDFPropertyManager.fileIdentifier);
			String validation = getProperty(res, MdQualityAnalysisRDFPropertyManager.xmlValidationErrors);
			infoL.add(new InfoMD(type,title, identifier,validation));
		}
		
		//definimos las rutas xpath de las propidades a analizar
		 
		 XPathExpression exprErr = xpath.compile("/*[local-name() = 'Resource']/*[local-name() = 'ResourceReportResource']"
				+ "/*[local-name() = 'InspireValidationErrors']/*[local-name() = 'ValidationError']");
		 XPathExpression exprWarn = xpath.compile("/*[local-name() = 'Resource']/*[local-name() = 'ResourceReportResource']"
				+ "/*[local-name() = 'InspireValidationWarnings']/*[local-name() = 'ValidationError']");
		 XPathExpression exprType = xpath.compile("./*[local-name() = 'SourceOfRequirement']/"
				+ "*[local-name() = 'IntraDocumentLocator']/*[local-name() = 'Description']");
		 XPathExpression exprValue = xpath.compile("./*[local-name() = 'GeoportalExceptionMessage']/"
				+ "*[local-name() = 'Message']");
		
		//procesamos cada report del validador
		DocumentBuilder dBuilder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
		for (InfoMD info : infoL) {
			Document doc = null;
			//identificamos los que son correctos
			if(info.validation.trim().equals("")){		
				continue;
			}
			
			
			//extraemos el contenido del report errores + warnings
			doc = dBuilder.parse(new InputSource( new StringReader( info.validation ) ));
			
			//si el metadato es del tipo incorrecto data vs service lo ignoramos
			//esto es temporal y solo ponerlo cuando se quiera filtrar el analisis a md de datos
			
			//System.out.println(info.validation);
			
			NodeList errors = (NodeList) exprErr.evaluate(doc, XPathConstants.NODESET);
			for(int k=0;k< errors.getLength();k++){
				info.errores.add(extractError(errors.item(k),"error", exprType, exprValue));
			}
			NodeList warn = (NodeList) exprWarn.evaluate(doc, XPathConstants.NODESET);
			for(int k=0;k< warn.getLength();k++){
				info.errores.add(extractError(warn.item(k),"warning", exprType, exprValue));
			}				
		}
		
		//generamos el report básico de errores encontrados
		int i=0;
		Sheet sheet = wb.createSheet("Insp results analisis");
		addHeader2(sheet.createRow(i++));
		for(InfoMD info :infoL){
			Row r = sheet.createRow(i++); int j=0;
			r.createCell(j++).setCellValue(info.type);
			r.createCell(j++).setCellValue(info.identifier);
			r.createCell(j++).setCellValue(info.title);
			//r.createCell(j++).setCellValue(info.correct);
			boolean hasWarnings = false;
			boolean haserrors = false;
			for(Error er: info.errores){
				if(!er.clase.equals("error")){
					hasWarnings = true;
				}
				if(er.clase.equals("error")){
					haserrors=true;
					
				}		
			}
			
			//es correcto, sin warnings ni errores
			if(!hasWarnings && !haserrors){
				r.createCell(j++).setCellValue(1);
			}else{
				r.createCell(j++).setCellValue(0);
			}
			
			//tiene warnings y no tiene errores
			if(hasWarnings && !haserrors){
				r.createCell(j++).setCellValue(1);
			}else{
				r.createCell(j++).setCellValue(0);
			}
			
			//tiene errores
			if(haserrors){
				r.createCell(j++).setCellValue(1);
			}else{
				r.createCell(j++).setCellValue(0);
			}
			
			//guardamos los errores
			for(Error er: info.errores){
				 r = sheet.createRow(i++);
				 r.createCell(j).setCellValue(er.clase);
				 r.createCell(j+1).setCellValue(er.type);
				 r.createCell(j+2).setCellValue(er.text);
			}
		}
		
		//generamos un report agregando todos los errores de inspire del mismo tipo
		HashMap<String,Integer> aggregados = new HashMap<String, Integer>();
		for(InfoMD info :infoL){
			Set<Error> tipos = new HashSet<Error>();
			tipos.addAll(info.errores);
			for(Error e:tipos){
				String res = e.clase+"@"+e.type+"-";
				if(aggregados.containsKey(res)){
					aggregados.put(res,aggregados.get(res)+1);
				}else{
					aggregados.put(res,1);
				}
			}
		}
		i=0;
	    sheet = wb.createSheet("Insp aggr results analisis");
		addHeader3(sheet.createRow(i++));
		for(String err :aggregados.keySet()){
			int oc = aggregados.get(err);
			String[] partes = err.split("@");
			Row r = sheet.createRow(i++); int j=0;
		    r.createCell(j++).setCellValue(partes[0]);
		    r.createCell(j++).setCellValue(partes[1]);
		    r.createCell(j++).setCellValue(oc);
		}
		
	}

	/************************************************************/
	/**
	 * Obtiene todos los errores en un nodo del validador
	 */
	private Error extractError(Node err, String clase, XPathExpression exprType, XPathExpression exprValue) throws Exception{
		NodeList typeE = (NodeList) exprType.evaluate(err, XPathConstants.NODESET);
		String tipos ="";
		for(int l=0;l< typeE.getLength();l++){
			Node t = typeE.item(l).getFirstChild();
			tipos+=t.getNodeValue()+"|";
		}		
		NodeList messE = (NodeList) exprValue.evaluate(err, XPathConstants.NODESET);
		String message ="";
		for(int l=0;l< messE.getLength();l++){
			Node t = messE.item(l).getFirstChild();
			message+=t.getNodeValue()+"|";
		}
		return new Error(tipos,message,clase);
	}
	
	
	
	/*************************************************************/
	/**
	 * lee una propiedad de un recurso RDF
	 */
	private String getProperty(Resource conc, Property prop) {
		String result = "";
		for (Statement st : conc.listProperties(prop).toList()) {
			if (result.length() == 0) {
				result = st.getString();
			} else {
				result = result + " | " + st.getString();
			}
		}
		return result;
	}

	/*********************************************************/
	/**
	 * añade el header indicado a la hoja
	 */
	private void addHeader(Row row) {
		row.createCell(0).setCellValue("Type");
		row.createCell(1).setCellValue("Identifier");
		row.createCell(2).setCellValue("MD title");
		row.createCell(3).setCellValue("Correct BB");
		row.createCell(4).setCellValue("Correct Place");
		row.createCell(5).setCellValue("Correct Correlation");
		row.createCell(6).setCellValue("Correlation BB y Text");
		row.createCell(7).setCellValue("BB");
		row.createCell(8).setCellValue("Places");
	}
	private void addHeader2(Row row) {
		row.createCell(0).setCellValue("Type");
		row.createCell(1).setCellValue("Identifier");
		row.createCell(2).setCellValue("MD title");
		row.createCell(3).setCellValue("Sin Errores ni warnings");
		row.createCell(4).setCellValue("Sin Errores, con warnings");
		row.createCell(5).setCellValue("Con Errores");
		//row.createCell(6).setCellValue("Errors Detail");
	}
	private void addHeader3(Row row) {
		row.createCell(0).setCellValue("Error Class");
		row.createCell(1).setCellValue("Error Type");
		row.createCell(2).setCellValue("Ocurrences");
	}

	/*************************************************/
	/**
	 * Clases para describir los errores
	 */
	private class InfoMD{
		public String type, title, identifier, validation;
		public List<Error> errores = new ArrayList<Error>();
		public InfoMD(String _type, String _title, String _identifier, String _validation){
			type = _type; title = _title; identifier = _identifier; validation = _validation;
		}
	}
	private class Error{
		int a = 10;
		@Override
		public int hashCode() {return a;}
		public String type, text, clase;
		public Error(String _type, String _text, String _clase){
			type = _type; text =_text; clase =_clase;
		}
		
		@Override
		public boolean equals(Object obj) {
		      if (getClass() != obj.getClass() || obj == null){
		         return false;
		      }
		      return (type.equals(((Error) obj).type));		      
		}
	}
	
	/*********************************************************/
	// propiedades del tasklet

	public void setQualityReportOutputFile(String qualityReportOutputFile) {
		this.qualityReportOutputFile = qualityReportOutputFile;
	}

	public void setQualityResultRDFFile(String qualityResultRDFFile) {
		this.qualityResultRDFFile = qualityResultRDFFile;
	}

}
