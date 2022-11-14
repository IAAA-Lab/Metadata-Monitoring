import { Component, OnInit } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {GlobalVariables} from '../../environments/environment';
import {Analysis_ISO19157, Analysis_MQA, Properties_ISO19157, Properties_MQA} from '../app.component';
import {Chart, ChartDataset} from 'chart.js';

@Component({
  selector: 'app-analysis',
  templateUrl: './analysis.component.html',
  styleUrls: ['./analysis.component.css']
})
export class AnalysisComponent implements OnInit{
  public chart: any;

  messageAnalysisMQA: Analysis_MQA = {
    properties: []
  };

  messageAnalysisISO19157: Analysis_ISO19157 = {
    properties: []
  };

  method = '';

  constructor(public GlobalVariables: GlobalVariables) { }

  ngOnInit(): void {
    this.GlobalVariables.sharedMessageAnalysisMQA.subscribe( messageAnalysisMQA => this.messageAnalysisMQA = messageAnalysisMQA);
    this.GlobalVariables.sharedMessageAnalysisISO19157.subscribe( messageAnalysisISO19157 => this.messageAnalysisISO19157 = messageAnalysisISO19157);
    this.drawGraphs()
  }
  drawGraphs() {
    let ISO19157Properties = this.messageAnalysisISO19157.properties
    let MQAProperties = this.messageAnalysisMQA.properties
    let ISO19157Length = ISO19157Properties.length
    let MQALength = MQAProperties.length
    let labels: string[] = []
    let data: string[] = []
    let colors: string[] = []

    //Mágia negra para sacar 3 decimales en la gráfica sin redondear
    let re = new RegExp('^-?\\d+(?:\.\\d{0,' + (3 || -1) + '})?');

    if (ISO19157Length != 0) {
      this.method = 'ISO19157'
      for (let i = 0; i < ISO19157Length; i++) {
        if (ISO19157Properties[i].Property == 'None') {
          labels.push(ISO19157Properties[i].Dimension + ' - ' + ISO19157Properties[i].Entity);
        } else {
          labels.push(ISO19157Properties[i].Dimension + ' - ' + ISO19157Properties[i].Entity + ' - '
            + ISO19157Properties[i].Property);
        }
        // @ts-ignore
        data.push(ISO19157Properties[i].Percentage.toString().match(re)[0])
        if (ISO19157Properties[i].Pass) {
          colors.push('green');
        } else {
          colors.push('red')
        }
      }

    } else if (MQALength != 0) {
      this.method = 'MQA'
      for (let i = 0; i < MQALength; i++) {
          labels.push(MQAProperties[i].Dimension + ' - ' + MQAProperties[i].Indicator_property);
        // @ts-ignore
        data.push(MQAProperties[i].Percentage.toString().match(re)[0])
        colors.push('blue')
      }
    }
    this.createChart(labels, data, colors)
  }
  // labels: string[], datasetLabel: string, data: string
  createChart(labels: string[], dataValues: string[], colors: string[]){
    this.chart = new Chart("MyChart", {
      type: 'bar', //this denotes tha type of chart

      data: {// values on X-Axis
        labels: labels,
        datasets: [
          {
            label: "Sales",
            data: dataValues,
            backgroundColor: colors
          }
        ]
      },
      options: {
        aspectRatio:2.5
      }
    });
  }

}

