import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

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
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
