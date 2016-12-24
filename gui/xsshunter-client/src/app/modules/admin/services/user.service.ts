import { Injectable } from '@angular/core';
import { Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';

import { HttpClientService } from '../../../core-services/http-client.service';


@Injectable()
export class UserService {
  
  private readonly _user_url = '/api/v1/admin/user';
  private readonly _team_url = '/api/v1/admin/team';
  private readonly _lock_url = '/api/v1/admin/lock';

  constructor(private _http: HttpClientService) { }

  getUsers() {
    return this._http.get(this._user_url);
  }

  getUser(userId: string) {
    return this._http.get(this._user_url + '/' + userId);
  }

  addUser(data: Object) {
    return this._http.post(this._user_url, data);
  }

  editUserAccount(data: Object) {
    return this._http.put(this._user_url, data);
  }

  lockUserAccount(userId: string) {
    return this._http.post(this._lock_url, {
      user_id: userId,
      lock: true
    });
  }

  unlockUserAccount(userId: string) {
    return this._http.post(this._lock_url, {
      user_id: userId,
      lock: false
    });
  }

  deleteUserAccount(userId: string) {
    return this._http.delete(this._user_url + '/' + userId);
  }

  getTeams() {
    return this._http.get(this._team_url);
  }

  addTeam(data: Object) {
    return this._http.post(this._team_url, data);
  }

}