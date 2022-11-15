// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
import { Injectable } from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Analysis_ISO19157, Analysis_MQA, Properties_ISO19157, Properties_MQA} from "../app/app.component";

export const environment = {
  production: false,
  baseUrl: "http://localhost:3000"
};

export enum apiPaths {
  evaluate = "/evaluate",
  login = "/login",
  results = "/results",
  export_data = "/results/export",
  analysis = "/results/analysis"
}

@Injectable({
  providedIn: 'root'
})
export class GlobalVariables {
  isAdminLoggedIn = false

  analysisISO19157: Analysis_ISO19157 = {
    properties: new Array<Properties_ISO19157>()
  };
  analysisMQA: Analysis_MQA = {
    properties: new Array<Properties_MQA>()
  };

  Date: string = '';
  URL: string = '';

  private messageIsAdminLoggedIn = new BehaviorSubject(this.isAdminLoggedIn);
  sharedMessageIsAdminLoggedIn = this.messageIsAdminLoggedIn.asObservable();

  private messageAnalysisISO19157 = new BehaviorSubject(this.analysisISO19157);
  sharedMessageAnalysisISO19157 = this.messageAnalysisISO19157.asObservable();

  private messageAnalysisMQA = new BehaviorSubject(this.analysisMQA);
  sharedMessageAnalysisMQA = this.messageAnalysisMQA.asObservable();

  private messageDate = new BehaviorSubject(this.Date);
  sharedMessageDate = this.messageDate.asObservable();

  private messageURL = new BehaviorSubject(this.URL);
  sharedMessageURL = this.messageURL.asObservable();

  nextMessageIsAdminLoggedIn(message: boolean) {
    this.messageIsAdminLoggedIn.next(message);
  }

  nextMessageAnalysisISO19157(message: Analysis_ISO19157) {
    this.messageAnalysisISO19157.next(message);
  }

  nextMessageAnalysisMQA(message: Analysis_MQA) {
    this.messageAnalysisMQA.next(message);
  }

  nextMessageDate(message: string) {
    this.messageDate.next(message);
  }

  nextMessageURL(message: string) {
    this.messageURL.next(message);
  }
}

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/plugins/zone-error';  // Included with Angular CLI.
