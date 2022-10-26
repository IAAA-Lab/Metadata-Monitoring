// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
import { Injectable } from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {HttpClient, HttpParams} from '@angular/common/http';

export const environment = {
  production: false,
  baseUrl: "http://localhost:3000"
};

export enum apiPaths {
  evaluate = "/evaluate",
  login = "/login"
}

@Injectable({
  providedIn: 'root'
})
export class GlobalVariables {
  isAdminLoggedIn = false

  private messageIsAdminLoggedIn = new BehaviorSubject(this.isAdminLoggedIn);
  sharedMessageIsAdminLoggedIn = this.messageIsAdminLoggedIn.asObservable();

  nextMessageIsAdminLoggedIn(message: boolean) {
    this.messageIsAdminLoggedIn.next(message);
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
