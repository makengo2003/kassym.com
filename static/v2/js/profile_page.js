function open_change_password_form() {
    document.getElementById('change_password_form').style.display = 'block'
}

function close_change_password_form() {
    document.getElementById('change_password_form').style.display = 'none'
}

function change_password(event) {
    event.preventDefault()
    var form = event.target

    if (!form.disabled) {
        form.disabled = true
        form.querySelectorAll("button[type='submit']")[0].style.opacity = "0.5"
        document.getElementById("change_password_error").innerText = ""

        var data = {}
        var inputs = form.getElementsByTagName("input");

        for (var i = 0; i < inputs.length; i++) {
            data[inputs[i].name] = inputs[i].value
        }

        axios.post("/api/user/change_password/", data, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => {
            close_change_password_form()
            form.reset()
            Swal.fire("Пароль успешно изменен", "", "success")
        }).catch((error) => {
            if (error.response) {
                if (error.response.status == 400) {
                    for (var key in error.response.data) {
                        for (var err in error.response.data[key]) {
                            document.getElementById("change_password_error").innerText = error.response.data[key][err]
                            break
                        }
                    }
                } else if (error.response.status == 403) {
                    document.getElementById("change_password_error").innerText = error.response.data["detail"]
                } else {
                    swal("Упс", "Что-то пошло не так!")
                }
            }
        }).finally(() => {
            form.disabled = false
            form.querySelectorAll("button[type='submit']")[0].style.opacity = "1"
        })
    }
}

function open_change_fullname_form() {
    document.getElementById('change_fullname_form').style.display = 'block'
}

function close_change_fullname_form() {
    document.getElementById('change_fullname_form').style.display = 'none'
}

function change_fullname(event) {
    event.preventDefault()
    var form = event.target

    if (!form.disabled) {
        form.disabled = true
        form.querySelectorAll("button[type='submit']")[0].style.opacity = "0.5"

        var data = {}
        var inputs = form.getElementsByTagName("input");

        for (var i = 0; i < inputs.length; i++) {
            data[inputs[i].name] = inputs[i].value
        }

        axios.post("/api/user/change_fullname/", data, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => {
            close_change_fullname_form()
            form.reset()
            Swal.fire("ФИО успешно изменен", "", "success")
            document.querySelectorAll("#profile_page .user_info h2")[0].innerText = data["first_name"] + " " + data["last_name"]
        }).finally(() => {
            form.disabled = false
            form.querySelectorAll("button[type='submit']")[0].style.opacity = "1"
        })
    }
}

function open_change_company_name_form() {
    document.getElementById('change_company_name_form').style.display = 'block'
}

function close_change_company_name_form() {
    document.getElementById('change_company_name_form').style.display = 'none'
}

function change_company_name(event) {
    event.preventDefault()
    var form = event.target

    if (!form.disabled) {
        form.disabled = true
        form.querySelectorAll("button[type='submit']")[0].style.opacity = "0.5"

        var data = {}
        var inputs = form.getElementsByTagName("input");

        for (var i = 0; i < inputs.length; i++) {
            data[inputs[i].name] = inputs[i].value
        }

        axios.post("/api/user/change_company_name/", data, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => {
            close_change_company_name_form()
            form.reset()
            Swal.fire("ИП успешно изменен", "", "success")
            document.querySelectorAll("#profile_page .user_info .company_name")[0].innerText = data["company_name"]
        }).finally(() => {
            form.disabled = false
            form.querySelectorAll("button[type='submit']")[0].style.opacity = "1"
        })
    }
}
