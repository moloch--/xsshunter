import { Component, OnInit, style, state, animate, transition, trigger } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';

import { HttpClientService } from '../../core-services/http-client.service';
import { OtpValidators } from '../../shared/validators';


@Component({
  selector: 'login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  providers: [FormBuilder],
  animations: [
    trigger('fadeInOut', [
      transition(':enter', [   // :enter is alias to 'void => *'
        style({opacity:0}),
        animate(400, style({opacity:1})) 
      ]),
      transition(':leave', [   // :leave is alias to '* => void'
        animate(400, style({opacity:0})) 
      ])
    ])
  ]
})
export class LoginComponent implements OnInit {

  private _loginForm: FormGroup;
  private _invalidLogin = false;
 
  constructor(private _router: Router,
              private _http: HttpClientService,
              private _fb: FormBuilder) { }

  ngOnInit() {
    
    if (this._http.session.isAuthenticated()) {
      this._router.navigate(['/home']);
    }
    
    this._loginForm = this._fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required],
      otp: ['', OtpValidators.isInvalidOtp]
    });

  }

  loginAttempt(value: any): void {
    this._http.createSession(value).then(resp => {
      console.log("[LoginFormComponent] Login success");
      this._router.navigate(['/home']);
    }).catch(err => {
      console.log("[LoginFormComponent] Invalid username or password");
      this._invalidLogin = true;
    });
  }

}
