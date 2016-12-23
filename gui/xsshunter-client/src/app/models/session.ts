/*
 *   Created by: moloch
 *         Date: 6/29/16
 *  Description: Model that is responsible for tracking session-state information
 */

declare var moment: any;

export class Session {

  private readonly UNAUTHENTICATED: string = 'unauthenticated';

  public username: string | null;
  public userId: string | null;
  public email: string | null;
  public expires: number | null;
  public debug: boolean | null;
  public data: string = this.UNAUTHENTICATED;
  public isAdmin: boolean | null;

  constructor(sessionData?: any) {
    if (sessionData) {
      this.setData(sessionData);
    }
  }

  setData(sessionData: any) {
    this.userId = sessionData.user_id || '';
    this.username = sessionData.username || '';
    this.email = sessionData.email || '';
    this.data = sessionData.data || this.UNAUTHENTICATED;
    this.expires = sessionData.expires || 0;
    this.debug = sessionData.debug || false;
    this.isAdmin = sessionData.is_admin || false;
  }

  isAuthenticated() {
    return this.data !== this.UNAUTHENTICATED && !this.isExpired() ? true : false;
  }

  isExpired() {
    return this.expires && this.expires <= this.getUnixTime() ? true : false;
  }

  private getUnixTime() {
    return moment.unix();
  }

  toJSON(): Object {
    return {
      username: this.username,
      user_id: this.userId,
      email: this.email,
      expires: this.expires,
      debug: this.debug,
      data: this.data,
      is_admin: this.isAdmin
    };
  }

}
