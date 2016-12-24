import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { UserService } from '../../services/user.service';



@Component({
  selector: 'admin-users',
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css']
})
export class UsersComponent implements OnInit {

  private _users: any;

  constructor(private _router: Router,
              private _userService: UserService) { }

  ngOnInit() {
    this._userService.getUsers().subscribe(users => {
      this._users = users;
    });
  }

  selectUser(user) {
    this._router.navigate(['/admin/users', user.id]);
  }

}
