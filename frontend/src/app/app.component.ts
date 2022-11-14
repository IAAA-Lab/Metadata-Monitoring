import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {}

export class ResultsIndex {
  URL: string = '';
  Date: string = '';
  Method: string = '';
}

export class Properties_ISO19157 {
  Dimension: string = '';
  Entity: string = '';
  Property: string = '';
  Count: number = 0;
  Population: number = 0;
  Percentage: number = 0;
  Pass: boolean = false;
}

export class Properties_MQA {
  Dimension: string = '';
  Indicator_property: string = '';
  Count: number = 0
  Population: number = 0;
  Percentage: number = 0;
  Points: number = 0;
}

export class Analysis_ISO19157 {
  properties: Properties_ISO19157[] = []
}

export class Analysis_MQA {
  properties: Properties_MQA[] = []
}
