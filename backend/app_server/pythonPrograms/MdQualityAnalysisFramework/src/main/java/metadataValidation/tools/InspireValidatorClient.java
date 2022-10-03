package metadataValidation.tools;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URL;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.mime.MultipartEntity;
import org.apache.http.entity.mime.content.StringBody;
import org.apache.http.impl.client.DefaultHttpClient;

/*
 * Simple Java Client for the INSPIRE Geoportal Validator
 */
@SuppressWarnings("deprecation")
public class InspireValidatorClient {

	private URL inspireResourceTesterURL;

	/**
	 * Constructor, sele pasa la url del servicio a valiad
	 */
	public InspireValidatorClient(URL inspireResourceTesterURL) {
		this.inspireResourceTesterURL = inspireResourceTesterURL;

	}

	/*************************************************************/
	/**
	 * Manda una solicitud de validación de un metadato como texto al servicio indicado en el constructor
	 */
	public HttpResponse validate(String resourceDescriptorText) throws UnsupportedEncodingException {
		HttpResponse retVal = null;

		@SuppressWarnings("resource")
		HttpClient httpClient = new DefaultHttpClient();
		HttpPost httpPost = new HttpPost(this.inspireResourceTesterURL.toString());
		// HttpPost httpPost = new
		// HttpPost("http://localhost:9998/INSPIREResourceTester");

		httpPost.addHeader("Accept", "application/xml");

		MultipartEntity reqEntity = new MultipartEntity();

		if (resourceDescriptorText != null) {
			StringBody stringPart = new StringBody(resourceDescriptorText);
			reqEntity.addPart("resourceRepresentation", stringPart);
		}

		httpPost.setEntity(reqEntity);

		try {
			retVal = httpClient.execute(httpPost);
		} catch (ClientProtocolException ex) {
			System.out.println(ex.getMessage());
		} catch (IOException ex) {
			System.out.println(ex.getMessage());
		}
		return retVal;
	}

	/*************************************************************/
	/**
	 * convierte la respuesta del servicio del validador eun una cadena de texto
	 */
	public String getValidation(HttpResponse validatorResponse) throws Exception {
		String res = null;
		int responseStatusCode = validatorResponse.getStatusLine().getStatusCode();
		if (responseStatusCode == 201) {
			String resultUrl = validatorResponse.getHeaders("Location")[0].getValue();
			if (resultUrl.endsWith("resourceReport")) {
				return org.apache.commons.io.IOUtils.toString(validatorResponse.getEntity().getContent(), "UTF-8");
			}
		}
		return res;
	}
}