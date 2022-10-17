import { Component, OnInit } from '@angular/core';
import {HttpClient, HttpParams} from "@angular/common/http";
import {apiPaths, environment, GlobalVariables} from "../../environments/environment";

@Component({
  selector: 'app-evaluation',
  templateUrl: './evaluation.component.html',
  styleUrls: ['./evaluation.component.css']
})
export class EvaluationComponent implements OnInit {
  baseUrl = environment.baseUrl;

  localEvaluationIsChecked = false
  directEvaluationIsChecked = false
  directEvaluationIsDisabled = false
  forceUncheckDirectEvaluation = false

  displayFilters = false
  periodicityIsNotANumber = false
  periodicityIsDisabled = true
  isAdminLoggedIn: boolean | undefined

  days = -1;

  constructor(private http: HttpClient, public GlobalVariables: GlobalVariables) { }

  ngOnInit(): void {
    this.GlobalVariables.sharedMessageIsAdminLoggedIn.subscribe( messageIsAdminLoggedIn => this.isAdminLoggedIn = messageIsAdminLoggedIn);
  }

  getForm(mqa: HTMLInputElement, iso19157: HTMLInputElement, sparql: HTMLInputElement, ckan: HTMLInputElement,
          nti: HTMLInputElement, dcat_ap: HTMLInputElement, direct: HTMLInputElement, local: HTMLInputElement,
          url: HTMLInputElement, days: number): void {
    console.log("mqa: " + mqa.checked)
    console.log("iso19157: " + iso19157.checked)
    console.log("sparql: " + sparql.checked)
    console.log("ckan: " + ckan.checked)
    console.log("nti: " + nti.checked)
    console.log("dcat_ap: " + dcat_ap.checked)
    console.log("direct: " + direct.checked)
    console.log("local: " + local.checked)
    console.log("URL: " + url.value)
    console.log("Days: " + days)

    if (!this.periodicityIsDisabled && (days <= 0)) {
      this.periodicityIsNotANumber = true
    } else {
      this.periodicityIsNotANumber = false
      this.evaluate(url)
    }
  }

  evaluate(url: HTMLInputElement) {

    const params = new HttpParams()
      .set("url", url.value)

    //TODO: comprobar si hay error sacar ventanita y si no lo hay, diciendo que todo correcto que ya aparecerá en los resultados
    this.http.get(this.baseUrl + apiPaths.mqa_sparql, {params: params, responseType: "text"}).subscribe(
      (resp: string) => {
        console.log(resp)
      }
    )

  }

  checkDirectEvaluation () {
    this.localEvaluationIsChecked = false
    this.directEvaluationIsChecked = true
  }
  checkLocalEvaluation () {
    this.localEvaluationIsChecked = true
    this.directEvaluationIsChecked = false
  }

  disableDirectEvaluation () {
    this.directEvaluationIsDisabled = true
    this.checkLocalEvaluation()
  }

  activateDirectEvaluation () {
    this.directEvaluationIsDisabled = false
    this.localEvaluationIsChecked = false
    this.forceUncheckDirectEvaluation = false
  }

  openFilters() {
    this.displayFilters = true
  }

  closeFilters() {
    this.displayFilters = false
  }

  togglePeriodicity() {
    this.periodicityIsDisabled = !this.periodicityIsDisabled
  }
}
