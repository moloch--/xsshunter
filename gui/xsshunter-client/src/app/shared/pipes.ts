import { Pipe, PipeTransform } from '@angular/core';


declare var moment: any;

/*
 * For nullable values will display a word instead of ''
 * 
 * Usage:
 *   value | nullable:nullWord
*/
@Pipe({ name: 'nullable' })
export class NullablePipe implements PipeTransform {
  transform(value: string | null, nullWord: string): string {
    return value === null ? nullWord : value;
  }
}

/*
 * Capitalize the first letter of a string
 * 
 * Usage:
 *   value | capitalize
*/
@Pipe({ name: 'capitalize' })
export class CapitalizePipe implements PipeTransform {
  transform(value: string): string {
    return value[0].toUpperCase() + value.slice(1);
  }
}

/*
 * Decode a base64 encoded string
 * 
 * Usage:
 *   value | base64decode
*/
@Pipe({ name: 'base64decode' })
export class Base64DecodePipe implements PipeTransform {
  transform(value: string): string {
    return atob(value);
  }
}

/*
 * Display a unixtime value in a given moment.js format,
 * default format is: 'MMM Do YYYY h:mm a'
 * 
 * Usage:
 *   value | unixtime:<format>
*/
@Pipe({ name: 'unixtime' })
export class UnixTimePipe implements PipeTransform {
  transform(value: number | null, format: string = 'MMM Do YYYY h:mm a'): string {
    if (value === null) {
      return 'Never';
    }
    return  moment(value * 1000).format(format);
  }
}