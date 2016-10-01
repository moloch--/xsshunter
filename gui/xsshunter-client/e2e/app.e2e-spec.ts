import { XsshunterClientPage } from './app.po';

describe('xsshunter-client App', function() {
  let page: XsshunterClientPage;

  beforeEach(() => {
    page = new XsshunterClientPage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
