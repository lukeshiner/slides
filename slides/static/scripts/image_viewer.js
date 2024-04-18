const slideNumbers = JSON.parse(document.getElementById('slideNumbers').textContent);
var currentSlideIndex = 0;
var scrollPosition = 0;

function getImageURL(slidePk) {
    return loadImageURL + "?slide_pk=" + slidePk;
}

function getImage(slidePk) {
    currentSlideIndex = slideNumbers.indexOf(slidePk);
    $.get(getImageURL(slidePk), function (data, status) {
        loadImage(data);
    });
}

function loadImage(data) {
    $("#mainImage").attr("src", data['slide']["slide_url"]);
    boxNumber = data['box_number'];
    previousSlideNumber = data['previous_slide_number'];
    nextSlideNumber = data['next_slide_number'];
    $("#slideNumber").html(currentSlideIndex + 1);
    $("#slideCount").html(slideNumbers.length);
    $("#slideNotes").html(data['slide']['notes']);
    $("#slideDate").html(data['slide']['date']);
    $("#slideName").html(data['slide']['name']);
}

function openFullscreen() {
    var elem = $("#imageBox").get(0);
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) { /* Safari */
        elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { /* IE11 */
        elem.msRequestFullscreen();
    }
    $("#mainImage").off("click").click(closeFullscreen);
    $("#imageInfo").addClass("d-none");
    $("#fullscreenButton").html('<i class="bi bi-fullscreen-exit"></i>');
}

function closeFullscreen() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.webkitExitFullscreen) { /* Safari */
        document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) { /* IE11 */
        document.msExitFullscreen();
    }
    $("#mainImage").off("click").click(openFullscreen);
    $("#fullscreenButton").click(openFullscreen);
    $("#imageInfo").removeClass("d-none");
    $("#fullscreenButton").html('<i class="bi bi-arrows-fullscreen"></i>');
}

function enableFullscreen() {
    $("#mainImage").off("click").click(openFullscreen);
    $("#fullscreenButton").click(openFullscreen);
}

function showImageViewer() {
    scrollPosition = $(window).scrollTop();
    $(".main").addClass("d-none");
    $("#imageViewer").removeClass("d-none");
}

function hideImageViewer() {
    closeFullscreen();
    $("#imageViewer").addClass("d-none");
    $(".main").removeClass("d-none");
    $(window).scrollTop(scrollPosition);
}

function enableClose() {
    $("#closeImageViewer").click(function () {
        hideImageViewer();
    });
}

function enableImageOpen() {
    $(".imageThumb").click(function () {
        var slidePk = $(this).data("slidePk");
        showImageViewer();
        getImage(slidePk);
    });
}

function goToPreviousSlide() {
    if (currentSlideIndex == 0) {
        currentSlideIndex = slideNumbers.length - 1
    } else {
        currentSlideIndex -= 1;
    }
    getImage(slideNumbers[currentSlideIndex]);
}

function goToNextSlide() {
    if (currentSlideIndex == slideNumbers.length - 1) {
        currentSlideIndex = 0;
    } else {
        currentSlideIndex += 1;
    }
    getImage(slideNumbers[currentSlideIndex]);
}

function enableNavigation() {
    $("#previousSlideButton").click(goToPreviousSlide);
    $("#nextSlideButton").click(goToNextSlide);
    $("body").keydown(function (e) {
        if (e.keyCode == 37) { // left arrow key
            goToPreviousSlide();
        }
        else if (e.keyCode == 39) { // right arrow key
            goToNextSlide();
        }
    });
}

$(document).ready(function () {
    enableFullscreen();
    enableClose();
    enableNavigation();
    enableImageOpen();
});