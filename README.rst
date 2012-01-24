Bookreader
==========

A simple web-based social book reading application that sits upon Fluidinfo.

It's also an example from the O'Reilly book "Getting Started with Fluidinfo".

Getting Started
---------------

Once you have cloned this repos you need to issue the following commands in
the project root::

  $ git submodule init
  $ git submodule update

You'll then find the fluidinfo.js source in the js/fi directory and the
mustache.js source in the js/mustache directory (relative to the project root).

Running the Application
-----------------------

Don't try to load the application into your browser directly from the
filesystem. Modern browsers don't allow CORS (cross-origin resource sharing)
requests to succeed unless the original page is loaded from a domain (like
localhost). To simplify things I've created a simple web-server that'll serve
the application on ``http://localhost:8080`` (you'll need to have Python
installed for this to work). To make it work open a terminal, navigate to the
root of this project and type::

    $ ./scripts/runserver.py

(The dollar "$" represents the terminal prompt. You don't have to type this.)

Running the Test Suite
----------------------

The test-suite uses Selenium (http://seleniumhq.org/), Python and Firefox.
Assuming you have Python and Firefox installed already it's possible to install
Selenium with the following command::

    $ pip install selenium

You should then start the local server (as described above) then switch to
another terminal window and run the test suite::

    $ python test/run.py

An instance of the Firefox browser will launch (under the control of Selenium)
and the progress of the test suite will be displayed in the terminal window.
Since, this is a "live" test with real network calls the time the test suite
takes to complete depends upon the latency of your network connection.

Project Geography
-----------------

This is a very simple project with few dependencies. All the HTML is contained
within the ``index.html`` file. The application logic is contained within the
``js/bookreader.js`` file. I sourced the content from
http://barefootintocyberspace.com/book/hypertext/ and scraped it into the file
``data/barefoot.json``. This project is released under a FLOSS license (see
the ``LICENSE`` file) so please fork it and adapt to your purposes.
