import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { Ng2BootstrapModule } from 'ng2-bootstrap';

import { ColumnComponent, DatatableComponent } from './components/datatable';
import { UploadFileComponent } from './components/upload-file';
import { NullablePipe, CapitalizePipe, Base64DecodePipe, UnixTimePipe } from '../pipes';


@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    Ng2BootstrapModule
  ],
  exports: [
    ColumnComponent,
    DatatableComponent,
    UploadFileComponent,
    NullablePipe,
    CapitalizePipe,
    Base64DecodePipe,
    UnixTimePipe
  ],
  declarations: [
    ColumnComponent,
    DatatableComponent,
    UploadFileComponent,
    NullablePipe,
    CapitalizePipe,
    Base64DecodePipe,
    UnixTimePipe
  ]
})
export class SharedModule { }
