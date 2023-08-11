class ClientServices {
    static get_clients(last_obj_id) {
        return axios.get("/api/user/get_clients/", {params: {last_obj_id: last_obj_id}}).then(response => response)
    }

    static search_clients(clients_search_input) {
        return axios.get("/api/user/search_clients/", {params: {clients_search_input: clients_search_input}}).then(response => response)
    }

    static get_client(client_id) {
        return axios.get("/api/user/get_client/", {params: {client_id: client_id}}).then(response => response)
    }

    static edit_client(client_form) {
        client_form["client_id"] = client_form["id"]
        return axios.post("/api/user/edit_client/", client_form, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => {
            return {success: true, id: response["data"]["client_id"]}
        }).catch((error) => {
            if (error.response) {
                if (error.response.status == 400) {
                    var errors = []
                    for (var key in error.response.data) {
                        for (var err in error.response.data[key]) {
                            errors.push(error.response.data[key][err])
                        }
                    }
                    return {success: false, errors: errors}
                } else {
                    swal("Упс", "Что-то пошло не так!")
                    return {success: false, errors: []}
                }
            }
        }).finally(() => {
            client_form["on_submit"] = false
        })
    }

    static add_client(client_form) {
        return axios.post("/api/user/add_client/", client_form, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => {
            return {success: true, id: response["data"]["client_id"]}
        }).catch((error) => {
            if (error.response) {
                if (error.response.status == 400) {
                    var errors = []
                    for (var key in error.response.data) {
                        for (var err in error.response.data[key]) {
                            if (error.response.data[key][err] == "Enter a valid phone number.") {
                                errors.push("Введите действительный номер телефона.")
                            } else {
                                errors.push(error.response.data[key][err])
                            }
                        }
                    }
                    return {success: false, errors: errors}
                } else {
                    swal("Упс", "Что-то пошло не так!")
                    return {success: false, errors: []}
                }
            }
        }).finally(() => {
            client_form["on_submit"] = false
        })
    }

    static delete_client(client_id) {
        return axios.post("/api/user/delete_client/", {client_id: client_id}, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        }).then((response) => {
            return {success: true}
        }).catch((error) => {
            swal("Упс", "Что-то пошло не так!")
            return {success: false}
        })
    }
}
