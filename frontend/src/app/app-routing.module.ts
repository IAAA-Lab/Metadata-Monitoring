import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ResultsComponent } from './results/results.component';
import {EvaluationComponent} from "./evaluation/evaluation.component";

const routes: Routes = [
  { path: 'evaluation', component: EvaluationComponent },
  { path: 'results', component: ResultsComponent },
  { path: '**', redirectTo: "/evaluation"}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})

export class AppRoutingModule  { }
