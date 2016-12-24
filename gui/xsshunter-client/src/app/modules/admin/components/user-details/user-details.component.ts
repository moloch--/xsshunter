import { Component, ViewChild, OnInit, Input } from '@angular/core';
import { ActivatedRoute, Router }   from '@angular/router';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';

import { Modal } from 'angular2-modal/plugins/bootstrap';

import { UserService } from '../../services/user.service';
import { EmailAddressValidators, PasswordValidators } from '../../../../shared/validators';
import { environment } from '../../../../../environments/environment';


@Component({
  selector: 'app-user-details',
  templateUrl: './user-details.component.html',
  styleUrls: ['./user-details.component.css']
})
export class UserDetailsComponent implements OnInit {

  private _user;
  private _teams;
  private _editable = false;
  private _editUserForm: FormGroup;
  private _updatedUser = false;
  private _editError = false;
  private _editErrorMessage: string;

  constructor(private _route: ActivatedRoute,
              private _router: Router,
              private _userService: UserService,
              private _fb: FormBuilder,
              public modal: Modal) { }

  ngOnInit() {
    
    this._userService.getTeams().subscribe((teams) => {
      this._teams = teams;
    });

    this._editUserForm = this._fb.group({
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
        Validators.minLength(environment.minPasswordLength),
        PasswordValidators.hasLowerCase,
        PasswordValidators.hasUpperCase,
        PasswordValidators.hasDigit,
        PasswordValidators.hasSymbol
      ])],
      confirm_password: [''],
      team_id: [''],
      is_admin: false,
      is_team_manager: false,
    });

    this._route.params.subscribe(params => {
      this._userService.getUser(params['user-id']).subscribe((user) => {
        this._user = user;
        this._editUserForm.setValue({
          name: this._user.name,
          email_address: this._user.email_address,
          password: '',
          confirm_password: '',
          team_id: this._user.team_id,
          is_admin: this._user.is_admin,
          is_team_manager: this._user.is_team_manager
        });
      });
    });
  }

  public enabledEditing() {
    this._editable = true;
  }

  public editUserAccount(value: any) {
    if (value.password && value.password !== value.confirm_password) {
      this._editErrorMessage = 'Passwords do not match';
      this._editError = true;
    } else {
      value.user_id = this._user.id;
      this._userService.editUserAccount(value).subscribe(
        user => {
          this._user = user;
          this._updatedUser = true;
          this._editable = false;
        },
        resp => {
          this._editErrorMessage = resp.json().error;
          this._editError = true;
        });
    }
  }

  public lockAccount() {
    this._userService.lockUserAccount(this._user.id).subscribe(
      user => {
        this._user = user;
      });
  };

  public unlockAccount() {
    this._userService.unlockUserAccount(this._user.id).subscribe(
      user => {
        this._user = user;
      });
  }

  public confirmDeleteAccount() {
    this.modal.confirm()
      .size('sm')
      .isBlocking(true)
      .showClose(true)
      .titleHtml('<i class="fa fa-fw fa-user-times"></i> Delete User?')
      .body(`Are you user you want to delete this user?`)
      .okBtn('Delete')
      .okBtnClass('btn btn-danger')
      .open()
      .then(dialog => dialog.result)
      .then(result => {
        this._deleteAccount();
      }).catch((error) => {
        console.log('User clicked cancel');
      });
  }

  private _deleteAccount() {
    this._userService.deleteUserAccount(this._user.id).subscribe(
      () => {
        this._router.navigate(['admin/users']);
      },
      resp => {
        this._editError = true;
        this._editErrorMessage = resp.json().error;
      });
  }

  public closeEditError() {
    this._editError = false;
  }

  public closeUpdated() {
    this._updatedUser = false;
  }

}
