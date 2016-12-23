/*
 * WebSocket management class
 */

import { Injectable } from '@angular/core';
import { Subject } from 'rxjs/Subject';
import { Observable } from 'rxjs/Observable';
import { Observer } from 'rxjs/Observer';

import { environment } from '../../environments/environment';


export interface WebSocketFrame {
    message_type: string;
    message: Object;
}


Injectable()
export class WebSocketService {

  private _rawSockets = {};
  private _apiHost: string;
  private _wsProtocol: string;
  private _sendQueue = {};

  constructor() {
    if (environment.production) {
      this._wsProtocol = 'wss:';  // Always use wss in production
    } else {
      this._wsProtocol = document.location.protocol === 'http:' ? 'ws:' : 'wss:';
    }
    this._apiHost = environment.apiHost ? environment.apiHost : document.location.host;
  }

  public connect(path: string, onOpenCallback: Function, onCloseCallback: Function): Subject<MessageEvent> {
    let url = this._toWebsocketUrl(path);
    console.log('WebSocket connecting to -> ' + url);
    let socket = this.create(url, onOpenCallback, onCloseCallback);
    return socket;
  }

  private _toWebsocketUrl(path: string) {
    let url = new URL("x://y");
    url.protocol = this._wsProtocol;
    url.hostname = this._apiHost;
    url.pathname = path;
    return url.toString();
  }

  public isReady(url: string): Boolean {
    let _url = this._toWebsocketUrl(url);
    return this._rawSockets[_url].readyState === WebSocket.OPEN ? true : false;
  }

  public connectWebSocket(path: string, onOpen: Function, onClose: Function): Subject<WebSocketFrame> {
    console.log('Connecting WebSocket to server');
    let messages$ = <Subject<WebSocketFrame>> this.connect(path, onOpen, onClose)
      .map((response: MessageEvent): WebSocketFrame => {
          let data = JSON.parse(response.data);
          return {
            message_type: data.message_type.toString(),
            message: data.message,
          };
      });
    return messages$;
  }

  private create(url: string, onOpenCallback: Function, onCloseCallback: Function): Subject<MessageEvent> {

    let socket = new WebSocket(url);
    this._rawSockets[url] = socket;
    this._sendQueue[url] = new Array();

    let observable = Observable.create((obs: Observer<MessageEvent>) => {
        socket.onmessage = obs.next.bind(obs);
        socket.onerror = obs.error.bind(obs);
        socket.onclose = () => {
          console.log('WARNING: WebSocket lost connection to server');
          obs.complete.bind(obs);
          onCloseCallback();
        }
        socket.onopen = () => {
          this._drainSendQueue(url);
          onOpenCallback();
        }
        return socket.close.bind(socket);
    });

    let observer = {
      next: (data: Object) => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify(data));
        } else {
          console.log('WebSocket not ready, queuing message');
          this._sendQueue[url].push(data);
        }
      },
    };

    return Subject.create(observer, observable);
  }

  private _drainSendQueue(url: string) {
    if (this._sendQueue[url].length === 0) {
      return;  // Short-cut if there are no queued messages
    }
    console.log('Sending all queued messages for ' + url);
    for (let index = 0; index < this._sendQueue[url].length; ++index) {
      let data = this._sendQueue[index];
      this._rawSockets[url].send(JSON.stringify(data));
    }
    this._sendQueue = new Array();
  }

}