import { Routes, RouterModule } from '@angular/router';
import { ModuleWithProviders } from '@angular/core';

import { AuthN, AuthzAdmin } from '../../app-routes/auth.guard';

import { UsersComponent } from './components/users';
import { UserDetailsComponent } from './components/user-details';
import { AddUserComponent } from './components/add-user';
import { AddTeamComponent } from './components/add-team';


const routes: Routes = [

  { path: 'admin/users', component: UsersComponent, canActivate: [AuthN, AuthzAdmin] },
  { path: 'admin/users/:user-id', component: UserDetailsComponent, canActivate: [AuthN, AuthzAdmin] },
  { path: 'admin/add-user', component: AddUserComponent, canActivate: [AuthN, AuthzAdmin] },
  { path: 'admin/add-team', component: AddTeamComponent, canActivate: [AuthN, AuthzAdmin] },

];

export const AdminRoutes: ModuleWithProviders = RouterModule.forChild(routes);
