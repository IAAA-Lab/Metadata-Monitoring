package consistency;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

/**
 * Created by jnog on 21/08/17.
 * It compares the bounding box geographic extent and the geographic scope of data quality
 */
public class BoundingBoxTopologicalConsistencyChecker {
    private static final String _SOUTHTAG="gmd:southBoundLatitude";
    private static final String _NORTHTAG="gmd:northBoundLatitude";
    private static final String _WESTTAG="gmd:westBoundLongitude";
    private static final String _EASTTAG="gmd:eastBoundLongitude";
    private static final String _DECIMALTAG="gco:Decimal";
    private static final String _SCOPETAG="gmd:DQ_Scope";
    private static final String _BOUNDINGBOXTAG="gmd:EX_GeographicBoundingBox";
    private static final String _BOUNDINGPOLYGONTAG="gmd:EX_BoundingPolygon";

    private static int multipleBoundingBox = 0;
    private static int multipleBoundingPolygon = 0;
    private static int multipleBoundingBoxErrorCount = 0;

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

    public static void findBoundingPolygonFromFile(String inputFileName) throws Exception {

        File inputFile = new File(inputFileName);

        if (inputFile.exists() && inputFile.isFile()) {
            DocumentBuilderFactory domFactory = DocumentBuilderFactory.newInstance();
//			  domFactory.setNamespaceAware(false); // false es con namesapace
            DocumentBuilder builder = domFactory.newDocumentBuilder();

//			System.out.println(inputFile.toURI().toString());
            Document xmlDoc = builder.parse(inputFile.toURI().toString());
            // Document xmlDoc = builder.parse(inputFile);

            NodeList list = xmlDoc.getElementsByTagName(_BOUNDINGPOLYGONTAG);
            String fileIdentifier = null;
            String parentIdentifier = null;
            Node metadataNode =null;

            if (list.getLength()>1) {
                System.out.println(inputFileName);
                multipleBoundingPolygon++;
            }


        }


    }

    public static void findBoundingPolygon(String inputFolderName) throws Exception {
//		System.out.println("Folder: "+inputFolderName);
        File inputFolder = new File(inputFolderName);

        identifierMap = new HashMap<String,String>();

        if (inputFolder.exists()&& inputFolder.isDirectory()) {

            String[] files = inputFolder.list();

            System.out.println(files.length + " files");

            for (String fileName: files) {
                findBoundingPolygonFromFile(inputFolderName+"/"+fileName);

            }
            System.out.println(multipleBoundingPolygon + " files with more than one bounding polygon");

        }


    }

    public static void findBoundingBoxFromFile(String inputFileName) throws Exception {

        File inputFile = new File(inputFileName);

        if (inputFile.exists() && inputFile.isFile()) {
            DocumentBuilderFactory domFactory = DocumentBuilderFactory.newInstance();
//			  domFactory.setNamespaceAware(false); // false es con namesapace
            DocumentBuilder builder = domFactory.newDocumentBuilder();

//			System.out.println(inputFile.toURI().toString());
            Document xmlDoc = builder.parse(inputFile.toURI().toString());
            // Document xmlDoc = builder.parse(inputFile);

            NodeList list = xmlDoc.getElementsByTagName(_BOUNDINGBOXTAG);
            String fileIdentifier = null;
            String parentIdentifier = null;
            Node metadataNode =null;

            if (list.getLength()>1) {

                BoundingBox[] bboxes = new BoundingBox[list.getLength()];
                boolean containsDQScope=false;
                for (int i = 0; i < list.getLength(); i++) {
//				  System.out.println("Entro 1");
                    Node boxNode = list.item(i);

                    if (boxNode.getParentNode().getParentNode().getParentNode().getParentNode().getNodeName().equals(_SCOPETAG))
                        containsDQScope=true;

                    bboxes[i]= extractBoundingBox(boxNode);
                }

                if (BoundingBox.checkGeographicCoordinates(bboxes)&&containsDQScope) {
                    multipleBoundingBox++;
                    if (!BoundingBox.checkCompatibility(bboxes)) {
                        System.out.println("Error: "+inputFileName + BoundingBox.toString(bboxes));

                        multipleBoundingBoxErrorCount++;

                    }
                    else {
                        System.out.println("Correct: "+inputFileName + BoundingBox.toString(bboxes));
                    }
                }



            }

        }


    }

    private static double extractDecimal(Node bound) {
        double result=0.0;

        NodeList boundChildren = bound.getChildNodes();
        for (int l = 0; l < boundChildren.getLength(); l++) {
            Node boundChild = boundChildren.item(l);
            if (boundChild.getNodeName().equals(_DECIMALTAG)) {
                result = Double.parseDouble(boundChild.getTextContent());
            }
        }
        return result;

    }

    private static BoundingBox extractBoundingBox (Node boxNode) {

        double north=0.0, south=0.0, east=0.0, west=0.0;

        NodeList bboxChildren = boxNode.getChildNodes();
        for (int j = 0; j < bboxChildren.getLength(); j++) {
            Node bboxChild = bboxChildren.item(j);
            if (bboxChild.getNodeName().equals(_NORTHTAG))
                north = extractDecimal(bboxChild);
            else if (bboxChild.getNodeName().equals(_SOUTHTAG))
                south = extractDecimal(bboxChild);
            else if (bboxChild.getNodeName().equals(_WESTTAG))
                west = extractDecimal(bboxChild);
            else if (bboxChild.getNodeName().equals(_EASTTAG))
                east = extractDecimal(bboxChild);
        }

        return new BoundingBox(west,east,north,south);
    }

    public static void findBoundingBox(String inputFolderName) throws Exception {
//		System.out.println("Folder: "+inputFolderName);
        File inputFolder = new File(inputFolderName);

        identifierMap = new HashMap<String,String>();

        if (inputFolder.exists()&& inputFolder.isDirectory()) {

            String[] files = inputFolder.list();

            System.out.println(files.length + " files");

            for (String fileName: files) {
                findBoundingBoxFromFile(inputFolderName+"/"+fileName);

            }
            System.out.println(multipleBoundingBox + " files with more than one bounding box");
            System.out.println(multipleBoundingBoxErrorCount + " files with errors");

        }


    }


    public static void main(String[] args) {
        try {


            //findBoundingPolygon("Metadatos20160902");
            findBoundingBox("Metadatos20160902");
            //checkIdentifiers();

        } catch(Exception ex) {
            ex.printStackTrace();
        }
    }

}
