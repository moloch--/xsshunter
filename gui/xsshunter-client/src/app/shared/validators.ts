import { FormControl } from '@angular/forms';

import { environment } from '../../environments/environment';


export class OtpValidators {

  static isInvalidOtp(control: FormControl) {
    if (control.value.length === 0) {
      return null;
    }
    let regexp = new RegExp('^[0-9]{6,8}$');
    return regexp.test(control.value) ? null : { isInvalidOtp: true };
  }

}


export class EmailAddressValidators {

  static isInvalidEmail(control: FormControl) {
    if (control.value === null || control.value.length === 0) {
      return null;
    }
    let regexp = new RegExp('^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$');
    return regexp.test(control.value) ? null : { isInvalidEmailAddress: true };
  }

}


export class PhoneNumberValidators {

  static isInvalidUSPhoneNumber(control: FormControl) {
    if (control.value.length === 0) {
      return null;
    }
    let regexp = new RegExp('^(\\+\\d{1,2}\\s)?\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}$');
    return regexp.test(control.value) ? null : { isInvalidPhoneNumber: true };
  }

}


export class PasswordValidators {

  static hasLowerCase(control: FormControl) {
    if (!environment.production) {
      return null;
    }
    return /[a-z]/.test(control.value) ? null : { missingLowerCase: true };
  }

  static hasUpperCase(control: FormControl) {
    if (!environment.production) {
      return null;
    }
    return /[A-Z]/.test(control.value) ? null : { missingUpperCase: true };
  }

  static hasDigit(control: FormControl) {
    if (!environment.production) {
      return null;
    }
    return /[0-9]/.test(control.value) ? null : { missingDigit: true };
  }

  static hasSymbol(control: FormControl) {
    if (!environment.production) {
      return null;
    }
    return /[\W]/.test(control.value) ? null : { missingSymbol: true };
  }

}
