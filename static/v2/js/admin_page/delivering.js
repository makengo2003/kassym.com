delivering_app = Vue.createApp({
    data() {
        return {
            orders: [],
            opened_by_others: [],
            search_input: "",
            searched: false,

            selected_status: "sorted",
            opened_order: null,
            is_making_delivered: false,
            websocket: new WebSocket('ws://' + window.location.host + '/ws/delivering/'),
        }
    },
    methods: {
        open_section() {
            this.get_orders()

        },
        close_section() {},

        select_status(status) {
            this.selected_status = status
            this.get_orders()
        },
        get_orders() {
            var filtration = {status: this.selected_status}

            if (this.search_input) {
                filtration["id"] = Number(this.search_input)
                this.searched = true
            } else {
                this.searched = false
            }

            axios("/api/delivering/get_orders/", {params: filtration}).then((response) => {
                this.orders = response.data
            })
        },

        open_object_file(obj, file) {
            window.open(obj[file], "_blank")

        },

        open_order(order) {
            document.body.style.overflow = 'hidden';
            this.opened_order = order
            this.websocket.send(JSON.stringify({"order_id": this.opened_order.id, "action": "open"}))
        },
        close_order() {
            if (this.opened_order != null) {
                this.websocket.send(JSON.stringify({"order_id": this.opened_order.id, "action": "close"}))
                this.opened_order = null
            }

            document.body.style.overflow = '';
        },

        make_delivered() {
            if (!this.is_making_delivered) {
                Swal.fire({
                    title: "Отправлен?",
                    icon: "question",
                    showCancelButton: true,
                    confirmButtonColor: "#3085d6",
                    cancelButtonColor: "#d33",
                    confirmButtonText: "Да",
                    cancelButtonText: "Нет"
                }).then((result) => {
                    if (result.isConfirmed) {
                        this.is_making_delivered = true

                        axios.post("/api/delivering/make_delivered/", {id: this.opened_order.id}, {
                            headers: {
                                "X-CSRFToken": $cookies.get("csrftoken"),
                            }
                        }).then((response) => {
                            Swal.fire("Отправлен", "", "success")
                        }).catch((error) => {
                            Swal.fire("Ошибка", "", "error")
                        }).finally(() => {
                            this.is_making_delivered = false
                        })
                    }
                });
            }
        },

        handle_websocket_message(event) {
            var data = JSON.parse(event.data);
            var data = data["message"]

            if (data["action"] == "orders_count_changed") {
                this.get_orders()
                if (this.opened_order) {
                    if (data["order_id"] == this.opened_order.id) {
                        axios("/api/delivering/get_orders/", {params: {id: data["order_id"]}}).then((response) => {
                            this.opened_order = response.data[0]
                        })
                    }
                }
            } else {
                this.opened_by_others = data
            }
        },
        handle_websocket_close(event=null) {
            Swal.fire({
              title: "Связь с сервером потеряна",
              icon: "error",
            }).then((result) => {
              window.location.reload()
            });
        },

        get_opened_by_other_fullname() {
            var not_found = true

            for (var i = 0; i < this.opened_by_others.length; i++) {
                if (this.opened_by_others[i].order_id == this.opened_order.id && this.opened_by_others[i].user_id != user_id) {
                    return this.opened_by_others[i].user_fullname
                }
            }

            if (not_found) {
                this.open_order(this.opened_order)
            }
        }
    },
    mounted() {
        this.websocket.addEventListener('message', this.handle_websocket_message);
        this.websocket.addEventListener('close', this.handle_websocket_close);
        this.websocket.addEventListener('error', this.handle_websocket_close);
    }
})


delivering_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_delivering_app = delivering_app.mount("#delivering_section")
