import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { AlertModule, ModalModule } from 'ng2-bootstrap';

import { SharedModule } from '../../shared';

import { UserService } from './services/user.service';
import { AdminComponent } from './admin.component';
import { AddUserComponent } from './components/add-user';
import { UsersComponent } from './components/users/users.component';
import { AddTeamComponent } from './components/add-team/add-team.component';
import { UserDetailsComponent } from './components/user-details/user-details.component';


@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule,
    AlertModule,
    ModalModule,
    SharedModule
  ],
  providers: [
    UserService
  ],
  declarations: [
    AdminComponent,
    AddUserComponent,
    UsersComponent,
    AddTeamComponent,
    UserDetailsComponent,
  ]
})
export class AdminModule { }
