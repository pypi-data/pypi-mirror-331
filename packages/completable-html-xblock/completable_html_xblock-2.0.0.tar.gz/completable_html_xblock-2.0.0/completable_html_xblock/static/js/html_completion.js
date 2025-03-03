function HTML5CompletionXBlock(runtime, element, data) {
    /*
    Add `submitCompletion` function to XBlock.
    You can invoke it with `document.getElementsByClassName("xblock-student_view-completable_html5")[0].submitCompletion();`.
     */
    element.submitCompletion = function () {
        var handlerUrl = runtime.handlerUrl(element, 'complete');
        $.post(handlerUrl, JSON.stringify(data));
    };
}
