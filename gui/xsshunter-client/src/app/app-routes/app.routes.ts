import { Routes, RouterModule } from '@angular/router';
import { ModuleWithProviders } from '@angular/core';

import { AuthN, AuthzAdmin } from './auth.guard';

import { SplashComponent } from '../app-components/splash';
import { DonateComponent } from '../app-components/donate';
import { FeaturesComponent } from '../app-components/features';
import { LoginComponent } from '../app-components/login';
import { LogoutComponent } from '../app-components/logout';
import { RegistrationComponent } from '../app-components/registration';
import { NotFoundComponent } from '../app-components/not-found';

import { HomeComponent } from '../app-components/home';
import { UserSettingsComponent } from '../app-components/user-settings';


const routes: Routes = [

  /* Public Routes */
  { path: '', component: SplashComponent, pathMatch: 'full' },
  { path: 'splash', component: SplashComponent, pathMatch: 'full' },
  { path: 'login', component: LoginComponent, pathMatch: 'full' },
  { path: 'register', component: RegistrationComponent, pathMatch: 'full' },
  { path: 'donate', component: DonateComponent, pathMatch: 'full' },
  { path: 'features', component: FeaturesComponent, pathMatch: 'full' },
  { path: 'logout', component: LogoutComponent, pathMatch: 'full' },

  /* Authenticated Routes */
  { path: 'home', component: HomeComponent, canActivate: [AuthN] },
  { path: 'settings', component: UserSettingsComponent, canActivate: [AuthN] },

  /* Catch all */
  { path: '**', component: NotFoundComponent }

];


export const RouterGuards = [AuthN, AuthzAdmin];
export const AppRoutes: ModuleWithProviders = RouterModule.forRoot(routes);
