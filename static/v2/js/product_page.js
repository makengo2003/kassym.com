function set_current_image(url) {
    var current_image = document.querySelectorAll(".images .current_image")[0]
    current_image.style.backgroundImage = "url('" + url + "')"

    var computedStyle = window.getComputedStyle(current_image);

    if (computedStyle.display == 'none') {
        open_image(url)
    }
}

function open_image(url) {
    document.getElementById("myModal").style.display = "flex"
    document.getElementById("modal_image").src = url
    document.getElementById("modal_image").setAttribute("data-src", url)
}

function show_prev_img() {
    var modal_image = document.getElementById("modal_image")
    var imgs = document.querySelectorAll(".images .image")

    for (var i = 0; i < imgs.length; i++) {
        if (imgs[i].getAttribute("data-src") == modal_image.getAttribute("data-src")) {
            if (i - 1 != -1) {
                modal_image.src = imgs[i - 1].getAttribute("data-src")
                document.getElementById("modal_image").setAttribute("data-src", imgs[i - 1].getAttribute("data-src"))
            } else {
                modal_image.src = imgs[imgs.length - 1].getAttribute("data-src")
                document.getElementById("modal_image").setAttribute("data-src", imgs[imgs.length - 1].getAttribute("data-src"))
            }

            break
        }
    }
}

function show_next_img() {
    var modal_image = document.getElementById("modal_image")
    var imgs = document.querySelectorAll(".images .image")

    for (var i = 0; i < imgs.length; i++) {
        if (imgs[i].getAttribute("data-src") == modal_image.getAttribute("data-src")) {
            if (i + 1 != imgs.length) {
                modal_image.src = imgs[i + 1].getAttribute("data-src")
                document.getElementById("modal_image").setAttribute("data-src", imgs[i + 1].getAttribute("data-src"))
            } else {
                modal_image.src = imgs[0].getAttribute("data-src")
                document.getElementById("modal_image").setAttribute("data-src", imgs[0].getAttribute("data-src"))
            }

            break
        }
    }
}

function go_back(url) {
    if (document.referrer.includes(url)) {
        window.history.go(-1)
    } else {
        window.location.href = url
    }
}
