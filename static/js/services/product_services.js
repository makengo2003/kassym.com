class ProductServices {
    static get_products(GetProductsRequestSchema) {
        if (!(GetProductsRequestSchema["last_obj_id"])) {
            GetProductsRequestSchema["last_obj_id"] = this._get_last_obj_id(mounted_products_app.products)
        }

        return axios.get("/api/product/get_products/", {
            params: GetProductsRequestSchema
        }).then((response) => {
            if (!user_is_authenticated) {
                var favourite_products = UserServices.get_local_favourite_products()

                for (var i = 0; i < response.data.length; i++) {
                    response.data[i]["is_favourite"] = favourite_products.includes(response.data[i]["id"])
                    mounted_products_app.products.push(response.data[i])
                }
            } else {
                for (var i = 0; i < response.data.length; i++) {
                    mounted_products_app.products.push(response.data[i])
                }
            }
            return {success: true, data: response.data}
        }).catch((error) => {
            console.log(error)
            return {success: false, data: {}}
        })
    }

    static _get_last_obj_id(products) {
        if (products.length == 0) {
            return 0
        }
        
        var last_obj_id = products[0]["id"]

        for (var i = 1; i < products.length; i++) {
            if (products[i]["id"] < last_obj_id) {
                last_obj_id = products[i]["id"]
            }
        }

        return last_obj_id
    }

    static search_products(search_input) {
        var last_obj_id = this._get_last_obj_id(mounted_products_app.products)

        axios.get("/api/product/search_products/", {
            params: {
                search_input: search_input,
                last_obj_id: last_obj_id
            }
        }).then((response) => {
            if (!user_is_authenticated) {
                var favourite_products = UserServices.get_local_favourite_products()

                for (var i = 0; i < response.data.length; i++) {
                    response.data[i]["is_favourite"] = favourite_products.includes(response.data[i]["id"])
                    mounted_products_app.products.push(response.data[i])
                }
            } else {
                for (var i = 0; i < response.data.length; i++) {
                    mounted_products_app.products.push(response.data[i])
                }
            }
        }).catch((error) => {
            console.log(error)
        })
    }

    static get_product(product_id) {
        return axios.get("/api/product/get_product/?product_id=" + product_id).then(response => response.data)
    }

    static change_product_is_available_status(product_id) {
        axios.post("/api/product/change_product_is_available_status/", {product_id: product_id}, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        })
    }

    static edit_product(product_form) {
        var form_data = new FormData()
        for (var key in product_form) {
            if (key == "images" || key == "options") {
                form_data.append(key, JSON.stringify(product_form[key]));
            } else {
                form_data.append(key, product_form[key]);
            }
        }

        return axios.post("/api/product/edit_product/", form_data, {
            headers: {
                'Content-Type': 'multipart/form-data',
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => {
            return {success: true}
        }).catch((error) => {
            swal("Упс", "Что-то пошло не так!")
            return {success: false}
        }).finally(() => {
            product_form["on_submit"] = false
        })
    }

    static add_product(product_form) {
        var form_data = new FormData()
        for (var key in product_form) {
            if (key == "images" || key == "options") {
                form_data.append(key, JSON.stringify(product_form[key]));
            } else {
                form_data.append(key, product_form[key]);
            }
        }

        return axios.post("/api/product/add_product/", form_data, {
            headers: {
                'Content-Type': 'multipart/form-data',
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => {
            return {success: true, product_id: response.data["product_id"]}
        }).catch((error) => {
            swal("Упс", "Что-то пошло не так!")
            return {success: false}
        }).finally(() => {
            product_form["on_submit"] = false
        })
    }

    static delete_product(product_id) {
        return axios.post("/api/product/delete_product/", {product_id: product_id}, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => response.data)
    }
}