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

    // The tag being used to store comments
    var commentTag = "comment"

    // Used to delineate individual comments in the commentTag
    var splitChar = "\n\u00B6\n";

    // Used to hold the list of comments on the block object that has focus
    var myComments = [];

    // Used to match tag paths
    var commentMatcher = new RegExp("^\\w+\\/"+commentTag+"$");

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

    // An object that defines how to process embedded links when displaying
    // comments.
    var embeddedLinks = {
        "youtube.com": function(raw) {
            var regex = /v=[a-zA-Z0-9]+/;
            var match = raw.match(regex);
            var template= '<object width="480" height="244"><param name="movie" value="http://www.youtube.com/v/{{id}}?version=3&rel=0&enablejsapi=1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/{{id}}?version=3&rel=0&enablejsapi=1" type="application/x-shockwave-flash" width="480" height="244" allowscriptaccess="always" allowfullscreen="true"></embed></object>'
            if(match){
                var id = match[0].replace("v=", "");
                return Mustache.to_html(template, {id: id});
            } else {
                return "";
            }
        },
        "vimeo.com": function(raw) {
            var regex = /vimeo.com\/[0-9]+$/g;
            var match = raw.match(regex);
            var template = '<object width="325" height="244"><param name="allowfullscreen" value="true" /><param name="allowscriptaccess" value="always" /><param name="movie" value="http://vimeo.com/moogaloop.swf?clip_id={{id}}&server=vimeo.com&show_title=0&show_byline=0&show_portrait=0&color=00adef&fullscreen=1&autoplay=0&loop=0" /><embed src="http://vimeo.com/moogaloop.swf?clip_id={{id}}&server=vimeo.com&show_title=0&show_byline=0&show_portrait=0&color=00adef&fullscreen=1&autoplay=0&loop=0" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="325" height="244"></embed></object>';
            if(match){
                var id = match[0].replace("vimeo.com/", "");
                return Mustache.to_html(template, {id: id});
            } else {
                return "";
            }
        },
        "twitpic.com": function(raw) {
            var regex = /twitpic.com\/[\w]+$/g;
            var match = raw.match(regex);
            var template = '<img src="http://twitpic.com/show/full/{{id}}" alt="Twitpic image {{id}}" style="max-width: 400px;"/>';
            if(match){
                var id = match[0].replace("twitpic.com/", "");
                return Mustache.to_html(template, {id: id});
            } else {
                return "";
            }
        },
        "yfrog.com": function(raw) {
            var template = '<img src="{{url}}" alt="yfrog image" style="max-width: 400px;"/>';
            return Mustache.to_html(template, {url: raw+":medium"});
        },
        "(\\.png|\\.gif|\\.jpg)$": function(raw) {
            var template = '<img src="{{url}}" alt="yfrog image" style="max-width: 400px;"/>';
            return Mustache.to_html(template, {url: raw});
        },
        "(\\.ogg|\\.mp3)$": function(raw) {
            var template = '<audio controls><source src="{{url}}"/></audio>';
            return Mustache.to_html(template, {url: raw});
        },
        "soundcloud.com": function(raw) {
            var template = '<object height="81" width="100%" id="{{id}}" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"><param name="movie" value="http://player.soundcloud.com/player.swf?url={{url}}&enable_api=true&object_id=yourPlayerId"></param><param name="allowscriptaccess" value="always"></param> <embed allowscriptaccess="always" height="81" src="http://player.soundcloud.com/player.swf?url={{url}}&enable_api=true&object_id=yourPlayerId" type="application/x-shockwave-flash" width="100%" name="{{id}}"></embed> </object>';
            var id = uuid();
            return Mustache.to_html(template, {url: encodeURIComponent(raw), id: id});
        }
    };

    // Various DOM elements that need to be referenced
    var contentBlocks = $(".row");
    var about = $("#aboutContainer");
    var colophon = $("#colophonContainer");
    var help = $("#helpContainer");
    var examplePopover = $("#examplePopover");
    var oops = $("#oops");
    var working = $("#working");
    var aboutLinks = $(".about");
    var colophonLinks = $(".colophon");
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
            $("#loginFormError").fadeIn("fast");
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
        $("#loginFormError").hide();
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
    Updates the participant counter for the object identified by the passed in
    about value.
    */
    var countParticipantComments = function(about){
        // Find the number of participants commenting on the block of
        // text.
        var participantOptions = {
            path: "about/" + about,
            onSuccess: function(result){
                // grab the users from the comment tags
                var counter = 0;
                for(i in result.data.tagPaths){
                    var pathName = result.data.tagPaths[i];
                    if(pathName.match(commentMatcher)) {
                        counter++;
                    }
                }
                // update UI
                if(counter>0) {
                    $("#"+result.data["id"]).html(counter).fadeIn("fast");
                } else {
                    $("#"+result.data["id"]).html("");
                }
            }
        };
        session.api.get(participantOptions);
    }

    /*
    Given a click event, will get and display the selected chapter.
    */
    var getChapter = function(e) {
        $(".popover").remove();
        contentBlocks.hide();
        showWorking();
        var chapterHash = e.target.hash.replace("#", "");
        var chapterName = "barefootintocyberspace:" + chapterHash;
        var onSuccess = function(result) {
            // order the results
            var orderedBlocks = result.data.sort(function(a, b){
                return a["beckyhogge/position"] - b["beckyhogge/position"];
            });
            // add them to the DOM
            chapter.empty();
            var i;
            var template = '<div style="margin-bottom: 18px;" class="span11 offset2 textBlock">{{{block}}}</div><div class="span3"><a href="annotate" class="tagLink"><img src="images/tags.png" alt="tag" style="opacity: 0.6; filter: alpha(opacity=0.6); vertical-align: middle"/></a><span style="margin-bottom: 4px; color: #999;" id="{{id}}"><small style="color: #999;">&nbsp;</small></span></div>';
            for(i=0; i<orderedBlocks.length; i++){
                block = orderedBlocks[i];
                var id = block["id"];
                var renderedBlock = $(Mustache.to_html(template, {block: block["beckyhogge/html"], id: id}));
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
                countParticipantComments(block["fluiddb/about"]);
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
        $(".popover").remove();
        contentBlocks.hide();
        about.fadeIn("fast");
        document.location.hash = "#about";
        return false;
    };

    /*
    Displays the colophon page (containing technical details).
    */
    var showColophon = function(){
        $(".popover").remove();
        contentBlocks.hide();
        colophon.fadeIn("fast");
        document.location.hash = "#colophon";
        return false;
    };

    /*
    Displays the help page.
    */
    var showHelp = function(){
        $(".popover").remove();
        contentBlocks.hide();
        help.fadeIn("fast");
        document.location.hash = "#help";
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
        return false;
    };

    /*
    Returns a list of objects representing comments from a string.
    */
    var extractComments = function(comments, author, about) {
        var result = [];
        if(typeof(comments) !== "string") {
            return [{author: author,
                    timestamp: new Date(0),
                    val: "Unreadable comment.",
                    about: about
                    }];
        }
        if(comments.indexOf(splitChar)<0){
            return [{author: author,
                    timestamp: new Date(0),
                    val: comments,
                    about: about
                    }];
        }
        var rawCommentList = comments.split(splitChar);
        var i;
        for(i=0; i<rawCommentList.length; i++){
            var rawComment = rawCommentList[i];
            if(rawComment.length > 31) {
                // UTC strings are always 29 characters long
                var dateString = rawComment.slice(0, 29);
                // Drop the newline at position 30
                var commentString = rawComment.slice(30);
                var commentDate = new Date(dateString);
                result.push({
                    author: author,
                    timestamp: commentDate,
                    val: commentString,
                    about: about
                })
            }
        }
        return result;
    }

    /*
    Packs a list of comments into a string representation
    */
    var packComments = function(comments) {
        var commentList = [];
        var i;
        for(i=0; i<comments.length; i++){
            var commentObject = comments[i];
            var commentAsString = commentObject.timestamp.toUTCString() + "\n" + commentObject.val;
            commentList.push(commentAsString);
        }
        if(commentList.length === 1) {
            return commentList[0]+splitChar;
        } else {
            return commentList.join(splitChar);
        }
    }

    /**
    Returns a randomly generated string that looks like a UUID4 (but isn't).
    Based upon the example here: http://bit.ly/rh378d
    */
    var uuid = function() {
        var S4 = function() {
            return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
        };
        return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
    };

    /*
    Given a list of comments, saves this under the user's commentTag.
    */
    var saveComments = function(options) {
        var stringValue = packComments(options.commentList);
        var tagPath = options.author+"/"+commentTag;
        var values = {};
        values[tagPath] = stringValue;
        var tagOptions = {
            values: values,
            about: options.about,
            onSuccess: function(result){
                myComments = options.commentList;
                options.onSuccess(result);
                countParticipantComments(options.about);
            },
            onError: options.onError
        }
        session.tag(tagOptions);
    };

    var postProcessComment = function(raw) {
        if(raw.length === 0) {
            return "<emphasis>Empty comment.</emphasis>";
        }
        var htmlSafe = Mustache.to_html("{{raw}}", {raw: raw});
        htmlSafe = htmlSafe.replace(/\n/g, "<br/>");
        // Check for URLs in the content
        var urlRe = /(https?):\/\/[-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|]/g;
        var match = htmlSafe.match(urlRe);
        // mediaList will contain any linked media to be embedded into the
        // value of the comment.
        var mediaList = [];
        if(match){
            var i;
            for(i=0; i<match.length; i++) {
                var url = match[i];
                // replace with anchor element
                var urlName = url.replace("http://", "");
                if(urlName.length>32){
                    urlName = url.slice(0, 32)+"...";
                }
                var a_template = '<a href="{{url}}" target="_new">{{urlName}}</a>';
                var anchor = Mustache.to_html(a_template, {url: url, urlName: urlName});
                htmlSafe = htmlSafe.replace(url, anchor);
                // add media to bottom of comment if from Youtube etc...
                var service;
                for(service in embeddedLinks){
                    var func = embeddedLinks[service];
                    var serviceMatch = url.match(new RegExp(service));
                    if(serviceMatch) {
                        mediaList.push(func(url));
                        break;
                    }
                }
            }
        }
        var mediaContainer = null;
        if(mediaList.length>0) {
            // Post process the media
            var mediaTemplate = '<div id="{{viewID}}"><a href="#">View media</a></div><div id="{{mediaID}}" style="display: none;"><p><a href="#" id="{{mediaID}}-toggle">Hide media</a></p><div id="{{mediaID}}-content"></div></div>';
            var viewID = uuid();
            var mediaID = uuid();
            var mediaContainer = $(Mustache.to_html(mediaTemplate, {viewID: viewID, mediaID: mediaID}));
            var viewDiv = mediaContainer.first();
            var mediaDiv = mediaContainer.last();
            viewDiv.find("a").click(function(){
                viewDiv.hide();
                mediaDiv.fadeIn("fast");
                return false;
            });
            mediaDiv.find("#"+mediaID+"-toggle").click(function(){
                mediaDiv.hide();
                viewDiv.fadeIn("fast");
                return false;
            });
            var i;
            for(i=0; i< mediaList.length; i++) {
                var media = mediaList[i];
                mediaDiv.append($(media));
            }
        }
        return $("<div/>").html(htmlSafe).append(mediaContainer);
    };

    /*
    Returns an appropriately rendered element to insert into the DOM.
    */
    var createAnnotation = function(annotation){
        var uniqueID = uuid();
        var template = '<div style="border-bottom: 1px solid #EEE; margin-bottom: 10px; padding-bottom: 10px;" id="{{id}}"><div><strong>{{author}}</strong> - {{date}} {{#delete}}<a class="deleteAnnotation" href="#"><small>delete</small></a>{{/delete}}</div></div>';
        annotation.id = uniqueID;
        // Check for unknown dates (represented by timestamp 0)
        if(annotation.timestamp.valueOf() === new Date(0).valueOf()) {
            annotation.date = "Unknown date";
        } else {
            annotation.date = Mustache.to_html("{{date}} - {{time}}", {
                date: annotation.timestamp.toLocaleDateString(),
                time: annotation.timestamp.toLocaleTimeString()
            });
        }
        annotation["delete"] = annotation.author === session.username;
        var valueElement = postProcessComment(annotation.val);
        var result = $(Mustache.to_html(template, annotation));
        result.append(valueElement);
        // Add a delete event handler
        var deleteAnchor = result.find(".deleteAnnotation");
        deleteAnchor.click(function(e){
            deleteAnchor.attr("disabled", "disabled");
            revisedCommentList = $.grep(myComments, function(val){
                return val.timestamp.valueOf() != annotation.timestamp.valueOf();
            });
            var cleanUpDelete = function() {
                var removeMe = $("#"+uniqueID);
                if(commentTagValues[0].childElementCount === 1){
                    removeMe.remove();
                    nothingTaggedLoggedIn.fadeIn("fast");
                } else {
                    removeMe.hide("fast", function() {
                        removeMe.remove();
                    });
                }
            }
            if(revisedCommentList.length > 0){
                var options = {
                    commentList: revisedCommentList,
                    author: annotation.author,
                    about: annotation.about,
                    onSuccess: function(result){
                        cleanUpDelete();
                    },
                    onError: function(result){
                        deleteAnchor.removeAttr("disabled");
                        onAnnotateError(result);
                    }
                };
                saveComments(options);
            } else {
                session.api.del({
                    path: ["about", annotation.about, annotation.author, commentTag],
                    onSuccess: function(result){
                        myComments = [];
                        cleanUpDelete();
                        countParticipantComments(annotation.about);
                    },
                    onError: function(result){
                        deleteAnchor.removeAttr("disabled");
                        onAnnotateError(result);
                    }
                });
            }
            return false;
        });
        return result;
    }

    /*
    Displays the comments annotated onto the object.
    */
    var showComments = function(result){
        myComments = []; // reset state
        var commentList = [];
        for(comment in result.data){
            if(comment.match(commentMatcher)) {
                var author = comment.split("/")[0];
                var extractedComments = extractComments(result.data[comment], author, result.data["fluiddb/about"]);
                if(author === session.username){
                    // The current user has left comments.
                    myComments = extractedComments;
                }
                $.merge(commentList, extractedComments);
            }
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
                return b.timestamp.valueOf() - a.timestamp.valueOf();
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
            for(i=0; i<result.data.tagPaths.length; i++) {
                var tag = result.data.tagPaths[i];
                if(tag.match(commentMatcher)){
                    // it must be a comment tag path.
                    commentTags.push(tag);
                }
            }
            if(commentTags.length > 1) {
                // only make the request if there are matching tag.
                var tagValOptions = {
                    about: aboutBlock,
                    select: commentTags,
                    onSuccess: showComments,
                    onError: onAnnotateError
                }
                session.getObject(tagValOptions);
            } else {
                // there were no matching tags so fake an empty result.
                showComments({data:[]});
            }
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
        $("#newCommentFormError").hide();
        // Validate the input.
        var rawInput = newCommentContent[0].value;
        var strippedInput = rawInput.replace(/^\s*/, "").replace(/\s*$/, "");
        if(strippedInput === "") {
            $("#newCommentFormError").fadeIn("fast");
            resetAnnotationForm();
            newCommentContent.focus();
            return false;
        }
        // Create a new annotation object.
        var user = session.username;
        var timestampValue = new Date();
        var commentValue = strippedInput;
        var parentBlockValue = $("#parentObject").attr("value");
        var newCommentObject = {
            author: user,
            timestamp: timestampValue,
            val: commentValue,
            about: parentBlockValue
        };
        myComments.push(newCommentObject);
        var options = {
            commentList: myComments,
            author: session.username,
            about: parentBlockValue,
            onSuccess: function(result){
                // add to the list of annotations
                var newAnnotation = createAnnotation(newCommentObject);
                commentTagValues.prepend(newAnnotation);
                newAnnotation.fadeIn("fast");
                // Update the UI to a new good state.
                commentTagValues.show();
                nothingTaggedLoggedIn.hide();
                resetAnnotationForm();
                newCommentForm.hide();
                annotateButton.show();
            },
            onError: onAnnotateError
        }
        saveComments(options);
        return false;
    };

    /*
    Initialises the DOM and sets everything up.
    */
    result.init = function(){
        $("#topbar").dropdown();
        $(".alert-message").alert();
        aboutLinks.click(showAbout);
        colophonLinks.click(showColophon);
        helpLinks.click(showHelp);
        loginForm.modal({
            backdrop: "static"
        });
        annotations.modal({
            backdrop: "static"
        });
        $("#cancelLogin").click(function(){
            $("#loginFormError").hide();
            loginForm.modal("hide");
        });
        $("#closeAnnotations").click(function(){
            annotations.modal("hide");
            newCommentForm.hide();
            annotateButton.show();
        });
        loginLink.click(showLogin);
        logoutLink.click(logout);
        loginForm.unbind('submit').submit(login);
        $(".chapterLink").click(getChapter);
        previousLink.click(getChapter);
        nextLink.click(getChapter);
        annotateButton.click(function(){
            annotateButton.hide();
            newCommentForm.fadeIn("fast");
            newCommentContent.focus();
        });
        cancelAnnotation.click(function(){
            $("#newCommentFormError").hide();
            newCommentForm.hide();
            annotateButton.fadeIn(50);
        });
        newCommentForm.unbind("submit").submit(addAnnotation);
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

        var hash = document.location.hash;
        if(hash) {
            var i;
            var hashName = hash.replace("#", "");
            for(i=0; i<chapterList.length; i++){
                if(hashName === chapterList[i]){
                    getChapter({target: {hash: hash}});
                    return;
                }
            }
            switch(hash){
                case "#about":
                    showAbout();
                    break;
                case "#colophon":
                    showColophon();
                    break;
                case "#help":
                    showHelp();
                    break;
            };
        }
    };

    return result;
};
