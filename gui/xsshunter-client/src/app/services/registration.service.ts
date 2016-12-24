import { Injectable } from '@angular/core';

import { HttpClientService } from '../core-services/http-client.service';


@Injectable()
export class RegistrationService {

  private readonly _registration_url = '/api/v2/registration';

  constructor(private _http: HttpClientService) { }

  public createNewUser(data) {
    return this._http.post(this._registration_url, data);
  }

}
