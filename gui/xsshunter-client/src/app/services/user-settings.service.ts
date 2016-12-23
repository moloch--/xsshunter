import { Injectable } from '@angular/core';

import { HttpClientService } from '../core-services/http-client.service';


@Injectable()
export class UserSettingsService {

  private _me_url = '/api/v1/me';

  constructor(private _http: HttpClientService) { }

  public getMe() {
    return this._http.get(this._me_url);
  }

  public updateSettings(data: any) {
    return this._http.put(this._me_url, data);
  }

}
