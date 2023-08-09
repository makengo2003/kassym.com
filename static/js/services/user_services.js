class UserServices {
    static _login(LoginRequestSchema) {
        axios.post("/api/user/login/", LoginRequestSchema, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => {
            window.location.href = "/profile/"
        }).catch((error) => {
            if (error.response) {
                if (error.response.status == 400) {
                    for (var key in error.response.data) {
                        for (var err in error.response.data[key]) {
                            mounted_login_app.login_form_errors.push(error.response.data[key][err])
                        }
                    }
                } else if (error.response.status == 403) {
                    mounted_login_app.login_form_errors.push("Истек срок действия аккаунта")
                } else {
                    swal("Упс", "Что-то пошло не так!")
                }
            }
        }).finally(() => {
            document.getElementById("login_form_submit_btn").disabled = false
        })
    }

    static login(LoginRequestSchema) {
        LoginRequestSchema["favourite_products"] = this.get_local_favourite_products()
        this._login(LoginRequestSchema)
        localStorage.clear()
    }

    static add_products_to_favourites(products_ids_list) {
        if (user_is_authenticated) {
            axios.post("/api/user/add_products_to_favourites/", {products_ids: products_ids_list}, {
                headers: {
                    "X-CSRFToken": $cookies.get("csrftoken"),
                }
            }).then((response) => {
                return
            }).catch((error) => {
                console.log(error)
            })
        } else {
            var favourite_products = this.get_local_favourite_products()

            for (var i = 0; i < products_ids_list.length; i++) {
                favourite_products.push(products_ids_list[i])
            }

            localStorage.setItem("favourite_products", favourite_products)
        }
    }

    static remove_product_from_favourites(product_id) {
        if (user_is_authenticated) {
            axios.post("/api/user/remove_product_from_favourites/", {product_id: product_id}, {
                headers: {
                    "X-CSRFToken": $cookies.get("csrftoken"),
                }
            }).then((response) => {
                return
            }).catch((error) => {
                console.log(error)
            })
        } else {
            var favourite_products = this.get_local_favourite_products()
            if (favourite_products.indexOf(product_id) != -1) {
                favourite_products.splice(favourite_products.indexOf(product_id), 1)
            }
            localStorage.setItem("favourite_products", favourite_products)
        }
    }

    static get_local_favourite_products() {
        var favourite_products = localStorage.getItem("favourite_products")

        if (!favourite_products) {
            localStorage.setItem("favourite_products", [])
            return []
        }

        favourite_products = favourite_products.split(",")
        for (var i = 0; i < favourite_products.length; i++) {
            favourite_products[i] = Number(favourite_products[i])
        }

        return favourite_products
    }

    static clear_favourites() {
        if (user_is_authenticated) {
            axios.post("/api/user/clear_favourites/", {}, {
                headers: {
                    "X-CSRFToken": $cookies.get("csrftoken"),
                }
            }).then((response) => {
                return
            }).catch((error) => {
                console.log(error)
            })
        } else {
            localStorage.setItem("favourite_products", [])
        }
    }

    static change_password(ChangePasswordRequestSchema) {
        axios.post("/api/user/change_password/", ChangePasswordRequestSchema, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => {
            window.location.hash = "#"
            swal("Пароль успешно изменен")
        }).catch((error) => {
            if (error.response) {
                if (error.response.status == 400) {
                    for (var key in error.response.data) {
                        for (var err in error.response.data[key]) {
                            mounted_change_password_app.change_password_form_errors.push(error.response.data[key][err])
                        }
                    }
                } else {
                    swal("Упс", "Что-то пошло не так!")
                }
            }
        }).finally(() => {
            document.getElementById("change_password_form_submit_btn").disabled = false
        })
    }
}