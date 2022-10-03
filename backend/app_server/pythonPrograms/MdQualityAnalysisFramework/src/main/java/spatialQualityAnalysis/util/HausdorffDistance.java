package spatialQualityAnalysis.util;

import java.awt.geom.Rectangle2D;

import org.six11.util.pen.Pt;

/**
 * Hausdorff spatial similarity function, taken from
 * http://www.alexandria.ucsb.edu/~gjanee/archive/2003/similarity.html
 **/

public class HausdorffDistance {

	private static class Box {
		Pt min, max;

		Box(Pt min, Pt max) {
			this.min = min;
			this.max = max;
		}
	}

	public static double getHausdorffDistanceW(Rectangle2D rectA, Rectangle2D rectB) {
		Pt min = new Pt(rectA.getX(), rectA.getY());
		Pt max = new Pt(rectA.getX() + rectA.getWidth(), rectA.getY() + rectA.getHeight());
		Box p = new Box(min, max);
		min = new Pt(rectB.getX(), rectB.getY());
		max = new Pt(rectB.getX() + rectB.getWidth(), rectB.getY() + rectB.getHeight());
		Box q = new Box(min, max);

		return Math.max(h(p, q), h(q, p));
	}

	static double h(Box p, Box q) {
		// I probably could do something with Collections.min() as well
		double a = dist(new Pt(p.min.getX(), p.min.getY()), q);
		double b = dist(new Pt(p.min.getX(), p.max.getY()), q);
		double c = dist(new Pt(p.max.getX(), p.min.getY()), q);
		double d = dist(new Pt(p.max.getX(), p.max.getY()), q);
		double e = Math.max(a, b);
		double f = Math.max(c, d);
		return Math.max(e, f);
	}

	static double dist(Pt p, Box Q) {
		Pt q = new Pt(Math.min(Math.max(p.getX(), Q.min.getX()), Q.max.getX()),
				Math.min(Math.max(p.getY(), Q.min.getY()), Q.max.getY()));
		return Math.sqrt((p.getX() - q.getX()) * (p.getX() - q.getX()) + (p.getY() - q.getY()) * (p.getY() - q.getY()));
	}
}