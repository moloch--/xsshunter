import { Component, OnInit } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';

import { environment } from '../../../environments/environment';
import { UserSettingsService } from '../../services/user-settings.service';
import { PasswordValidators, EmailAddressValidators } from '../../shared/validators';


@Component({
  selector: 'user-settings',
  templateUrl: './user-settings.component.html',
  styleUrls: ['./user-settings.component.css']
})
export class UserSettingsComponent implements OnInit {

  private _userSettingsForm: FormGroup;
  private _user: any;
  private _settingsUpdated = false;

  constructor(private _settingsService: UserSettingsService,
              private _fb: FormBuilder) { }

  ngOnInit() {

    this._userSettingsForm = this._fb.group({
      email_address: ['',  Validators.compose([
        Validators.required,
        EmailAddressValidators.isInvalidEmail
      ])],
      new_password: ['', Validators.compose([
        Validators.minLength(environment.minPasswordLength),
        PasswordValidators.hasLowerCase,
        PasswordValidators.hasUpperCase,
        PasswordValidators.hasDigit,
        PasswordValidators.hasSymbol
      ])],
      confirm_password: ['', ],
      old_password: ['', ]
    });

    this._settingsService.getMe().subscribe(
      user => {
        this._user = user;
        this._userSettingsForm.setValue({
          email_address: this._user.email_address,
          new_password: '',
          confirm_password: '',
          old_password: ''
        });
      });
  }

  public saveSettings(values: any) {
    this._settingsUpdated = false;
    if (values.new_password) {
      // Check that the new_password matches the confirm_password
      if (values.new_password !== values.confirm_password) {
        this._userSettingsForm.setErrors({ passwordMismatch: true });
      }
      // Check if the user entered their current password
      if (!values.old_password) {
        this._userSettingsForm.setErrors({ oldPasswordInvalid: true });
      }
      return;
    }

    this._settingsService.updateSettings(values).subscribe(
      user => {
        this._user = user;
        this._userSettingsForm.setValue({
          email_address: this._user.email_address,
          new_password: '',
          confirm_password: '',
          old_password: ''
        });
        this._settingsUpdated = true;
      },
      error => {
        console.log('Error while saving settings');
        console.log(error);
      });
  }

  public closedUpdated() {
    this._settingsUpdated = false;
  }

}
