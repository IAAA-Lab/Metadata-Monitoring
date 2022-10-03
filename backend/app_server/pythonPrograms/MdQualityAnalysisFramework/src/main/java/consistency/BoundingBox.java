package consistency;

/**
 * Created by jnog on 21/08/17.
 */
public class BoundingBox {
    private double _westBoundLongitude;
    private double _eastBoundLongitude;
    private double _northBoundLatitude;
    private double _southBoundLatitude;

    public BoundingBox (double westBoundLongitude, double eastBoundLongitude, double northBoundLatitude, double southBoundLatitude) {
        _westBoundLongitude=westBoundLongitude;
        _eastBoundLongitude=eastBoundLongitude;
        _northBoundLatitude=northBoundLatitude;
        _southBoundLatitude=southBoundLatitude;

    }

    public boolean overlap(BoundingBox bbox) {
        return bbox._westBoundLongitude <= this._eastBoundLongitude
                && bbox._eastBoundLongitude>= this._westBoundLongitude
                && bbox._southBoundLatitude <= this._northBoundLatitude
                && bbox._northBoundLatitude >= this._southBoundLatitude;
    }

    public boolean compatible(BoundingBox bbox) {
        return overlap(bbox);
    }

    public static boolean checkCompatibility(BoundingBox[] bboxes) {
        for (int i=0; i<bboxes.length; i++)
            for (int j=i+1; j < bboxes.length; j++)
                if (!bboxes[i].compatible(bboxes[j]))
                    return false;
        return true;
    }

    private static boolean isLatitude (double latitude) {
        return latitude >= -90.0 && latitude <=90.0;
    }

    private static boolean isLongitude (double longitude) {
        return longitude >= -180.0 && longitude <=180.0;
    }

    public boolean hasGeographicCoordinates() {
       return isLatitude(_northBoundLatitude)
               && isLatitude(_southBoundLatitude)
               && isLongitude(_eastBoundLongitude)
               && isLongitude(_westBoundLongitude);
    }

    public static boolean checkGeographicCoordinates(BoundingBox[] bboxes) {
        for (BoundingBox bbox: bboxes)
          if (!bbox.hasGeographicCoordinates())
              return false;
        return true;
    }

    public String toString() {
        return "west: "+_westBoundLongitude+ " east: "+_eastBoundLongitude + " south "+_southBoundLatitude+" north "+_northBoundLatitude;
    }

    public static String toString(BoundingBox[] bboxes) {
        String result ="";
        for (BoundingBox bbox:bboxes)
            result +="\n"+bbox;
        return result;
    }
}
