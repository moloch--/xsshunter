import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';


@Component({
  selector: 'upload-file',
  templateUrl: './upload-file.component.html',
  styleUrls: ['./upload-file.component.css']
})
export class UploadFileComponent implements OnInit {

  @Input() buttonText: string;
  @Output() contentEmitter = new EventEmitter();

  private _fileReader: FileReader;
  private _hideInput = true;
  private _reading = false;

  constructor() { }

  ngOnInit() {
  }

  private _getText() {
    return this.buttonText ? this.buttonText : 'Browse';
  }

  private _changeListener($event) {
    this._readFile($event.target);
  }

  private _readFile(values: any) {
    this._reading = true;
    let file: File = values.files[0]; 
    this._fileReader = new FileReader();
    this._fileReader.onloadend = (event) => {
      this._onReadCompleted();  // Get around `this` bullshit
    }
    this._fileReader.readAsBinaryString(file);
  }

  private _onReadCompleted() {
    this._reading = false;
    this.contentEmitter.emit({ value: btoa(this._fileReader.result) });
  }

}
