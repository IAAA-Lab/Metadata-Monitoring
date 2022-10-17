import { Component, OnInit } from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import { Router } from '@angular/router';
import {environment, apiPaths, GlobalVariables} from "../../environments/environment";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})

export class LoginComponent implements OnInit {
  baseUrl = environment.baseUrl;

  username: string = '';
  password: string = '';
  error: boolean = false;
  emptyError: boolean = false;

  constructor(private http: HttpClient, private router: Router, public GlobalVariables: GlobalVariables) { }

  ngOnInit(): void {
  }


  logIn() {
    //reset variables to update the value in html properly
    this.error = false
    this.emptyError = false

    const user = {
      username: this.username,
      password: this.password
    }

    this.http.post(this.baseUrl + apiPaths.login, user, {observe : 'response'}).subscribe(
      (resp: any) => {
        //user is set as logged in
        this.GlobalVariables.nextMessageIsAdminLoggedIn(true)
        this.backToEvaluation()
      }, (error: any) => {
        if (error.status == 401) {
          this.error = true;
        } else {
          this.emptyError = true
        }
      }
    )
  }

  backToEvaluation() {
    this.router.navigate(['evaluation']);
  }
}
