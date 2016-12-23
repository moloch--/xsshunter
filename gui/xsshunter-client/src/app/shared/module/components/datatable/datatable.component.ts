import { Injectable, Component, Input, Output, EventEmitter, OnInit } from '@angular/core';

import { ColumnComponent } from './column.component';


export interface CustomSorter {
  key: string,
  sorter: Function
};


@Component({
  selector: 'datatable',
  templateUrl: './datatable.component.html',
  styleUrls: ['./datatable.component.css'],
})
export class DatatableComponent implements OnInit {

  @Input() dataset;
  @Input() enableFilter = false;
  @Input() title: string;
  @Input() faClass: string;
  @Input() defaultSortingKey: string;
  @Input() defaultSortingReverse = false;
  @Input() enablePages = true;
  @Output() rowSelection = new EventEmitter();

  public columns: ColumnComponent[] = [];
  public filterQuery = '';
  public filteredList: Array<Object>;
  
  private _viewData: Array<Object>;
  private _isSorted = false;
  private _sortingKey: string | null;
  private _reverse = false;
  private _currentPage = 1;
  private _maxPageSize = 10;

  private _faClassMap = { 
    'fa': true,
    'fa-fw': true,
    'fa-search': false,
    'fa-user': false,
    'fa-users': false
  };

  ngOnInit() {
    if (this.faClass in this._faClassMap) {
      this._faClassMap[this.faClass] = true;
    }

    if (this.defaultSortingKey) {
      this._sortingKey = this.defaultSortingKey;
      this.dataset = this._sortData(this.dataset);
      if (this.defaultSortingReverse) {
        this.dataset.reverse();
        this._reverse = true;
      }
      this._isSorted = true;
    }
  }

  private _pageChanged(event) {
    console.log('Page changed to: ' + event.page);
  }

  private _getData() {

    // Sort data if enabled
    if (this._isSorted) {
      this._sortData(this.dataset);
    }
    
    // Reverse sort if enabled
    if (this._reverse) {
      this.dataset.reverse();
    }

    // Return filtered results or entire data set
    let data = this.enableFilter && this.filterQuery.length ? this.filteredList : this.dataset;
    if (!this.enablePages || !data || data.length < this._maxPageSize) {
      return data;
    } else {
      let offset = this._currentPage * this._maxPageSize;
      return data.slice(offset - this._maxPageSize, offset);
    }
  }

  private _sortData(data: Array<Object>) {
    if (this._sortingKey === null || this._sortingKey.length < 1) {
      console.error('Sort called, but no sorting key is set');
      return data;
    }
    if (!data) {
      console.error('Sort called, but no data!');
    }

    // Generic property sort function
    return data.sort((a, b) => {
      if (a[this._sortingKey] > b[this._sortingKey]) {
        return 1;
      } else if (a[this._sortingKey] < b[this._sortingKey]) {
        return -1;
      } else {
        return 0;
      }
    });

  }

  public addColumn(column) {
    this.columns.push(column);
  }

  public appendRow(row) {
    this.dataset.push(row);
  }

  public prependRow(row) {
    this.dataset.unshift(row);
  }

  public filter() {
    this.filteredList = this.dataset.filter(
      item => {
        let result = '';
        for (let key in item) {
          result += item[key];
        }
        return result.toLowerCase().indexOf(this.filterQuery.toLowerCase()) > -1;
      });
  }

  public sortBy(column: ColumnComponent) {
    if (!column.sortable) {
      return;
    }
    // If they clicked the same column twice we reverse the sort
    if (column.value === this._sortingKey) {
      this._reverse = !this._reverse;
    }

    // Set the sorting key value
    this._sortingKey = column.value;
    this._isSorted = true;
  }

  public selectRow(row: Object) {
    this.rowSelection.emit({ value: row });
  }

}