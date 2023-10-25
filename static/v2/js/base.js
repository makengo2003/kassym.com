function phone_number_on_input(event) {
    if (!event.target.value.startsWith("+7")) {
        event.target.value = "+7" + event.target.value
        if (event.target.value.endsWith("+")) {
            event.target.value = event.target.value.slice(0, event.target.value.length-1)
        }
    }
}

function login(event) {
    event.preventDefault()

    var form = event.target
    form.disabled = true

    var phone_number = document.getElementById("login_form_phone_number").value
    var password = document.getElementById("login_form_password").value

    document.getElementById("login_error").innerText = ""

    axios.post("/api/user/login/", {
        username: phone_number,
        password: password
    }, {
        headers: {
            "X-CSRFToken": $cookies.get("csrftoken"),
        }
    }).then((response) => {
        window.location.href = "/admin/"
    }).catch((error) => {
        if (error.response) {
            if (error.response.status == 400) {
                for (var key in error.response.data) {
                    for (var err in error.response.data[key]) {
                        document.getElementById("login_error").innerText = error.response.data[key][err]
                        break
                    }
                }
            } else if (error.response.status == 403) {
                document.getElementById("login_error").innerText = error.response.data["detail"]
            } else {
                swal("Упс", "Что-то пошло не так!")
            }
        }
    }).finally(() => {
        form.disabled = false
    })
}

function open_login_form() {
    document.getElementById('login_form_window').style.display = 'block'
}

if (!user_is_authenticated) {
    var categories = document.querySelectorAll(".main-page-top-container .categories .categories_list .category")
    var search_forms = document.querySelectorAll(".search")
    var slides = document.querySelectorAll(".slides .slides-cell")
    var products = document.querySelectorAll(".products_list .product_card")
    var add_wishlist_btns = document.querySelectorAll(".products_list .product_card .add_wishlist_btn")
    var categories_burger = document.querySelectorAll(".categories-burger-content .categories a")
    var see_more_products_btns = document.querySelectorAll(".main-page-products .see_more_products_btn_block button")

    see_more_products_btns[0].onclick = open_login_form

    for (var i = 0; i < categories_burger.length; i++) {
        categories_burger[i].removeAttribute("href")
        categories_burger[i].onclick = open_login_form
    }

    for (var i = 0; i < categories.length; i++) {
        categories[i].removeAttribute("href")
        categories[i].onclick = open_login_form
    }

    for (var i = 0; i < search_forms.length; i++) {
        search_forms[i].onsubmit = function(event) {
            event.preventDefault()
            open_login_form()
        }
    }

    for (var i = 0; i < slides.length; i++) {
        slides[i].onclick = open_login_form
    }

    for (var i = 0; i < add_wishlist_btns.length; i++) {
        add_wishlist_btns[i].onclick = open_login_form
    }

    for (var i = 0; i < products.length; i++) {
        products[i].removeAttribute("href")
        products[i].onclick = open_login_form
    }
}

function leave_request(event) {
    event.preventDefault()

    var form = event.target
    form.disabled = true

    var phone_number = document.getElementById("leave_request_phone_number").value
    var fullname = document.getElementById("leave_request_fullname").value

    axios.post("/api/user/leave_request/", {
        phone_number: phone_number,
        fullname: fullname
    }, {
        headers: {
            "X-CSRFToken": $cookies.get("csrftoken"),
        }
    }).then((response) => {
        document.getElementById('watch_instruction_form_window').style.display = 'none'
        document.getElementById('watch_instruction_window').style.display = 'flex'
        localStorage.setItem("already_left_request", true);
        form.disabled = false
    })
}

function open_instruction_window() {
    const already_left_request = localStorage.getItem("already_left_request");

    if (already_left_request || user_is_authenticated) {
        document.getElementById('watch_instruction_window').style.display = 'flex'
    } else {
        document.getElementById('watch_instruction_form_window').style.display = 'block'
    }
}

function close_instruction_video() {
    var video = document.getElementById("instruction_video");
    video.pause();
    document.getElementById('watch_instruction_window').style.display = 'none'
}

function wait_burger_opening() {
    document.getElementsByClassName("burger-container")[0].classList.toggle("active_burger")
    document.getElementsByClassName("burger")[0].removeEventListener("transitionend", wait_burger_opening)
}


function open_burger() {
    close_categories_burger()
    document.getElementsByClassName("hamburger-menu")[0].classList.toggle('active_hamburger');
    document.getElementsByClassName("burger")[0].addEventListener("transitionend", wait_burger_opening)
    document.getElementsByClassName("hamburger-menu")[0].onclick = close_burger
    document.body.style.overflow = 'hidden';
}

function wait_burger_content_closing() {
    document.getElementsByClassName("hamburger-menu")[0].classList.toggle('active_hamburger');
    document.getElementsByClassName("burger-container")[0].removeEventListener("transitionend", wait_burger_content_closing)
}

function close_burger() {
    document.getElementsByClassName("burger-container")[0].classList.toggle("active_burger")
    document.getElementsByClassName("burger-container")[0].addEventListener("transitionend", wait_burger_content_closing)
    document.getElementsByClassName("hamburger-menu")[0].onclick = open_burger
    document.body.style.overflow = 'auto';
}

function open_categories_burger() {
    document.getElementsByClassName("burger-content")[0].style.display = "none"
    document.getElementsByClassName("categories-burger-content")[0].style.display = "block"
}

function close_categories_burger() {
    document.getElementsByClassName("burger-content")[0].style.display = "block"
    document.getElementsByClassName("categories-burger-content")[0].style.display = "none"
}
