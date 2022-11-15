import { Component, OnInit } from '@angular/core';
import {Chart} from 'chart.js';
import {apiPaths, environment, GlobalVariables} from "../../environments/environment";
import {HttpClient, HttpParams} from '@angular/common/http';
import {Analysis_ISO19157, Analysis_MQA, ResultsIndex} from "../app.component";
import {Router} from "@angular/router";

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.css']
})



export class ResultsComponent implements OnInit {
  baseUrl = environment.baseUrl;
  results: Array<ResultsIndex> = new Array<ResultsIndex>();

  constructor(private http: HttpClient, public GlobalVariables: GlobalVariables, private router: Router) { }

  ngOnInit(): void {
    this.http.get<[ResultsIndex]>(this.baseUrl + apiPaths.results).subscribe(
      (resp: [ResultsIndex]) => {
        this.results = resp
      }
    )
    this.GlobalVariables.nextMessageAnalysisMQA(new Analysis_MQA());
    this.GlobalVariables.nextMessageAnalysisISO19157(new Analysis_ISO19157());
  }

  getAnalysisMQA(result: ResultsIndex) {
    const params = new HttpParams()
      .set('date', result.Date)
      .set('method', result.Method)
      .set('url', result.URL)

    this.http.get<Analysis_MQA>(this.baseUrl + apiPaths.analysis, {params: params}).subscribe(
      (resp: Analysis_MQA) => {
          this.GlobalVariables.nextMessageAnalysisMQA(resp);
          this.GlobalVariables.nextMessageDate(result.Date)
          this.GlobalVariables.nextMessageURL(result.URL)
          this.goToAnalysis()
      }
    )
  }

  getAnalysisISO19157(result: ResultsIndex) {
    const params = new HttpParams()
      .set('date', result.Date)
      .set('method', result.Method)
      .set('url', result.URL)

    this.http.get<Analysis_ISO19157>(this.baseUrl + apiPaths.analysis, {params: params}).subscribe(
      (resp: Analysis_ISO19157) => {
        this.GlobalVariables.nextMessageAnalysisISO19157(resp);
        this.GlobalVariables.nextMessageDate(result.Date)
        this.GlobalVariables.nextMessageURL(result.URL)
        this.goToAnalysis()
      }
    )
  }

  goToAnalysis() {
    this.router.navigate(['analysis']);
  }
}
