import {
  Component, OnInit, style, state, animate, transition, trigger
} from '@angular/core';


@Component({
  selector: 'app-features',
  templateUrl: './features.component.html',
  styleUrls: ['./features.component.css'],
  animations: [
    trigger('fadeInOut', [
      transition(':enter', [   // :enter is alias to 'void => *'
        style({opacity:0}),
        animate(400, style({opacity:1})) 
      ]),
      transition(':leave', [   // :leave is alias to '* => void'
        animate(400, style({opacity:0})) 
      ])
    ])
  ]
})
export class FeaturesComponent implements OnInit {

  constructor() { }

  ngOnInit() {
  }

}
