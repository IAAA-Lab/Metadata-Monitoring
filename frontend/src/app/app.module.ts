import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import {HttpClientModule} from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { tap } from 'rxjs/operators';
import { AppComponent } from './app.component';
import { ResultsComponent } from './results/results.component';
import {AppRoutingModule} from "./app-routing.module";
import { EvaluationComponent } from './evaluation/evaluation.component';
import { LoginComponent } from './login/login.component';

@NgModule({
  declarations: [
    AppComponent,
    ResultsComponent,
    EvaluationComponent,
    LoginComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
