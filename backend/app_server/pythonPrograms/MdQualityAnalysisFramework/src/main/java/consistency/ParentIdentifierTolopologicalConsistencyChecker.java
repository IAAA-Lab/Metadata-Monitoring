package consistency;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.File;
import java.io.FileOutputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

/**
 * Created by jnog on 19/08/17.
 * It checks whether parentIdentifier refers to an existent fileIdentifier in the metadata collection.
  */
public class ParentIdentifierTolopologicalConsistencyChecker {

    private static final String _METADATATAG="gmd:MD_Metadata";
    private static final String _IDENTIFIERTAG="gmd:fileIdentifier";
    private static final String _PARENTIDENTIFIERTAG="gmd:parentIdentifier";
    private static final String _CHARACTERTAG="gco:CharacterString";

    private static Map<String,String> identifierMap=null;

    private static String simplify(String value){
        String simplifiedValue = value.toLowerCase();
        if (simplifiedValue.endsWith(".xml")) {
            simplifiedValue= simplifiedValue.replaceFirst(".xml","");
            System.out.println("Simplify: "+value + " " + simplifiedValue);
        }
         if (simplifiedValue.isEmpty()||simplifiedValue.contains("no aplica")||simplifiedValue.contains("no se aplica"))
             simplifiedValue=null;
        return simplifiedValue;
    }

    public static void createMapFromFile(String inputFileName) throws Exception {

//		System.out.println(" file name: "+inputFileName);
        File inputFile = new File(inputFileName);

        if (inputFile.exists() && inputFile.isFile()) {
            DocumentBuilderFactory domFactory = DocumentBuilderFactory.newInstance();
//			  domFactory.setNamespaceAware(false); // false es con namesapace
            DocumentBuilder builder = domFactory.newDocumentBuilder();

//			System.out.println(inputFile.toURI().toString());
            Document xmlDoc = builder.parse(inputFile.toURI().toString());
            // Document xmlDoc = builder.parse(inputFile);

            NodeList list = xmlDoc.getElementsByTagName(_METADATATAG);
            String fileIdentifier = null;
            String parentIdentifier = null;
            Node metadataNode =null;

            for (int i = 0; i < list.getLength(); i++) {
//				  System.out.println("Entro 1");
                metadataNode = list.item(i);
                NodeList metadataChildren = metadataNode.getChildNodes();
                for (int j = 0; j < metadataChildren.getLength(); j++) {
                    Node metadataChild = metadataChildren.item(j);
                    if (metadataChild.getNodeName().equals(_IDENTIFIERTAG)) {
//					System.out.println("Entro 3");

                        NodeList fileIdentifierChildren = metadataChild.getChildNodes();
                        for (int l = 0; l < fileIdentifierChildren.getLength(); l++) {
                            Node fileIdentifierChild = fileIdentifierChildren.item(l);
                            if (fileIdentifierChild.getNodeName().equals(_CHARACTERTAG)) {
//										System.out.println("Entro 4");
                                fileIdentifier = simplify(fileIdentifierChild.getTextContent());
                            }
                        }
                    }

                    if (metadataChild.getNodeName().equals(_PARENTIDENTIFIERTAG)) {
//					System.out.println("Entro 3");

                        NodeList fileIdentifierChildren = metadataChild.getChildNodes();
                        for (int l = 0; l < fileIdentifierChildren.getLength(); l++) {
                            Node fileIdentifierChild = fileIdentifierChildren.item(l);
                            if (fileIdentifierChild.getNodeName().equals(_CHARACTERTAG)) {
//										System.out.println("Entro 4");
                                parentIdentifier = simplify(fileIdentifierChild.getTextContent());
                            }
                        }
                    }
                }

//				  System.out.println (identifier);

                if (fileIdentifier != null && metadataNode != null) {

                    //System.out.println(fileIdentifier + "\t" + parentIdentifier);

                    identifierMap.put(fileIdentifier,parentIdentifier);
                    //record.
                }

            }

        }


    }

    public static void createMap(String inputFolderName) throws Exception {
//		System.out.println("Folder: "+inputFolderName);
        File inputFolder = new File(inputFolderName);

        identifierMap = new HashMap<String,String>();

        if (inputFolder.exists()&& inputFolder.isDirectory()) {

            String[] files = inputFolder.list();

            System.out.println(files.length + " files");

            for (String fileName: files) {
                createMapFromFile(inputFolderName+"/"+fileName);

            }

        }


    }

    public static void checkIdentifiers() {
        Set<String> fileIdentifiers = identifierMap.keySet();

        int parentIdentifierCount=0;
        int errorCount=0;

        for (String fileIdentifier: fileIdentifiers) {
            String parentIdentifier = identifierMap.get(fileIdentifier);
            if (parentIdentifier!=null) {
                parentIdentifierCount++;
                if (!identifierMap.containsKey(parentIdentifier)) {
                    errorCount++;
                    System.out.println("Error\t"+fileIdentifier+"\t"+parentIdentifier);
                } else
                    System.out.println("Correct\t"+fileIdentifier+"\t"+parentIdentifier);
            }
        }
        double accuracy = (parentIdentifierCount-errorCount)*1.0/parentIdentifierCount;

        System.out.print(parentIdentifierCount +" records with parentIdentifier, "+errorCount + " errors, accuracy "+accuracy );
    }

    public static void main(String[] args) {
        try {


            createMap("Metadatos20160902");
            checkIdentifiers();

        } catch(Exception ex) {
            ex.printStackTrace();
        }
    }
}
