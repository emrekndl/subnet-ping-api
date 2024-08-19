document.addEventListener("DOMContentLoaded", (event) => { document.body.addEventListener('htmx:beforeSwap', function (evt) {
      if (evt.detail.xhr.status == 204) {
        evt.detail.shouldSwap = true;
      }
    });
})

let notifications = new Notifications();
notifications.init();
//   document.addEventListener('htmx:afterRequest', function(event) {
//     if (event.detail.requestConfig.verb === 'post' && event.detail.pathInfo.requestPath === '/api/ip/') {
//         htmx.get("{% url 'index' %}", "#index");
//     }
