import { Component, OnInit } from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {apiPaths, environment, GlobalVariables} from '../../environments/environment';
import {EvaluationStarted} from "../app.component";

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
  isEvaluationStarted: EvaluationStarted = {
    evaluationStarted: false
  }

  days = -1;

  constructor(private http: HttpClient, public GlobalVariables: GlobalVariables) { }

  ngOnInit(): void {
    this.GlobalVariables.sharedMessageIsAdminLoggedIn.subscribe( messageIsAdminLoggedIn => this.isAdminLoggedIn = messageIsAdminLoggedIn);
  }

  getForm(mqa: HTMLInputElement, iso19157: HTMLInputElement, sparql: HTMLInputElement, ckan: HTMLInputElement,
          nti: HTMLInputElement, dcatAp: HTMLInputElement, direct: HTMLInputElement, local: HTMLInputElement,
          url: HTMLInputElement, days: number): void {

    if (!this.periodicityIsDisabled && (days <= 0)) {
      this.periodicityIsNotANumber = true
    } else {
      this.periodicityIsNotANumber = false
      //If more than one evaluation is submitted without reloading, days is not reset to -1
      // if only the check is disabled
      if (this.periodicityIsDisabled) {
        days = -1
      }
      this.evaluate(mqa.checked, iso19157.checked, sparql.checked, ckan.checked, nti.checked,
      dcatAp.checked, direct.checked, local.checked, url.value, days);
    }
    console.log('mqa: ' + mqa.checked)
    console.log('iso19157: ' + iso19157.checked)
    console.log('sparql: ' + sparql.checked)
    console.log('ckan: ' + ckan.checked)
    console.log('nti: ' + nti.checked)
    console.log('dcatAp: ' + dcatAp.checked)
    console.log('direct: ' + direct.checked)
    console.log('local: ' + local.checked)
    console.log('URL: ' + url.value)
    console.log('Days: ' + days)
  }

  evaluate(mqa: boolean, iso19157: boolean, sparql: boolean, ckan: boolean,
           nti: boolean, dcatAp: boolean, direct: boolean, local: boolean,
           url: string, days: number) {
    const params = new HttpParams()
      .set('mqa', mqa)
      .set('iso19157', iso19157)
      .set('sparql', sparql)
      .set('ckan', ckan)
      .set('nti', nti)
      .set('dcatAp', dcatAp)
      .set('direct', direct)
      .set('local', local)
      .set('days', days)
      .set('url', url)

    this.http.get<EvaluationStarted>(this.baseUrl + apiPaths.evaluate, {params: params}).subscribe(
      (resp: EvaluationStarted) => {
        this.isEvaluationStarted = resp
        console.log(this.isEvaluationStarted.evaluationStarted)
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
