import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';

import { Ng2BootstrapModule, AlertModule } from 'ng2-bootstrap';

import { HttpClientService } from './core-services/http-client.service';
import { WebSocketService } from './core-services/web-socket.service';
import { UserSettingsService } from './services/user-settings.service';

import { SharedModule } from './shared/module/shared.module'; 

import { AppRoutes, RouterGuards }  from './app-routes/app.routes';

import { AppComponent } from './app.component';
import { LoginComponent } from './app-components/login';
import { LogoutComponent } from './app-components/logout';
import { NotFoundComponent } from './app-components/not-found';
import { TopMenuComponent } from './app-components/top-menu';
import { HomeComponent } from './app-components/home/home.component';
import { UserSettingsComponent } from './app-components/user-settings/user-settings.component';
import { RegistrationComponent } from './app-components/registration/registration.component';
import { SplashComponent } from './app-components/splash/splash.component';


@NgModule({
  declarations: [
    AppComponent,

    LoginComponent,
    LogoutComponent,
    NotFoundComponent,
    TopMenuComponent,
    HomeComponent,
    UserSettingsComponent,
    RegistrationComponent,
    SplashComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    HttpModule,

    // Bootstrap
    Ng2BootstrapModule,
    AlertModule,
    

    // Shared module
    SharedModule,

    // Routes
    AppRoutes,  
  ],
  providers: [
    HttpClientService,
    WebSocketService,
    RouterGuards,

    UserSettingsService,
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
