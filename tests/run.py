import unittest2 as unittest
import fluidinfo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import time

# The driver for the tests that follow
driver = webdriver.Firefox()
driver.get('http://localhost:8080/')

# A session to Fluidinfo that allows us to clean up any mess that we may make.
fluidinfo.login('test', 'test')

class TestBookreaderInitialisation(unittest.TestCase):
    """
    Ensures the application starts in a good state.
    """

    def testAboutStartState(self):
        """
        Make sure the about div is displayed.
        """
        aboutContainer = driver.find_element_by_id('aboutContainer')
        self.assertTrue(aboutContainer.is_displayed())

    def testColophonStartState(self):
        """
        Make sure the colophon div is not displayed at start state.
        """
        colophonContainer = driver.find_element_by_id('colophonContainer')
        self.assertFalse(colophonContainer.is_displayed())

    def testHelpStartState(self):
        """
        Make sure the help div is not displayed at start state.
        """
        helpContainer = driver.find_element_by_id('helpContainer')
        self.assertFalse(helpContainer.is_displayed())

    def testOopsStartState(self):
        """
        Make sure the oops div is not displayed at start state.
        """
        oopsContainer = driver.find_element_by_id('oops')
        self.assertFalse(oopsContainer.is_displayed())

    def testWorkingStartState(self):
        """
        Make sure the working div is not displayed at start state.
        """
        workingContainer = driver.find_element_by_id('working')
        self.assertFalse(workingContainer.is_displayed())


class TestBookreaderSession(unittest.TestCase):
    """
    Ensures that session handling (login / logout) work as expected.
    """

    def testToggleLogin(self):
        """
        Checks the "login" link opens the login lightbox.
        """
        pass

    def testCancelLogin(self):
        """
        Ensures that the cancel button in the login form works as expected.
        """
        pass

    def testSubmitLogin(self):
        """
        Checks that the login form closes with valid input and that the
        logout and user info elements are displayed.
        """
        pass

    def testLoginInsistsOnUsernameAndPassword(self):
        """
        Makes sure the login form only works if both username and password are
        supplied.
        """
        pass

    def testLoginErrorHidesOnCancel(self):
        """
        Ensures the error message is hidden when the form is cancelled.
        """
        pass

    def testLoginErrorHidesOnValidLogin(self):
        """
        Ensures the error message is hidden when the form is correctly
        submitted.
        """
        pass

    def testLogout(self):
        """
        Makes sure that the logout link works as expected (updates the UI).
        """
        pass


class TestBookreaderReader(unittest.TestCase):
    """
    Check the reading aspect of the application works as expected.
    """

    def testReaderMenuItems(self):
        """
        Ensures that the chapter menu loads the chapters.
        """
        pass

    def testTagLink(self):
        """
        Ensures that the tag link opens the annotation lightbox.
        """
        pass

    def testAnnotateThisForLoggedInUser(self):
        """
        Makes sure that if the user is logged in they get to see
        "Annotate this!" button in the annotation lightbox.
        """
        pass

    def testPreviousButton(self):
        """
        Ensures the "Previous" button works as expected.
        """
        pass

    def testNextButton(self):
        """
        Ensures the "Next" button works as expected.
        """
        pass

    def textParticipantCount(self):
        """
        Checks that the participant counter eventually gets displayed.
        """
        pass


class TestBookreaderAnnotate(unittest.TestCase):
    """
    Makes sure the annotation related capabilities work as expected.
    """

    def tearDown(self):
        """
        Clean up the test user's account.
        """
        # Remove all the test user's "comment" tags.
        fluidinfo.delete('/values', tags=['test/comment',],
            query='has beckyhogge/html')

    def testAddAnnotation(self):
        """
        Tests a simple comment works correctly.
        """
        pass

    def testCheckForEmptyComment(self):
        """
        Ensures the annotation form displays the correct error message if the
        user attempts to add an empty comment.
        """
        pass

    def testCancelResetsErrorElement(self):
        """
        Makes sure that the error message from submitting an empty comment is
        hidden when the Cancel button is clicked.
        """
        pass

    def testSubmitResetsErrorElement(self):
        """
        Ensures the error message from submitting an empty comment is hidden
        when the form is submitted.
        """
        pass

    def testDeleteComment(self):
        """
        Makes sure that comments are deleted properly.
        """
        pass

    def testMultipleCommentsFromUser(self):
        """
        Makes sure that multiple comments from the same user on an individual
        object are handled properly.
        """
        pass

    def testDeleteOneOfMultipleComments(self):
        """
        Ensures that a single comment deleted from a list of comments from the
        same user on an individual user are handled properly.
        """
        pass

    def testDisplayURLsAsLinks(self):
        """
        Makes sure 1-n referenced URLs are turned into anchors that are
        correctly truncated.
        """
        pass

    def testDisplayYouTube(self):
        """
        Ensure links to YouTube result in the correct media preview.
        """
        pass

    def testDisplayVimeo(self):
        """
        Ensure links to Vimeo result in the correct media preview.
        """
        pass

    def testDisplayTwitpic(self):
        """
        Ensure links to Twitpic result in the correct media preview.
        """
        pass

    def testDisplayYFrog(self):
        """
        Ensure links to yFrog result in the correct media preview.
        """
        pass

    def testDisplaySoundcloud(self):
        """
        Ensure links to SoundCloud result in the correct media preview.
        """
        pass

    def testDisplayPNG(self):
        """
        Ensure direct links to a PNG image result in the correct media preview.
        """
        pass

    def testDisplayGIF(self):
        """
        Ensure direct links to a GIF image result in the correct media preview.
        """
        pass

    def testDisplayJPG(self):
        """
        Ensure direct links to a JPG image result in the correct media preview.
        """
        pass

    def testDisplayOGG(self):
        """
        Ensure direct links to an OGG audio file result in the correct media
        preview.
        """
        pass

    def testDisplayMP3(self):
        """
        Ensure direct links to an MP3 audio file result in the correct media
        preview.
        """
        pass


if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        driver.quit()
