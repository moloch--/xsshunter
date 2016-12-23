import { Component, Input } from '@angular/core';
import { DatatableComponent } from './datatable.component';


@Component({
  selector: 'column',
  template: ``
})
export class ColumnComponent {

  @Input() value;
  @Input() header;
  @Input() sortable = false;
  @Input() customContent = false;
  @Input() customRenderFunction: Function;
  @Input() boolean = false;
  @Input() count = false;
  @Input() lazyLoad = false;
  @Input() fontAwesome = false;
  @Input() date = false;

  constructor(table: DatatableComponent) {
    if (this.fontAwesome && !this.customRenderFunction) {
      console.error('fontAwesome requires a customRenderFunction');
    }
    table.addColumn(this);
  }

  public getValue() {
    return this.value;
  }

}