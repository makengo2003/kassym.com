var base_client_form_data = {
    id: 0,
    fullname: "",
    password: "",
    phone_number: "",
    company_name: "",
    created_at: "",
    expires_at: "",
    device1: "",
    device2: "",
    on_submit: false,
    errors: []
}


clients_app = Vue.createApp({
    data() {
        return {
            client_form: Object.assign({}, base_client_form_data),
            clients: [],
            last_obj_id: 0,
            is_getting_clients: false,
            there_is_no_more_clients: false,
            clients_search_input: "",
            admin_searched_clients: false,
        }
    },
    methods: {
        open() {
            if (this.clients.length == 0) {
                this.get_clients()
            }
        },
        get_clients() {
            this.is_getting_clients = true

            ClientServices.get_clients(this.last_obj_id).then((response) => {
                this.is_getting_clients = false
                if (response["data"].length == 0) {
                    this.there_is_no_more_clients = true
                } else {
                    this.there_is_no_more_clients = false

                    for (var i = 0; i < response["data"].length; i++) {
                        this.clients.push(response["data"][i])
                    }

                    this.last_obj_id = this.clients[this.clients.length - 1]["id"]
                }
            })
        },
        close() {},
        window_scroll_down_event_listener() {
            if (!this.is_getting_clients && !this.there_is_no_more_clients) {
                this.get_clients()
            }
        },
        open_client_form(client=null) {
            if (client) {
                ClientServices.get_client(client["id"]).then((response) => {
                    this.client_form = Object.assign(this.client_form, response["data"])
                })
            } else {
                if (this.client_form["id"] != 0) {
                    this.client_form = Object.assign({}, base_client_form_data)
                }
            }

            document.getElementById("client_form_window").style.display = "block"
        },
        client_form_submit() {
            this.client_form["on_submit"] = true

            if (this.client_form["id"]) {
                var submit_function = ClientServices.edit_client
            } else {
                var submit_function = ClientServices.add_client
            }

            submit_function(this.client_form).then((response1) => {
                if (response1["success"]) {
                    document.getElementById("client_form_window").style.display = "none"
                    ClientServices.get_client(response1["id"]).then((response2) => {
                        var found = false
                        for (var i = 0; i < this.clients.length; i++) {
                            if (this.clients[i]["id"] == response1["id"]) {
                                found = true
                                this.clients[i] = response2["data"]
                                break
                            }
                        }

                        if (!found) {
                            this.clients.unshift(response2["data"])
                        }

                        this.client_form = Object.assign({}, base_client_form_data)
                    })
                } else {
                    this.client_form["errors"] = response1["errors"]
                }
            })
        },
        delete_client() {
            swal({
              title: "Подтвердите ваше действия. Вы хотите удалить пользователя?",
              icon: "warning",
              buttons: true,
              dangerMode: true,
            }).then((will) => {
                if (will) {
                    ClientServices.delete_client(this.client_form["id"]).then((response) => {
                        document.getElementById("client_form_window").style.display = "none"
                        for (var i = 0; i < this.clients.length; i++) {
                            if (this.clients[i]["id"] == this.client_form["id"]) {
                                this.clients.splice(i, 1)
                                break
                            }
                        }
                        this.client_form = Object.assign({}, base_client_form_data)
                    })
                }
            })
        },
        reset_devices() {
            this.client_form["device1"] = ""
            this.client_form["device2"] = ""
        },
        search_clients() {
            this.is_getting_clients = true

            ClientServices.search_clients(this.clients_search_input).then((response) => {
                this.admin_searched_clients = true
                this.clients = []

                for (var i = 0; i < response["data"].length; i++) {
                    this.clients.push(response["data"][i])
                }
            })
        },
        cancel_searching() {
            this.admin_searched_clients = false
            this.is_getting_clients = false
            this.last_obj_id = 0
            this.there_is_no_more_clients = false
            this.clients = []
            this.clients_search_input = ""
            this.get_clients()
        }
    },
})


clients_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_clients_app = clients_app.mount("#clients")

alert("TEST")
