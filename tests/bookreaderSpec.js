/**
 * Some BDD style tests. The point is that reading these should be like
 * reading some sort of specification for the application being tested.
 */

/**
 * Encapsulates tests that describe the expected behaviour of the bookreader
 * application
 */
describe("bookreader.js", function() {

    beforeEach(function() {
        jasmine.getFixtures().load("mockDom.html");
        this.server = sinon.fakeServer.create();
        this.xhr = sinon.useFakeXMLHttpRequest();
        $.jStorage.flush();
    });

    afterEach(function() {
        this.server.restore();
    });
});
