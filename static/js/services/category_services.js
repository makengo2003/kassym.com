class CategoryServices {
    static get_category(category_id) {
        return axios.get("/api/category/get_category/?category_id=" + category_id).then(response => response.data)
    }

    static get_categories() {
        return axios.get("/api/category/get_categories/").then(response => response.data)
    }

    static add_category(category_form) {
        return axios.post("/api/category/add_category/", category_form, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
                'Content-Type': 'multipart/form-data'
            }
        }).finally(() => {
            category_form["on_submit"] = false
            return {success: true}
        })
    }

    static edit_category(category_form) {
        return axios.post("/api/category/edit_category/", category_form, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
                'Content-Type': 'multipart/form-data'
            }
        }).finally(() => {
            category_form["on_submit"] = false
            return {success: true}
        })
    }

    static delete_category(category_id) {
        return axios.post("/api/category/delete_category/", {category_id: category_id}, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => response.data)
    }

    static save_categories_order(categories_order) {
        axios.post("/api/category/save_categories_order/", {categories_order: categories_order}, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        })
    }
}