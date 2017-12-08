function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var reviewersInvitedReviewers = new Vue({
    el: "#reviewer-invited-reviewers",
    data: {
        url: window.location.protocol + "//" + window.location.hostname
        + ":" + window.location.port,
        csrftoken: getCookie('csrftoken'),
        invitedReviewers: new Array(0), // Should contain reviewer object /w name, email
        showInvitedReviewers: false
    },
    mounted: function () {
        this.checkForInvitations();
    },
    watch: {
        invitedReviewers: function (invitedRevs) {
            if ( invitedRevs.length > 0 ) {
                this.showInvitedReviewers = true;
            } else {
                this.showInvitedReviewers = false;
            }
        }
    },
    methods: {
        checkForInvitations: function () {
            var vue = this;
            var postUrl = vue.url + "/account/get-invite/";

            var postData = {
                name: document.getElementById("paper-id").innerHTML
            };

            $.ajax({
                type: "POST",
                headers: {'X-CSRFToken': vue.csrftoken},
                url: postUrl,
                data: JSON.stringify(postData),
                error: function (jqXHR) {
                    console.log("An error has occurred while sending the Ajax Request!");
                    console.log(jqXHR.responseType);
                    console.log(jqXHR.responseText);
                },
                success: function (response) {
                    if (response["error"] === undefined) {
                        vue.updateInvitations(response)
                    } else {
                        vue.updateInvitations(null);
                    }
                }
            });
        },
        updateInvitations: function (resp) {
            if (resp === null) {
                this.invitedReviewers = [];
                return;
            }

            var dataObject = JSON.parse(resp);
            for (i = 0; i < dataObject.length; ++i) {
                var obj = {
                    email: dataObject[i]["fields"]["email"],
                    name: dataObject[i]["fields"]["name"]
                };
                this.$set(this.invitedReviewers, i, obj);
            }

        },
        removeInvite: function (i) {
          this.invitedReviewers.splice(i, 1);
        },
        cancelInvite: function (i, email, name) {
            var vue = this;
            var postUrl = this.url + "/account/cancel-invite/";

            var postData = {
                name: name,
                email: email
            };

            var self = this;
            $.ajax({
                type: "POST",
                headers: {'X-CSRFToken': this.csrftoken},
                url: postUrl,
                data: JSON.stringify(postData),
                error: function (jqXHR) {
                    console.log("An error has occurred while sending the Ajax Request!");
                    console.log(jqXHR.responseType);
                    console.log(jqXHR.responseText);
                },
                success: function (response) {
                    if (response["error"] === undefined) {
                        vue.removeInvite(i);
                    } else {
                        console.log(response);
                    }
                }
            });
        }
    }
});

var reviewersControlPanel = new Vue({
    el: "#reviewer-control-panel",
    data: {
        url: "/account/invite/",
        reviewerEmail: "",
        responseMessage: "",
        showAddReviewer: false,
        invitationHasFailed: false,
        invitationHasSucceeded: false
    },
    methods: {
        addReviewer: function () {
            this.showAddReviewer = !this.showAddReviewer
        },
        inviteReviewer: function () {
            var vue = this;
            // Should make ajax call /w email, name and url.
            // Need to implement function that will create an Invitation
            var email = this.reviewerEmail;
            // Get the relative url, skip http:// and https://
            var _index = document.location.href.indexOf("/", 8);
            var url = document.location.href.slice(_index);
            var paperId = document.getElementById("paper-id").innerHTML;
            var csrftoken = getCookie('csrftoken');

            var data = {
                url: url,
                email: email,
                name: paperId
            };

            var postUrl = window.location.protocol + "//" + window.location.hostname
                + ":" + window.location.port + this.url;

            $.ajax({
                type: "POST",
                headers: {'X-CSRFToken': csrftoken},
                url: postUrl,
                data: JSON.stringify(data),
                error: function (jqXHR) {
                    console.log("An error has occurred while sending the Ajax Request!");
                    console.log(jqXHR.responseType);
                    console.log(jqXHR.responseText);
                },
                success: function (response) {
                    if (response["error"] === undefined) {
                        vue.inviteReviewerSuccess(response);
                        reviewersInvitedReviewers.checkForInvitations();
                    } else {
                        vue.inviteReviewerFailure(response)
                    }
                }
            });
        },
        inviteReviewerSuccess: function (data) {
            this.invitationHasFailed = false;
            this.invitationHasSucceeded = true;
            this.responseMessage = data["message"];
            this.showAddReviewer = false;
        },
        inviteReviewerFailure: function (data) {
            this.responseMessage = data["error"];
            this.invitationHasFailed = true;
            this.invitationHasSucceeded = false;
        }
    }
});