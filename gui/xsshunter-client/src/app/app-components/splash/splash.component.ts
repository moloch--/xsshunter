import { 
  Component, OnInit, style, state, animate, transition, trigger
} from '@angular/core';


@Component({
  selector: 'app-splash',
  templateUrl: './splash.component.html',
  styleUrls: ['./splash.component.css'],
  animations: [
    trigger('fadeInOut', [
      transition(':enter', [   // :enter is alias to 'void => *'
        style({opacity:0}),
        animate(750, style({opacity:1})) 
      ]),
      transition(':leave', [   // :leave is alias to '* => void'
        animate(750, style({opacity:0})) 
      ])
    ])
  ]
})
export class SplashComponent implements OnInit {

  constructor() { }

  ngOnInit() {
  }

}
