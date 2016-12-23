import { Component } from '@angular/core';

import { HttpClientService } from '../../core-services/http-client.service';


@Component({
  selector: 'top-menu',
  templateUrl: './top-menu.component.html',
})
export class TopMenuComponent {

  constructor(private _http: HttpClientService) {
    // Pass
  }

  isDebugMode() {
    return this._http.session ? this._http.session.debug : false;
  }

  isAdmin() {
    return this._http.session ? this._http.session.isAdmin : false;
  }

  getUsername() {
    return this._http.session ? this._http.session.username : '';
  }

}
