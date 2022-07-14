import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'metadata-monitoring';


  getForm(mqa: HTMLInputElement, iso19157: HTMLInputElement, sparql: HTMLInputElement, ckan: HTMLInputElement,
          nti: HTMLInputElement, dcat_ap: HTMLInputElement, direct: HTMLInputElement, local: HTMLInputElement): void {
    console.log("mqa: " + mqa.checked)
    console.log("iso19157: " + iso19157.checked)
    console.log("sparql: " + sparql.checked)
    console.log("ckan: " + ckan.checked)
    console.log("nti: " + nti.checked)
    console.log("dcat_ap: " + dcat_ap.checked)
    console.log("direct: " + direct.checked)
    console.log("local: " + local.checked)
  }
}
