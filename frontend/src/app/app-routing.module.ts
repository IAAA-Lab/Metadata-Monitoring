import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ResultsComponent } from './results/results.component';
import { EvaluationComponent } from "./evaluation/evaluation.component";
import { LoginComponent } from './login/login.component';


const routes: Routes = [
  { path: 'evaluation', component: EvaluationComponent },
  { path: 'results', component: ResultsComponent },
  { path: 'login', component: LoginComponent },
  { path: '**', redirectTo: "/evaluation"}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})

export class AppRoutingModule  { }
