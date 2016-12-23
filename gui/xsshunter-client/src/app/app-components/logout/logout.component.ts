import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { HttpClientService } from '../../core-services/http-client.service';

@Component({
  selector: 'logout',
  template: ''
})
export class LogoutComponent implements OnInit {

  constructor(private _router: Router, private _http: HttpClientService) {}

  ngOnInit() {
    this._http.destroySession();
    this._router.navigate(['/login']);
  }

}
