import { Component, OnInit } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';

import { environment } from '../../../../../environments/environment';

import { UserService } from '../../services/user.service';


@Component({
  selector: 'admin-add-team',
  templateUrl: './add-team.component.html',
  styleUrls: ['./add-team.component.css']
})
export class AddTeamComponent implements OnInit {

  private _addTeamForm: FormGroup;

  constructor(private _router: Router,
              private _userService: UserService,
              private _fb: FormBuilder) { }

  ngOnInit() {
    this._addTeamForm = this._fb.group({
      name: ['', Validators.compose([
        Validators.required,
        Validators.minLength(environment.minTeamNameLength),
        Validators.maxLength(environment.maxTeamNameLength)
      ])],
    });
  }

  addTeamAttempt(value: any) {
    this._userService.addTeam(value).subscribe(
      resp => {
        this._router.navigate(['/admin/add-user']);
      },
      err => {
        this._addTeamForm.setErrors({ failedToCreateTeam: true });
      });
  }

}
