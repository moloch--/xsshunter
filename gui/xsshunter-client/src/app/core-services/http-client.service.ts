import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { Http, Headers, Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { Subject } from 'rxjs/Subject';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';

import 'rxjs/add/operator/map';
import 'rxjs/add/operator/toPromise';

import { WebSocketService, WebSocketFrame } from './web-socket.service';
import { Session } from '../models/session';
import { environment } from '../../environments/environment';


export const UNAUTHENTICATED = 'unauthenticated';


@Injectable()
export class HttpClientService {

  session: Session = new Session();

  private _protocol: string;
  private _apiHost: string;
  private readonly _sessionUrl = '/api/v2/session';
  private readonly _AUTH_HEADER = 'X-XSS-HUNTER';
  private readonly _JSON_MIME = 'application/json';

  private _session$: BehaviorSubject<Session> = new BehaviorSubject(this.session);
  public session$: Observable<Session> = this._session$.asObservable();

  constructor(private _router: Router, private _http: Http, private _ws: WebSocketService) {
    if (environment.production) {
      this._protocol = 'https:';  // Force HTTPS in production
    } else {
      this._protocol = document.location.protocol;
    }
    this._apiHost = environment.apiHost ? environment.apiHost : document.location.host;
    console.log(`API Host is set to '${this._apiHost}'`);

    this.loadLocalSession();
  }

  /*
   * Converts a path to a HTTP URI
   */
  toAbsoluteUrl(path: string) {
    let url = new URL('x://y');
    url.protocol = this._protocol;
    url.hostname = this._apiHost;
    url.pathname = path;
    return url.toString();
  }

  /*
   * Adds HTTP headers to each request
   */
  headers(): Headers {
    let headers = new Headers();
    if (this.session && this.session.isAuthenticated()) {
      headers.append(this._AUTH_HEADER, this.session.data);
    } else {
      headers.append(this._AUTH_HEADER, UNAUTHENTICATED);
    }
    headers.append('Content-type', this._JSON_MIME);
    headers.append('Accept', this._JSON_MIME);
    return headers;
  }

  /*
   * Determines if the current session is authenticated
   */
  isAuthenticated() {
    return this.session ? this.session.isAuthenticated() : false;
  }

  /*
   * Update current session and notify observers
   */
  private _updateSession(data: Object) {
    this.session.setData(data);
    this._session$.next(this.session);
  }

  /*
   * Loads session data from localStorage
   */
  loadLocalSession(): Boolean {
    if (localStorage && localStorage.getItem('data')) {
      let sessionData = {
        user_id: localStorage.getItem('user_id'),
        username: localStorage.getItem('username'),
        data: localStorage.getItem('data'),
        expires: parseInt(localStorage.getItem('expires'), 10),
        debug: localStorage.getItem('debug') === 'true',
        is_admin: localStorage.getItem('is_admin') == 'true'
      }
      this._updateSession(sessionData);
      if (!this.session.isExpired()) {
        console.log('Resuming session from local storage');
        return true;
      }
    }
    return false;
  }

  /*
   * Saves current session data to localStorage
   */
  saveLocalSession() {
    if (this.session && this.session.isAuthenticated) {
      if (localStorage) {
        console.log('Saving local session ...');
        localStorage.setItem('user_id', this.session.userId);
        localStorage.setItem('username', this.session.username);
        localStorage.setItem('data', this.session.data);
        localStorage.setItem('expires', this.session.expires.toString());
        localStorage.setItem('debug', this.session.debug.toString());
        localStorage.setItem('is_admin', this.session.isAdmin.toString());
      }
    } else {
      console.log('No valid session to save');
    }
  }

  /*
   * Creates a new session given credentials `args`
   */
  createSession(args: Object) {
    console.log('Attempting to start new session ...');
    return this.post(this._sessionUrl, JSON.stringify(args))
      .toPromise()
      .then(sessionData => {
        console.log(sessionData);
        this._updateSession(sessionData);
        this.saveLocalSession();
      });
  }

  /*
   * Clears the current session and remove anything in localStorage
   */
  destroySession() {
    this._updateSession({});
    if (localStorage) {
      localStorage.clear();
    }
  }

  /*
   * HTTP GET
   */
  get(url): Observable<Response>  {
    console.log(`GET -> ${this.toAbsoluteUrl(url)}`);
    return this._http.get(this.toAbsoluteUrl(url), {
      headers: this.headers()
    }).filter(
      resp => { 
        if (200 <= resp.status && resp.status <= 299) {
          return true;
        } else if (resp.status == 403) {
          console.log('Session appears to have expired, logging out.');
          this._router.navigate(['/logout']);
          return false;
        }
      }).map(resp => resp.json());
  }

  /*
   * HTTP POST
   */
  post(url, data): Observable<Response> {
    console.log(`POST -> ${this.toAbsoluteUrl(url)}`);
    return this._http.post(this.toAbsoluteUrl(url), data, {
      headers: this.headers()
    }).map(resp => resp.json());
  }

  /*
   * HTTP PUT
   */
  put(url, data): Observable<Response>  {
    console.log(`PUT -> ${this.toAbsoluteUrl(url)}`);
    return this._http.put(this.toAbsoluteUrl(url), data, {
      headers: this.headers()
    }).map(resp => resp.json());
  }

  /*
   * HTTP DELETE
   */
  delete(url): Observable<Response>  {
    console.log(`DELETE -> ${this.toAbsoluteUrl(url)}`);
    return this._http.delete(this.toAbsoluteUrl(url), {
      headers: this.headers()
    }).map(resp => resp.json());
  }

}
