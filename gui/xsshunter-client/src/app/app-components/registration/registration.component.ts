import { Component, OnInit, style, state, animate, transition, trigger } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';

import { RegistrationService } from '../../services/registration.service';
import { EmailAddressValidators, PasswordValidators, SubdomainValidators } from '../../shared/validators';
import { environment } from '../../../environments/environment';


@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrls: ['./registration.component.css'],
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
export class RegistrationComponent implements OnInit {

  private _newUserForm: FormGroup;
  private _recaptcha;
  private _submitted = false;
  private _errorMessage: string;

  constructor(private _router: Router,
              private _registrationService: RegistrationService,
              private _fb: FormBuilder) { }

  ngOnInit() {
    this._newUserForm = this._fb.group({
      username: ['', Validators.compose([
        Validators.required,
        Validators.minLength(environment.minUsernameLength),
        Validators.maxLength(environment.maxUsernameLength)
      ])],
      subdomain: ['', Validators.compose([
        Validators.required,
        SubdomainValidators.isInvalidSubdomain
      ])],
      email: ['', Validators.compose([
        Validators.required,
        EmailAddressValidators.isInvalidEmail,
      ])],
      password: ['', Validators.compose([
        Validators.required,
        Validators.minLength(environment.minPasswordLength)
      ])],
      confirm_password: ['', Validators.required],
    });
  }

  private _getMinPasswordLength() {
    return environment.minPasswordLength;
  }

  private _getMinUsernameLength() {
    return environment.minUsernameLength;
  }

  private _setRecaptcha(recaptcha) {
    this._recaptcha = recaptcha;
  }

  private _createNewUserAttempt(values: any) {
    if (!this._recaptcha) {
      this._newUserForm.setErrors({ captchaRequired: true });
      return;
    }
    this._submitted = true;
    values.recaptcha = this._recaptcha;
    this._registrationService.createNewUser(values).subscribe(
      user => {
        this._submitted = false;
        this._router.navigate(['/login']);
      },
      resp => {
        this._submitted = false;
        this._errorMessage = resp.json().error;
      });
  }
}
