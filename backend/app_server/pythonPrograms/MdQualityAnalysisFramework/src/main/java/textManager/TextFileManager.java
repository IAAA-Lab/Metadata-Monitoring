package textManager;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.util.List;
import java.util.Scanner;

/**
 * contiene metodos que facilitan la lectura y escritura de texto en ficheros
 * es funcionalidad se usa amenudo y asi no esta multiplicada nveces
 */
public class TextFileManager {
	
	// Variable que codifica el encidng utf8
	private static final String encodingUTF8 = "UTF-8";
	private static final String newLine = System.getProperty("line.separator");
	
	/*********************************************************************************/
	/**
	 * lee un fichero de texto en utf-8
	 */
	public static String loadTextFile(String filePath) {
		 try {
			 Scanner scanner = new Scanner(new FileInputStream(filePath), encodingUTF8);	
			 StringBuilder textB = new StringBuilder();
		     while (scanner.hasNextLine()){
		        textB.append(scanner.nextLine() + newLine);
		     }		    
		     scanner.close();
		     return textB.toString();
		 }catch (Exception e) {
				System.out.println("-->> Error al leer el fichero: " + filePath);
				e.printStackTrace();
				throw new RuntimeException();
		}
	}
	
	/*********************************************************************************/
	/**
	 * Guarda un fichero de texto en utf-8
	 */
	public static void saveTextFile(String filePath, String fileContent) {
		try {
			File f = new File(filePath);
			f.getParentFile().mkdirs();
			FileOutputStream fos = new FileOutputStream(filePath);
			OutputStreamWriter osw = new OutputStreamWriter(fos, encodingUTF8);
			osw.write(fileContent); osw.flush(); osw.close();
		} catch (Exception e) {
			System.out.println("-->> Error al guardar el fichero: " + filePath);
			e.printStackTrace();
			throw new RuntimeException();
		}
	}
	public static void saveTextFile(File f, String fileContent) {
		try {			
			f.getParentFile().mkdirs();
			FileOutputStream fos = new FileOutputStream(f);
			OutputStreamWriter osw = new OutputStreamWriter(fos, encodingUTF8);
			osw.write(fileContent); osw.flush(); osw.close();
		} catch (Exception e) {
			System.out.println("-->> Error al guardar el fichero: " + f.getName());
			e.printStackTrace();
			throw new RuntimeException();
		}
	}
	
	/*********************************************************************************/
	/**
	 * Guarda na lista de strings en un fichero de texto en utf-8
	 */
	public static void saveTextFile(String filePath, List<String> fileContent) {
		try {
			FileOutputStream fos = new FileOutputStream(filePath);
			OutputStreamWriter osw = new OutputStreamWriter(fos, encodingUTF8);
			for(String text:fileContent){
				osw.write(text+newLine);
			}
			osw.flush(); osw.close();
		} catch (Exception e) {
			System.out.println("-->> Error al guardar el fichero: " + filePath);
			e.printStackTrace();
			throw new RuntimeException();
		}
	}
	
}
