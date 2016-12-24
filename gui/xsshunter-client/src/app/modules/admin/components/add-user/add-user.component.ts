import { Component, OnInit } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';

import { UserService } from '../../services/user.service';
import { EmailAddressValidators, PasswordValidators } from '../../../../shared/validators';
import { environment } from '../../../../../environments/environment';


@Component({
  selector: 'admin-add-user',
  templateUrl: './add-user.component.html',
  providers: [FormBuilder],
  styleUrls: ['./add-user.component.css'],
})
export class AddUserComponent implements OnInit {

  private _addUserForm: FormGroup;
  private _teams: any;

  constructor(private _router: Router,
              private _userService: UserService,
              private _fb: FormBuilder) { }

  ngOnInit() {

    this._userService.getTeams().subscribe(
      teams => {
        this._teams = teams;
      });

    this._addUserForm = this._fb.group({
      name: ['', Validators.compose([
        Validators.required,
        Validators.minLength(environment.minUserNameLength),
        Validators.maxLength(environment.maxUserNameLength)
      ])],
      email_address: ['', Validators.compose([
        Validators.required,
        EmailAddressValidators.isInvalidEmail,
      ])],
      password: ['', Validators.compose([
        Validators.required,
        Validators.minLength(environment.minPasswordLength),
        PasswordValidators.hasLowerCase,
        PasswordValidators.hasUpperCase,
        PasswordValidators.hasDigit,
        PasswordValidators.hasSymbol
      ])],
      confirm_password: ['', Validators.required],
      team_id: [''],
      is_admin: false,
      is_team_manager: false,
    });

  }

  addUserAttempt(value: any) {
    console.log(value);
    if (value.team_name !== '') {
      if (value.password === value.confirm_password) {
        this._userService.addUser(value).subscribe(
          resp => {
            this._router.navigate(['/admin/users']);
          },
          err => {
            this._addUserForm.setErrors({ failedToCreatUser: true });
          });
      } else { 
        this._addUserForm.setErrors({ confirmPasswordMismatch: true });
      }
    } else {
      this._addUserForm.setErrors({ invalidTeamSelection: true });
    }
  }

}
