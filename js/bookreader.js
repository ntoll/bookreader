/*
Application logic for the simple book-reader application built upon
Fluidinfo.

(c) 2012 Nicholas H.Tollervey.
*/

/*
Returns an appropriately configured object for working with Fluidinfo and
updating the DOM.
*/
var bookreader = function() {
    // The object to be returned.
    var result = {};

    // Various DOM elements that need to be referenced
    var contentBlocks = $(".row");
    var about = $("#about");
    var help = $("#help");
    var examplePopover = $("#examplePopover");
    var oops = $("#oops");
    var working = $("#working");
    var aboutLinks = $(".about");
    var helpLinks = $(".help");
    var chapter = $("#chapter");
    var loginLink = $(".loginLink");
    var logoutLink = $("#logoutLink");
    var loginInfo = $("#loginInfo");
    var userInfo = $(".userInfo");
    var loginForm = $("#loginForm");
    var annotations = $("#annotations");
    var annotateButton = $("#annotateButton");
    var newCommentForm = $("#newCommentForm");
    var newCommentContent = $("#newCommentContent");
    var submitAnnotation = $("#submitAnnotation");
    var cancelAnnotation = $("#cancelAnnotation");
    var nothingTaggedAnonymous = $("#nothingTaggedAnonymous");
    var nothingTaggedLoggedIn = $("#nothingTaggedLoggedIn");
    var fetchingCommentTags = $("#fetchingCommentTags");
    var commentTagValues = $("#commentTagValues");
    var previousLink = $("#previousLink");
    var nextLink = $("#nextLink");

    // The session to be used to connect to Fluidinfo (defaults to anonymous).
    var session = fluidinfo({});
    // Check for local storage of prior session.
    var username = $.jStorage.get("u", false);
    var password = $.jStorage.get("p", false);
    if(username && password) {
        session = fluidinfo({
            username: username,
            password: password
        });
        loginInfo.hide();
        $("#username").html(escape(username));
        userInfo.fadeIn();
    }

    /*
    Logs the user in. Expects an object with a username and password attribute.
    */
    var login = function(){
        var username = $.trim($("#usernameInput").attr("value"));
        var password = $.trim($("#passwordInput").attr("value"));
        $("#usernameInput").attr("value", "");
        $("#passwordInput").attr("value", "");
        // Validate username and password
        if(username === "" || password === "") {
            alert("You must enter both a valid username and password.");
            $("#usernameInput").focus();
            return false;
        }
        session = fluidinfo({
            username: username,
            password: password
        });
        $.jStorage.set('u', username);
        $.jStorage.set('p', password);
        loginInfo.hide();
        $("#username").html(escape(username));
        userInfo.fadeIn();
        loginForm.modal("hide");
        return false;
    };

    /*
    Logs the user out.
    */
    var logout = function() {
        session = fluidinfo({});
        $.jStorage.flush();
        userInfo.hide();
        loginInfo.fadeIn();
        return false;
    };

    /*
    Reports errors to the end user in a nice and friendly way.
    */
    var onError = function(result){
        console.error(result);
        contentBlocks.hide();
        var msg = "<h2>"+result.status+" "+result.statusText+"</h2>";
        msg += "<p>Response headers:</p><dl>"
        for(header in result.headers) {
            msg += "<dt>"+header+"</dt>";
            msg += "<dd>"+result.headers[header]+"</dd>";
        }
        msg += "</dl><p>If this problem persists please use the feedback link on the left hand side of this web-page.</p>";
        $("#errorMessage").html(msg);
        oops.fadeIn("slow");
    };

    /*
    Reports errors to the end user in a nice and friendly way and puts the UI
    into a good state.
    */
    var onAnnotateError = function(result){
        // put the UI into a good state
        annotations.modal("hide");
        resetAnnotationForm();
        newCommentForm.hide();
        annotateButton.show();
        onError(result);
    };

    /*
    Initialises reference popups for a specific reference within a certain
    block.
    */
    var popupInit = function(rawContent, renderedBlock){
        var r = $(rawContent);
        var refName = r.find("a:first").attr("name");
        renderedBlock.find("a").filter(function(){
            return $(this).attr("href").match("#"+refName);
        }).popover({
            placement: "below",
            html: true,
            title: function(){
                return "Reference";
            },
            content: function(){
                return rawContent;
            },
            trigger: "manual"
        }).click(function(){
            var link = $(this);
            if(link.attr("on")){
                link.popover("hide");
                link.removeAttr("on");
            } else {
                link.popover("show");
                link.attr("on", "on");
            }
            return false;
        });
    };

    /*
    Given a chapter name will display and set up the previous/next buttons
    at the bottom of the screen.
    */
    var showNavButtons = function(chapter) {
        // Ordered list of chapters
        var chapterList = [
            "prologue",
            "command",
            "courage",
            "information",
            "kids",
            "anarchists",
            "overload",
            "goolag",
            "ciphers",
            "infowar",
            "epilogue",
            "acknowledgements",
            "glossary"
        ];
        var i;
        var previous;
        var next;
        for(i=0; i<chapterList.length; i++){
            if(chapter === chapterList[i]){
                // Found the current chapter
                previous = i-1;
                next = i+1;
                break;
            }
        }
        if(previous >= 0) {
            previousLink.removeAttr("disabled");
            previousLink.attr("href", "#"+chapterList[previous]);
            previousLink.show();
        } else {
            previousLink.hide();
        }
        if(next <= 12) {
            nextLink.removeAttr("disabled");
            nextLink.attr("href", "#"+chapterList[next]);
            nextLink.show();
        } else {
            nextLink.hide();
        }
    };

    /*
    Given a click event, will get and display the selected chapter.
    */
    var getChapter = function(e) {
        contentBlocks.hide();
        showWorking();
        var chapterHash = e.srcElement.hash.replace("#", "");
        var chapterName = "barefootintocyberspace:" + chapterHash;
        var onSuccess = function(result) {
            // order the results
            var orderedBlocks = result.data.sort(function(a, b){
                return a["beckyhogge/position"] - b["beckyhogge/position"];
            });
            // add them to the DOM
            chapter.empty();
            var i;
            var template = '<div style="margin-bottom: 18px;" class="span13 offset1">{{{block}}}</div><div class="span2"><a href="annotate" class="tagLink"><img src="tags.png" alt="tag" style="opacity: 0.6; filter: alpha(opacity=0.6);"/></a></div>';
            for(i=0; i<orderedBlocks.length; i++){
                block = orderedBlocks[i];
                var renderedBlock = $(Mustache.to_html(template, {block: block["beckyhogge/html"]}));
                chapter.append(renderedBlock);

                /**
                Attach events and popovers
                **/

                // Tag image fadeTo
                renderedBlock.find("img").hover(function(){
                    $(this).fadeTo('fast', 1.0);
                },
                function(){
                    $(this).fadeTo('fast', 0.6);
                });
                // Click event handler for tagging
                var tagLink = renderedBlock.find(".tagLink");
                tagLink.attr("target", block["fluiddb/about"]);
                tagLink.click(showAnnotations);
                // Popovers for references
                var references = block["beckyhogge/references"];
                if(references !== undefined) {
                    var j;
                    for(j=0; j<references.length; j++) {
                        popupInit(references[j], renderedBlock);
                    }
                }
            }
            // ensure the chapter is visible
            contentBlocks.hide();
            chapter.fadeIn("fast");
            // show the nav buttons
            showNavButtons(chapterHash);
            $("#bottomNav").fadeIn("fast");
        };
        var options = {
            select: ["beckyhogge/html", "beckyhogge/position", "beckyhogge/references", "fluiddb/about"],
            where: 'beckyhogge/parent ="'+chapterName+'"',
            onSuccess: onSuccess,
            onError: onError
        };
        session.query(options);
    };

    /*
    Displays the about page (the first thing the user sees).
    */
    var showAbout = function(){
        contentBlocks.hide();
        about.fadeIn("fast");
        return false;
    };

    /*
    Displays the help page.
    */
    var showHelp = function(){
        contentBlocks.hide();
        help.fadeIn("fast");
        return false;
    };

    /*
    Shows the working message.
    */
    var showWorking = function(){
        contentBlocks.hide();
        working.fadeIn("fast");
    };

    /*
    Displays the login widget.
    */
    var showLogin = function(){
        loginForm.modal("show");
        $("#usernameInput").focus();
    };

    /*
    Returns an appropriately rendered element to insert into the DOM.
    */
    var createAnnotation = function(annotation){
        var uniqueID = Mustache.to_html("{{about}}-{{author}}-{{timestamp}}", annotation).replace(/\:/g, "_");
        var template = '<div style="border-bottom: 1px solid #EEE; margin-bottom: 10px; padding-bottom: 10px;" id="{{id}}"><div><strong>{{author}}</strong> - {{date}} {{#delete}}<a class="deleteAnnotation" href="#"><small>delete</small></a>{{/delete}}</div><div>{{val}}</div></div>';
        annotation["id"] = uniqueID;
        annotation["date"] = new Date(parseInt(annotation.timestamp)).toDateString();
        annotation["delete"] = annotation.author === session.username;
        var result = $(Mustache.to_html(template, annotation));
        // Add a delete event handler
        var deleteAnchor = result.find(".deleteAnnotation");
        deleteAnchor.click(function(e){
            deleteAnchor.attr("disabled", "disabled");
            session.api.del({
                path: "tags/"+annotation.path,
                onSuccess: function(result){
                    var removeMe = $("#"+uniqueID);
                    if(commentTagValues[0].childElementCount === 1){
                        removeMe.remove();
                        nothingTaggedLoggedIn.fadeIn("fast");
                    } else {
                        removeMe.hide("fast", function() {
                            removeMe.remove();
                        });
                    }
                },
                onError: function(result){
                    deleteAnchor.removeAttr("disabled");
                    onAnnotateError(result);
                }
            });
            return false;
        });
        return result;
    }


    /*
    Displays the comments annotated onto the object.
    */
    var showComments = function(result){
        var commentList = [];
        for(comment in result.data){
            if(comment === "id" || comment === "fluiddb/about") {
                continue;
            }
            var splitName = comment.split("/");
            var commentValue = result.data[comment];
            commentList.push({
                author: splitName[0],
                timestamp: splitName[2],
                val: commentValue,
                about: result.data["fluiddb/about"],
                path: comment
            });
        }
        fetchingCommentTags.hide();
        if(commentList.length === 0) {
            if(session.username){
                nothingTaggedLoggedIn.fadeIn("fast");
            } else {
                nothingTaggedAnonymous.fadeIn("fast");
            }
        } else {
            var orderedComments = commentList.sort(function(a, b){
                return b.timestamp - a.timestamp;
            });
            var i;
            for(i=0; i<orderedComments.length; i++){
                var renderedComment = createAnnotation(orderedComments[i]);
                commentTagValues.append(renderedComment);
            }
            commentTagValues.fadeIn("fast");
        }
    };

    /*
    Handles the annotation of a block.
    */
    var showAnnotations = function(e){
        commentTagValues.empty().hide();
        nothingTaggedAnonymous.hide();
        nothingTaggedLoggedIn.hide();
        fetchingCommentTags.show();
        if(session.username === undefined){
            $("#newCommentContainer").hide();
        } else {
            $("#newCommentContainer").show();
        }
        var aboutBlock = e.currentTarget.target;
        $("#parentObject").attr("value", aboutBlock);
        annotations.modal("show");
        var onSuccess = function(result){
            var commentTags = ['fluiddb/about'];
            var i;
            var r = /^\w+\/comments\/\d+$/;
            for(i=0; i<result.data.tagPaths.length; i++) {
                var tag = result.data.tagPaths[i];
                if(tag.match(r)){
                    // it must be a comment tag path.
                    commentTags.push(tag);
                }
            }
            var tagValOptions = {
                about: aboutBlock,
                select: commentTags,
                onSuccess: showComments,
                onError: onAnnotateError
            }
            session.getObject(tagValOptions);
        }
        session.api.get({
            path: "about/"+aboutBlock,
            onSuccess: onSuccess,
            onError: onAnnotateError
        });
        return false;
    };

    /*
    Puts the annotation form into a good state.
    */
    var resetAnnotationForm = function(){
        submitAnnotation.button("reset");
        newCommentContent.removeAttr("disabled");
        cancelAnnotation.removeAttr("disabled");
        newCommentContent[0].value = "";
    }

    /*
    Handles the submission of a new annotation.
    */
    var addAnnotation = function(e){
        // Put the UI in a safe state.
        submitAnnotation.button("loading");
        newCommentContent.attr("disabled", "disabled");
        cancelAnnotation.attr("disabled", "disabled");
        // Validate the input.
        var rawInput = newCommentContent[0].value;
        var strippedInput = rawInput.replace(/^\s*/, "").replace(/\s*$/, "");
        if(strippedInput === "") {
            alert("You must enter something to annotate!");
            resetAnnotationForm();
            newCommentContent.focus();
            return false;
        }
        // Create a new annotation object.
        var user = session.username;
        var timestampValue = new Date().valueOf();
        var tagName = user+"/comments";
        var commentValue = strippedInput;
        var parentBlockValue = $("#parentObject").attr("value");

        var onSuccess = function(result){
            // add to the list of annotations
            var newAnnotation = createAnnotation({
                about: parentBlockValue,
                author: user,
                timestamp: timestampValue,
                val: commentValue,
                path: tagName
            });
            commentTagValues.prepend(newAnnotation);
            newAnnotation.fadeIn("fast");
            // Update the UI to a new good state.
            commentTagValues.show();
            nothingTaggedLoggedIn.hide();
            resetAnnotationForm();
            newCommentForm.hide();
            annotateButton.show();
        };
        var values = {}
        values[tagName] = commentValue;

        var options = {
            values: values,
            about: parentBlockValue,
            onSuccess: onSuccess,
            onError: onAnnotateError
        }
        session.tag(options);
        return false;
    };

    /*
    Initialises the DOM and sets everything up.
    */
    result.init = function(){
        $('#topbar').dropdown();
        aboutLinks.click(showAbout);
        helpLinks.click(showHelp);
        loginForm.modal({
            backdrop: "static"
        });
        annotations.modal({
            backdrop: "static"
        });
        $("#cancelLogin").click(function(){
            loginForm.modal("hide");
        });
        $("#closeAnnotations").click(function(){
            annotations.modal("hide");
            newCommentForm.hide();
            annotateButton.show();
        });
        loginLink.click(showLogin);
        logoutLink.click(logout);
        loginForm.submit(login);
        $(".chapterLink").click(getChapter);
        previousLink.click(getChapter);
        nextLink.click(getChapter);
        annotateButton.click(function(){
            annotateButton.hide();
            newCommentForm.fadeIn("fast");
            newCommentContent.focus();
        });
        cancelAnnotation.click(function(){
            newCommentForm.hide();
            annotateButton.fadeIn(50);
        });
        newCommentForm.submit(addAnnotation);
        examplePopover.popover({
            placement: "below",
            html: true,
            title: function(){
                return "An Example Reference";
            },
            content: function(){
                return '<p>Reference information will be displayed here and <a href="http://barefootintocyberspace.com/book/" target="_new">may contain links</a>.</p>';
            },
            trigger: "manual"
        });
        examplePopover.click(function(){
            var link = $(this);
            if(link.attr("on")){
                link.popover("hide");
                link.removeAttr("on");
            } else {
                link.popover("show");
                link.attr("on", "on");
            }
            return false;
        });
    };

    return result;
};
