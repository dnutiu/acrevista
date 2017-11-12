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

// TODO: Implement pending invitations and a way to cancel them.
new Vue({
    el: "#reviewer-control-panel",
    data: {
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
            vue = this;
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
                + ":" + window.location.port + "/account/invite/";

            // Also make modal that shows ok or error.
            $.ajax({
                type: "POST",
                headers: {'X-CSRFToken': csrftoken},
                url: postUrl,
                data: JSON.stringify(data),
                // success: success,
                error: function (jqXHR) {
                    console.log("An error has occurred while sending the Ajax Request!");
                    console.log(jqXHR.responseType);
                    console.log(jqXHR.responseText);
                },
                success: function (response) {
                    if (response["error"] === undefined) {
                        vue.inviteReviewerSuccess(response)
                    } else {
                        vue.inviteReviewerFailure(response)
                    }
                }
            });
        },
        inviteReviewerSuccess: function (data) {
            console.log("Success!");
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