import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import {HttpClientModule} from '@angular/common/http';

import { AppComponent } from './app.component';
import { ResultsComponent } from './results/results.component';
import {AppRoutingModule} from "./app-routing.module";
import { EvaluationComponent } from './evaluation/evaluation.component';

@NgModule({
  declarations: [
    AppComponent,
    ResultsComponent,
    EvaluationComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
