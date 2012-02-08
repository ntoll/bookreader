import unittest2 as unittest
import fluidinfo
import uuid
import time # used to sleep(1) to allow UI to update
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

    def setUp(self):
        """
        Put the application into a known good state on the homepage
        """
        about = driver.find_element_by_class_name('about')
        about.click()
        logoutLink = driver.find_element_by_id('logoutLink')
        if logoutLink.is_displayed():
            logoutLink.click()

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

    def setUp(self):
        """
        Make sure we're in a good state.
        """
        logoutLink = driver.find_element_by_id('logoutLink')
        if logoutLink.is_displayed():
            logoutLink.click()

    def tearDown(self):
        """
        Put the application back into a known good state on the homepage
        """
        annotations = driver.find_element_by_id('annotations')
        if annotations.is_displayed():
            close = driver.find_element_by_id('closeAnnotations')
            close.click()
        about = driver.find_element_by_class_name('about')
        about.click()
        logoutLink = driver.find_element_by_id('logoutLink')
        if logoutLink.is_displayed():
            logoutLink.click()

    def testToggleLogin(self):
        """
        Checks the "login" link opens the login lightbox.
        """
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        self.assertTrue(loginFormContainer.is_displayed())

    def testCancelLogin(self):
        """
        Ensures that the cancel button in the login form works as expected.
        """
        # Display the form.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        self.assertTrue(loginFormContainer.is_displayed())
        # Fill in some rubbish that we want clearing/cancelling
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        # Now cancel it.
        cancelLink = driver.find_element_by_id('cancelLogin')
        cancelLink.click()
        self.assertFalse(loginFormContainer.is_displayed())
        # Check the old values have gone.
        self.assertEqual('', usernameInput.text)
        self.assertEqual('', passwordInput.text)

    def testSubmitLogin(self):
        """
        Checks that the login form closes with valid input and that the
        logout and user info elements are displayed.
        """
        # Display the form.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        self.assertTrue(loginFormContainer.is_displayed())
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Ensure the correct elements are displayed.
        self.assertFalse(loginLink.is_displayed())
        username = driver.find_element_by_id('username')
        logoutLink = driver.find_element_by_id('logoutLink')
        self.assertTrue(username.is_displayed())
        self.assertTrue(logoutLink.is_displayed())
        self.assertEqual('test', username.text)

    def testSubmitBadLogin(self):
        """
        Checks that an appropriate error message is displayed if bad username
        and password are passed in.
        """
        # Display the form.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        self.assertTrue(loginFormContainer.is_displayed())
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys(str(uuid.uuid4())[:8]);
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id('loginFormError').is_displayed());
        # Ensure the correct elements are displayed.
        loginFormError = driver.find_element_by_id('loginFormError')
        self.assertTrue(loginFormError.is_displayed())

    def testLoginInsistsOnUsernameAndPassword(self):
        """
        Makes sure the login form only works if both username and password are
        supplied.
        """
        # Display the form.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        self.assertTrue(loginFormContainer.is_displayed())
        # Only fill in the username
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        loginFormError = driver.find_element_by_id('loginFormError')
        self.assertTrue(loginFormError.is_displayed())
        # Reset
        cancelLink = driver.find_element_by_id('cancelLogin')
        cancelLink.click()
        # Only fill in the password
        loginLink.click();
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        loginFormError = driver.find_element_by_id('loginFormError')
        self.assertTrue(loginFormError.is_displayed())
        cancelLink.click()

    def testLoginErrorHidesOnCancel(self):
        """
        Ensures the error message is hidden when the form is cancelled.
        """
        # Display the form.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        self.assertTrue(loginFormContainer.is_displayed())
        # Only fill in the username
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        loginFormError = driver.find_element_by_id('loginFormError')
        self.assertTrue(loginFormError.is_displayed())
        # Reset
        cancelLink = driver.find_element_by_id('cancelLogin')
        cancelLink.click()
        # Check the error message is no longer there
        loginLink.click();
        loginFormError = driver.find_element_by_id('loginFormError')
        self.assertFalse(loginFormError.is_displayed())
        cancelLink.click()

    def testLoginErrorHidesOnValidLogin(self):
        """
        Ensures the error message is hidden when the form is correctly
        submitted.
        """
        # Display the form.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        self.assertTrue(loginFormContainer.is_displayed())
        # Only fill in the username
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        loginFormError = driver.find_element_by_id('loginFormError')
        self.assertTrue(loginFormError.is_displayed())
        # Reset
        cancelLink = driver.find_element_by_id('cancelLogin')
        cancelLink.click()
        # Fill in correctly with the username and password
        loginLink.click();
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Logout
        logoutLink = driver.find_element_by_id('logoutLink')
        logoutLink.click()
        # Check the error message is no longer there
        loginLink.click();
        loginFormError = driver.find_element_by_id('loginFormError')
        self.assertFalse(loginFormError.is_displayed())
        cancelLink.click()

    def testLogout(self):
        """
        Makes sure that the logout link works as expected (updates the UI).
        """
        # Display the form.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        self.assertTrue(loginFormContainer.is_displayed())
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Ensure the correct elements are displayed.to be logged in.
        self.assertFalse(loginLink.is_displayed())
        username = driver.find_element_by_id('username')
        logoutLink = driver.find_element_by_id('logoutLink')
        self.assertTrue(username.is_displayed())
        self.assertTrue(logoutLink.is_displayed())
        self.assertEqual('test', username.text)
        # Now log out.
        logoutLink.click();
        self.assertTrue(loginLink.is_displayed())
        self.assertFalse(username.is_displayed())
        self.assertFalse(logoutLink.is_displayed())


class TestBookreaderNavigationLinks(unittest.TestCase):
    """
    Ensures that the menu links at the top of the page display the right
    content when clicked.
    """

    def setUp(self):
        """
        Make sure we're in a good default state.
        """
        annotations = driver.find_element_by_id('annotations')
        if annotations.is_displayed():
            close = driver.find_element_by_id('closeAnnotations')
            close.click()
        about = driver.find_element_by_class_name('about')
        about.click()
        logoutLink = driver.find_element_by_id('logoutLink')
        if logoutLink.is_displayed():
            logoutLink.click()

    def testAboutCSSClick(self):
        """
        Clicking on elements with the "about" class displays the about content.
        """
        # Display something other than the about div.
        colophon = driver.find_element_by_class_name('colophon')
        time.sleep(1)
        colophon.click();
        aboutContainer = driver.find_element_by_id('aboutContainer')
        self.assertFalse(aboutContainer.is_displayed())
        # Click the title and check.
        about = driver.find_element_by_class_name('about')
        about.click()
        time.sleep(1)
        self.assertTrue(aboutContainer.is_displayed())

    def testContentsClick(self):
        """
        Clicking on the Contents link displays the chapter menu.
        """
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        dropdownMenu = driver.find_element_by_class_name('dropdown-menu')
        self.assertTrue(dropdownMenu.is_displayed())

    def testColophonClick(self):
        """
        Clicking on elements with the "colophon" class displays the colophon.
        """
        colophon = driver.find_element_by_class_name('colophon')
        colophon.click();
        colophonContainer = driver.find_element_by_id('colophonContainer')
        self.assertTrue(colophonContainer.is_displayed())

    def testFeedbackClick(self):
        """
        Clicking on the Feedback link displays the feedback widget from
        uservoice.
        """
        feedbackLink = driver.find_element_by_id('feedbackLink')
        feedbackLink.click()
        uvwDialog = driver.find_element_by_id('uvw-dialog')
        self.assertTrue(uvwDialog.is_displayed())
        close = driver.find_element_by_id('uvw-dialog-close')
        close.click()

    def testHelpClick(self):
        """
        Clicking on elements with the "help" class displays the help content.
        """
        helpLink = driver.find_element_by_class_name('help')
        helpLink.click();
        helpContainer = driver.find_element_by_id('helpContainer')
        self.assertTrue(helpContainer.is_displayed())


class TestBookreaderReader(unittest.TestCase):
    """
    Check the various UI elements involved in the reading aspect of the
    application work as expected.
    """

    def tearDown(self):
        """
        Put the application back into a known good state on the homepage
        """
        annotations = driver.find_element_by_id('annotations')
        if annotations.is_displayed():
            close = driver.find_element_by_id('closeAnnotations')
            close.click()
        about = driver.find_element_by_class_name('about')
        about.click()
        logoutLink = driver.find_element_by_id('logoutLink')
        if logoutLink.is_displayed():
            logoutLink.click()

    def testReaderMenuItems(self):
        """
        Ensures that the chapter menu loads the chapters.
        """
        working = driver.find_element_by_id('working')
        oops = driver.find_element_by_id('oops')
        chapter = driver.find_element_by_id('chapter')
        bottomNav = driver.find_element_by_id('bottomNav')
        self.assertFalse(working.is_displayed())
        self.assertFalse(oops.is_displayed())
        self.assertFalse(chapter.is_displayed())
        self.assertFalse(bottomNav.is_displayed())
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        self.assertTrue(working.is_displayed())
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        self.assertFalse(oops.is_displayed())
        self.assertTrue(chapter.is_displayed())
        self.assertTrue(bottomNav.is_displayed())

    def testTagLink(self):
        """
        Ensures that the tag link opens the annotation lightbox.
        """
        # Display the chapter
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())

    def testCloseAnnotationsLightbox(self):
        """
        Ensures that the Annotations lightbox is hidden when the "close" button
        is clicked.
        """
        # Display the chapter
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        close = driver.find_element_by_id('closeAnnotations')
        close.click()
        self.assertFalse(annotations.is_displayed())

    def testNoAnnotationFormForAnonymousUser(self):
        """
        If the user isn't logged in then there shouldn't be an annotation button
        in the annotation lightbox.
        """
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        self.assertFalse(annotateThisButton.is_displayed())

    def testAnnotateThisForLoggedInUser(self):
        """
        Makes sure that if the user is logged in they get to see
        "Annotate this!" button in the annotation lightbox.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        self.assertTrue(annotateThisButton.is_displayed())

    def testAnnotateThisButtonDisplaysAnnotationForm(self):
        """
        Checks that when the "Annotate this!" button is clicked a logged in
        user sees an annotation form.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        self.assertTrue(newCommentForm.is_displayed())
        self.assertFalse(annotateThisButton.is_displayed())

    def testCancelAnnotationHidesAnnotationForm(self):
        """
        Checks that when the annotation form is displayed, if the cancel button
        is clicked then the form is hidden and cleared.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        self.assertTrue(newCommentForm.is_displayed())
        self.assertFalse(annotateThisButton.is_displayed())
        # Add some junk to the form for it to be cleared when cancelled
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys('This is a test comment')
        # Cancel and test.
        cancelAnnotation = driver.find_element_by_id('cancelAnnotation')
        cancelAnnotation.click()
        time.sleep(1)
        self.assertFalse(newCommentForm.is_displayed())
        self.assertTrue(annotateThisButton.is_displayed())
        self.assertEqual('', newCommentContent.text)

    def testCloseAnnotationLightboxHidesAnnotationForm(self):
        """
        Ensures that if the annotation form is displayed but the lightbox is
        then cancelled that the annotation form is hidden when the lightbox is
        triggered again.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        self.assertTrue(newCommentForm.is_displayed())
        self.assertFalse(annotateThisButton.is_displayed())
        # Add some junk to the form for it to be cleared when cancelled
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys('This is a test comment')
        # Close the lightbox.
        close = driver.find_element_by_id('closeAnnotations')
        close.click()
        self.assertFalse(annotations.is_displayed())
        # Re-open the annotations lightbox to ensure it's in a good state.
        tagLink.click()
        self.assertFalse(newCommentForm.is_displayed())
        self.assertTrue(annotateThisButton.is_displayed())
        self.assertEqual('', newCommentContent.text)

    def testPreviousButton(self):
        """
        Ensures the "Previous" button works as expected.
        """
        # Display the glossary
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[12].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        previousLink = driver.find_element_by_id('previousLink')
        nextLink = driver.find_element_by_id('nextLink')
        self.assertTrue(previousLink.is_displayed())
        self.assertFalse(nextLink.is_displayed())
        # Now go visit the next chapter...
        previousLink.click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        chapter = driver.find_element_by_id('chapter')
        # Check the content is on screen and *both* nav buttons visible.
        self.assertTrue(chapter.is_displayed)
        self.assertTrue(previousLink.is_displayed())
        self.assertTrue(nextLink.is_displayed())

    def testNextButton(self):
        """
        Ensures the "Next" button works as expected.
        """
        # Display the prologue
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        previousLink = driver.find_element_by_id('previousLink')
        nextLink = driver.find_element_by_id('nextLink')
        self.assertFalse(previousLink.is_displayed())
        self.assertTrue(nextLink.is_displayed())
        # Now go visit the next chapter...
        nextLink.click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        chapter = driver.find_element_by_id('chapter')
        # Check the content is on screen and *both* nav buttons visible.
        self.assertTrue(chapter.is_displayed)
        self.assertTrue(previousLink.is_displayed())
        self.assertTrue(nextLink.is_displayed())

    def textParticipantCount(self):
        """
        Checks that the participant counter eventually gets displayed.
        """
        # Display the prologue
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_class_name('participantCount').is_displayed() == True)
        # Rather pointless test but it's here for completeness
        participantCount = driver.find_element_by_class_name('participantCount')
        self.assertTrue(participantCount.is_displayed())


class TestBookreaderAnnotate(unittest.TestCase):
    """
    Makes sure the annotation related capabilities work as expected. These
    tests cause state change in Fluidinfo (which is immediately reverted). No
    other way to do it with a single-instance database.
    """

    def setUp(self):
        """
        Clean up the test user's account.
        """
        closeAnnotations = driver.find_element_by_id('closeAnnotations')
        if closeAnnotations.is_displayed():
            closeAnnotations.click()
        about = driver.find_element_by_class_name('about')
        about.click()
        logoutLink = driver.find_element_by_id('logoutLink')
        if logoutLink.is_displayed():
            logoutLink.click()
        # Remove all the test user's "comment" tags.
        fluidinfo.delete('/values', tags=['test/comment',],
            query='has beckyhogge/html')

    def testAddAnnotation(self):
        """
        Tests a simple comment works correctly.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        insightfulComment = str(uuid.uuid4())
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(insightfulComment) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(insightfulComment in commentTagValues.text)

    def testCheckForEmptyComment(self):
        """
        Ensures the annotation form displays the correct error message if the
        user attempts to add an empty comment.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Fail to add any content.
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the error message is correctly displayed.
        newCommentFormError = driver.find_element_by_id('newCommentFormError')
        self.assertTrue(newCommentFormError.is_displayed())

    def testCancelResetsErrorElement(self):
        """
        Makes sure that the error message from submitting an empty comment is
        hidden when the Cancel button is clicked.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Fail to add any content.
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the error message is correctly displayed.
        newCommentFormError = driver.find_element_by_id('newCommentFormError')
        self.assertTrue(newCommentFormError.is_displayed())
        # Ensure the error message is no longer there.
        cancelAnnotation = driver.find_element_by_id('cancelAnnotation')
        cancelAnnotation.click()
        annotateThisButton.click()
        self.assertFalse(newCommentFormError.is_displayed())

    def testSubmitResetsErrorElement(self):
        """
        Ensures the error message from submitting an empty comment is hidden
        when the form is submitted.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Fail to add any content.
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the error message is correctly displayed.
        newCommentFormError = driver.find_element_by_id('newCommentFormError')
        self.assertTrue(newCommentFormError.is_displayed())
        # Now fill in the form and submit.
        insightfulComment = str(uuid.uuid4())
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(insightfulComment) > -1)
        # Check the form doesn't have the error message still displayed.
        annotateThisButton.click()
        self.assertFalse(newCommentFormError.is_displayed())

    def testCloseAnnotationsResetsErrorElement(self):
        """
        Ensures the error message from submitting an empty comment is hidden
        when the annotations lightbox is closed.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Fail to add any content.
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the error message is correctly displayed.
        newCommentFormError = driver.find_element_by_id('newCommentFormError')
        self.assertTrue(newCommentFormError.is_displayed())
        # Close the annotations lightbox
        closeAnnotations = driver.find_element_by_id('closeAnnotations')
        closeAnnotations.click()
        # Show the lightbox again
        tagLink.click()
        # Check the form doesn't have the error message still displayed.
        annotateThisButton.click()
        self.assertFalse(newCommentFormError.is_displayed())

    def testDeleteComment(self):
        """
        Makes sure that comments are deleted properly.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        insightfulComment = str(uuid.uuid4())
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(insightfulComment) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(insightfulComment in commentTagValues.text)
        # Now delete it
        deleteAnnotation = driver.find_element_by_class_name('deleteAnnotation')
        deleteAnnotation.click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(insightfulComment) == -1)
        self.assertFalse(insightfulComment in commentTagValues.text)

    def testMultipleCommentsFromUser(self):
        """
        Makes sure that multiple comments from the same user on an individual
        object are handled properly.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        insightfulComment = str(uuid.uuid4())
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(insightfulComment) > -1)
        # Add a second comment.
        annotateThisButton.click()
        insightfulComment2 = str(uuid.uuid4())
        newCommentContent.send_keys(insightfulComment2)
        submitAnnotation.click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(insightfulComment2) > -1)
        # Check that the new comments are both displayed in the UI
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(insightfulComment in commentTagValues.text)
        self.assertTrue(insightfulComment2 in commentTagValues.text)

    def testDeleteOneOfMultipleComments(self):
        """
        Ensures that a single comment deleted from a list of comments from the
        same user on an individual user are handled properly.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        insightfulComment = str(uuid.uuid4())
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(insightfulComment) > -1)
        # Add a second comment.
        annotateThisButton.click()
        insightfulComment2 = str(uuid.uuid4())
        newCommentContent.send_keys(insightfulComment2)
        submitAnnotation.click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(insightfulComment2) > -1)
        # Check that the new comments are both displayed in the UI
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(insightfulComment in commentTagValues.text)
        self.assertTrue(insightfulComment2 in commentTagValues.text)
        # Now delete the latest comment (insightfulComment2)
        deleteAnnotation = driver.find_element_by_class_name('deleteAnnotation')
        deleteAnnotation.click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(insightfulComment2) == -1)
        self.assertFalse(insightfulComment2 in commentTagValues.text)
        self.assertTrue(insightfulComment in commentTagValues.text)

    def testDisplayURLsAsLinks(self):
        """
        Makes sure 1-n referenced URLs are turned into anchors that are
        correctly truncated.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'https://fluidinfo.com',
            'http://ntoll.org',
            'http://a.very.long/url/indeed?truncated=true'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for three links.
        fluidinfoLink = driver.find_element_by_link_text(
            'fluidinfo.com')
        ntollLink = driver.find_element_by_link_text('ntoll.org')
        truncatedLink = driver.find_element_by_partial_link_text(
            'a.very.long')
        self.assertTrue(fluidinfoLink.is_displayed())
        self.assertTrue(ntollLink.is_displayed())
        self.assertTrue(truncatedLink.is_displayed())
        self.assertEqual('a.very.long/url/indeed?truncated...',
            truncatedLink.text)

    def testDisplayYouTube(self):
        """
        Ensure links to YouTube result in the correct media preview.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'http://www.youtube.com/watch?v=xOYEOw8mrDw'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for embedded media.
        viewMediaLink = commentTagValues.find_element_by_class_name(
            'viewMediaLink')
        viewMediaLink.click()
        mediaContainer = commentTagValues.find_element_by_class_name(
            'mediaContainer')
        self.assertTrue(mediaContainer.is_displayed())
        self.assertEqual(1,
            len(mediaContainer.find_elements_by_tag_name('object')))
        hideMediaLink = mediaContainer.find_element_by_class_name(
            'hideMediaLink')
        self.assertTrue(hideMediaLink.is_displayed())
        hideMediaLink.click()
        self.assertFalse(mediaContainer.is_displayed())
        self.assertTrue(viewMediaLink.is_displayed())

    def testDisplayVimeo(self):
        """
        Ensure links to Vimeo result in the correct media preview.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'http://vimeo.com/15106053'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for embedded media.
        viewMediaLink = commentTagValues.find_element_by_class_name(
            'viewMediaLink')
        viewMediaLink.click()
        mediaContainer = commentTagValues.find_element_by_class_name(
            'mediaContainer')
        self.assertTrue(mediaContainer.is_displayed())
        self.assertEqual(1,
            len(mediaContainer.find_elements_by_tag_name('object')))
        hideMediaLink = mediaContainer.find_element_by_class_name(
            'hideMediaLink')
        self.assertTrue(hideMediaLink.is_displayed())
        hideMediaLink.click()
        self.assertFalse(mediaContainer.is_displayed())
        self.assertTrue(viewMediaLink.is_displayed())

    def testDisplayTwitpic(self):
        """
        Ensure links to Twitpic result in the correct media preview.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'http://twitpic.com/13k8oa'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for embedded media.
        viewMediaLink = commentTagValues.find_element_by_class_name(
            'viewMediaLink')
        viewMediaLink.click()
        mediaContainer = commentTagValues.find_element_by_class_name(
            'mediaContainer')
        self.assertTrue(mediaContainer.is_displayed())
        self.assertEqual(1,
            len(mediaContainer.find_elements_by_tag_name('img')))
        hideMediaLink = mediaContainer.find_element_by_class_name(
            'hideMediaLink')
        self.assertTrue(hideMediaLink.is_displayed())
        hideMediaLink.click()
        self.assertFalse(mediaContainer.is_displayed())
        self.assertTrue(viewMediaLink.is_displayed())

    def testDisplayYFrog(self):
        """
        Ensure links to yFrog result in the correct media preview.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'http://yfrog.com/esbhlhyj'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for embedded media.
        viewMediaLink = commentTagValues.find_element_by_class_name(
            'viewMediaLink')
        viewMediaLink.click()
        mediaContainer = commentTagValues.find_element_by_class_name(
            'mediaContainer')
        self.assertTrue(mediaContainer.is_displayed())
        self.assertEqual(1,
            len(mediaContainer.find_elements_by_tag_name('img')))
        hideMediaLink = mediaContainer.find_element_by_class_name(
            'hideMediaLink')
        self.assertTrue(hideMediaLink.is_displayed())
        hideMediaLink.click()
        self.assertFalse(mediaContainer.is_displayed())
        self.assertTrue(viewMediaLink.is_displayed())

    def testDisplaySoundcloud(self):
        """
        Ensure links to SoundCloud result in the correct media preview.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'http://soundcloud.com/user1194499/tuba'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for embedded media.
        viewMediaLink = commentTagValues.find_element_by_class_name(
            'viewMediaLink')
        viewMediaLink.click()
        mediaContainer = commentTagValues.find_element_by_class_name(
            'mediaContainer')
        self.assertTrue(mediaContainer.is_displayed())
        self.assertEqual(1,
            len(mediaContainer.find_elements_by_tag_name('object')))
        hideMediaLink = mediaContainer.find_element_by_class_name(
            'hideMediaLink')
        self.assertTrue(hideMediaLink.is_displayed())
        hideMediaLink.click()
        self.assertFalse(mediaContainer.is_displayed())
        self.assertTrue(viewMediaLink.is_displayed())

    def testDisplayPNG(self):
        """
        Ensure direct links to a PNG image result in the correct media preview.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'http://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for embedded media.
        viewMediaLink = commentTagValues.find_element_by_class_name(
            'viewMediaLink')
        viewMediaLink.click()
        mediaContainer = commentTagValues.find_element_by_class_name(
            'mediaContainer')
        self.assertTrue(mediaContainer.is_displayed())
        self.assertEqual(1,
            len(mediaContainer.find_elements_by_tag_name('img')))
        hideMediaLink = mediaContainer.find_element_by_class_name(
            'hideMediaLink')
        self.assertTrue(hideMediaLink.is_displayed())
        hideMediaLink.click()
        self.assertFalse(mediaContainer.is_displayed())
        self.assertTrue(viewMediaLink.is_displayed())

    def testDisplayGIF(self):
        """
        Ensure direct links to a GIF image result in the correct media preview.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'http://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Rotating_earth_%28large%29.gif/200px-Rotating_earth_%28large%29.gif'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for embedded media.
        viewMediaLink = commentTagValues.find_element_by_class_name(
            'viewMediaLink')
        viewMediaLink.click()
        mediaContainer = commentTagValues.find_element_by_class_name(
            'mediaContainer')
        self.assertTrue(mediaContainer.is_displayed())
        self.assertEqual(1,
            len(mediaContainer.find_elements_by_tag_name('img')))
        hideMediaLink = mediaContainer.find_element_by_class_name(
            'hideMediaLink')
        self.assertTrue(hideMediaLink.is_displayed())
        hideMediaLink.click()
        self.assertFalse(mediaContainer.is_displayed())
        self.assertTrue(viewMediaLink.is_displayed())

    def testDisplayJPG(self):
        """
        Ensure direct links to a JPG image result in the correct media preview.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'http://upload.wikimedia.org/wikipedia/commons/8/8c/JPEG_example_JPG_RIP_025.jpg'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for embedded media.
        viewMediaLink = commentTagValues.find_element_by_class_name(
            'viewMediaLink')
        viewMediaLink.click()
        mediaContainer = commentTagValues.find_element_by_class_name(
            'mediaContainer')
        self.assertTrue(mediaContainer.is_displayed())
        self.assertEqual(1,
            len(mediaContainer.find_elements_by_tag_name('img')))
        hideMediaLink = mediaContainer.find_element_by_class_name(
            'hideMediaLink')
        self.assertTrue(hideMediaLink.is_displayed())
        hideMediaLink.click()
        self.assertFalse(mediaContainer.is_displayed())
        self.assertTrue(viewMediaLink.is_displayed())

    def testDisplayOGG(self):
        """
        Ensure direct links to an OGG audio file result in the correct media
        preview.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'http://upload.wikimedia.org/wikipedia/commons/b/bd/Rondo_Alla_Turka.ogg'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for embedded media.
        viewMediaLink = commentTagValues.find_element_by_class_name(
            'viewMediaLink')
        viewMediaLink.click()
        mediaContainer = commentTagValues.find_element_by_class_name(
            'mediaContainer')
        self.assertTrue(mediaContainer.is_displayed())
        self.assertEqual(1,
            len(mediaContainer.find_elements_by_tag_name('audio')))
        hideMediaLink = mediaContainer.find_element_by_class_name(
            'hideMediaLink')
        self.assertTrue(hideMediaLink.is_displayed())
        hideMediaLink.click()
        self.assertFalse(mediaContainer.is_displayed())
        self.assertTrue(viewMediaLink.is_displayed())

    def testDisplayMP3(self):
        """
        Ensure direct links to an MP3 audio file result in the correct media
        preview.
        """
        # Log in.
        loginLink = driver.find_element_by_class_name('loginLink')
        loginLink.click();
        loginFormContainer = driver.find_element_by_id('loginFormContainer')
        usernameInput = driver.find_element_by_id('usernameInput')
        passwordInput = driver.find_element_by_id('passwordInput')
        usernameInput.send_keys('test');
        passwordInput.send_keys('test');
        loginForm = driver.find_element_by_id('loginForm')
        loginForm.submit()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('userInfo').is_displayed());
        # Show the annotations lightbox.
        dropdownToggle = driver.find_element_by_class_name('dropdown-toggle')
        dropdownToggle.click()
        chapterLinks = driver.find_elements_by_class_name('chapterLink')
        chapterLinks[0].click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('working').is_displayed() == False)
        tagLink = driver.find_element_by_class_name('tagLink')
        tagLink.click()
        annotations = driver.find_element_by_id('annotations')
        self.assertTrue(annotations.is_displayed())
        annotateThisButton = driver.find_element_by_id('annotateButton')
        annotateThisButton.click()
        newCommentForm = driver.find_element_by_id('newCommentForm')
        # Add a randomly generated test annotation
        uniqueToken = str(uuid.uuid4())
        insightfulComment = ' '.join([
            uniqueToken,
            'http://sampleswap.org/mp3/artist/zentec/audiophyla_valve-320.mp3'
        ])
        newCommentContent = driver.find_element_by_id('newCommentContent')
        newCommentContent.send_keys(insightfulComment)
        submitAnnotation = driver.find_element_by_id('submitAnnotation')
        submitAnnotation.click()
        # Check that the new tag value is displayed in the UI
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_id('commentTagValues').text.find(uniqueToken) > -1)
        commentTagValues = driver.find_element_by_id('commentTagValues')
        self.assertTrue(uniqueToken in commentTagValues.text)
        # Check for embedded media.
        viewMediaLink = commentTagValues.find_element_by_class_name(
            'viewMediaLink')
        viewMediaLink.click()
        mediaContainer = commentTagValues.find_element_by_class_name(
            'mediaContainer')
        self.assertTrue(mediaContainer.is_displayed())
        self.assertEqual(1,
            len(mediaContainer.find_elements_by_tag_name('audio')))
        hideMediaLink = mediaContainer.find_element_by_class_name(
            'hideMediaLink')
        self.assertTrue(hideMediaLink.is_displayed())
        hideMediaLink.click()
        self.assertFalse(mediaContainer.is_displayed())
        self.assertTrue(viewMediaLink.is_displayed())


if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        driver.quit()
