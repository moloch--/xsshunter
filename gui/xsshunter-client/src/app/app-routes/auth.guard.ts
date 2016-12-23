import { Injectable } from '@angular/core';
import { CanActivate } from '@angular/router';
import { Router } from '@angular/router';

import { HttpClientService } from '../core-services/http-client.service';


@Injectable()
export class AuthN implements CanActivate {

  constructor(private _router: Router,
              private _http: HttpClientService) {
  }

  canActivate() {
    if (this._http.isAuthenticated()) {
      return true;
    } else {
      this._http.destroySession();
      this._router.navigate(['/login']);
      return false;
    }
  }

}


@Injectable()
export class AuthzAdmin implements CanActivate {

  constructor(private _router: Router,
              private _http: HttpClientService) {
  }

  canActivate() {
    let permission = this._http.isAuthenticated() && this._http.session.isAdmin ? true : false;
    console.log('User is admin? ' + permission);
    return permission;
  }

}