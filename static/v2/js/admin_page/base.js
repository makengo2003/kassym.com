var websocket_prefix = "ws://"

if (window.location.host.contains("https")) {
    websocket_prefix = "wss://"
}


orders_app = Vue.createApp({
    data() {
        return {
            section_is_opened_ones: false,
            edit_order_form_is_opened: false,
            edit_order_form_is_submitting: false,

            search_input: "",
            searched: false,

            change_times: [],
            orders: [],
            opened_by_others: [],

            orders_counts: {
                new_orders_count: 0,
                accepted_orders_count: 0,
            },

            opened_category: "new_orders",
            opened_order: null,
            selected_change_time: null,
            websocket: new WebSocket(websocket_prefix + window.location.host + '/ws/order/'),
            uploaded_files: []
        }
    },
    methods: {
        open_section() {
            if (!this.section_is_opened_ones) {
                this.get_orders_change_times()
            }
        },
        close_section() {},
        open_category(category) {
            this.opened_category = category

            var status = category.slice(0, -7)
            var selected_change_time = this.selected_change_time.split(".").reverse().join("-")

            if (status == "all") {
                var filtration = {created_at__date: selected_change_time}
            } else {
                var filtration = {"status": status, created_at__date: selected_change_time}
            }

            if (this.search_input) {
                if (!isNaN(this.search_input)) {
                    filtration["id"] = Number(this.search_input)
                } else {
                    filtration["user__client__company_name"] = this.search_input
                }

                this.searched = true
            } else {
                this.searched = false
            }

            axios("/api/order/get_many/", {params: {filtration: JSON.stringify(filtration), ordering: JSON.stringify(["-is_express", "-created_at"])}}).then((response) => {
                this.orders = response.data
            })
        },
        search() {
            this.open_category(this.opened_category)
        },
        set_orders_counts() {
            var selected_change_time = this.selected_change_time.split(".").reverse().join("-")

            axios("/api/order/get_orders_counts/", {params: {created_at__date: selected_change_time}}).then((response) => {
                this.orders_counts = response.data
            })
        },

        get_orders_change_times() {
            axios("/api/change_time/get_many/").then((response) => {
                this.change_times = response.data

                if (!this.section_is_opened_ones) {
                    this.selected_change_time = this.change_times[0].dt
                    this.select_orders_change_time()
                    this.section_is_opened_ones = true
                }
            })
        },
        select_orders_change_time() {
            this.open_category(this.opened_category)
            this.set_orders_counts()
        },
        selected_orders_change_time_is_today() {
            if (this.change_times.length > 0) {
                return this.change_times[0].dt == this.selected_change_time
            }
            return false

        },
        finish_change_time_is_available() {
            return this.orders_counts.new_orders_count == 0

        },
        finish_change_time() {
            Swal.fire({
                title: "Завершить смену?",
                icon: "question",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Да",
                cancelButtonText: "Нет"
            }).then((result) => {
                if (result.isConfirmed) {
                    axios.post("/api/change_time/finish/", {},
                        {
                            headers: {
                                "X-CSRFToken": $cookies.get("csrftoken"),
                            }
                        }
                    ).then((response) => {
                        Swal.fire({
                            title: "Смена завершена",
                            icon: "success",
                        })
                    }).catch((error) => {
                        if (error.response.status == 400) {
                            Swal.fire({
                                title: "Для завершения смены необходимо обработать все сегодняшние заказы.",
                                icon: "error",
                            })
                        } else {
                            Swal.fire({
                                title: 'Неизвестная ошибка',
                                icon: "error",
                            })
                        }
                    })
                }
            });
        },

        open_object_file(obj, file) {
            window.open(obj[file], "_blank")

        },
        show_order_dt(order) {
            return order.created_at.split(", ")[1].slice(0, 5)

        },

        accept_order(order) {
            Swal.fire({
                title: "Принять заказ?",
                icon: "question",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Да",
                cancelButtonText: "Нет"
            }).then((result) => {
                if (result.isConfirmed) {
                    axios.post("/api/order/accept/",
                        {
                            id: this.opened_order.id,
                        },
                        {
                            headers: {
                                "X-CSRFToken": $cookies.get("csrftoken"),
                            }
                        }
                    ).then((response) => {
                        Swal.fire({
                            title: "Заказ принят",
                            icon: "success"
                        });
                        this.close_order()
                    })
                }
            });
        },
        edit_order() {
            this.edit_order_form_is_opened = true

        },
        cancel_edit_order() {
            this.edit_order_form_is_opened = false

            this.cancel_file_upload(this.opened_order, "uploaded_deliveries_qr_code")
            this.cancel_file_upload(this.opened_order, "uploaded_selection_sheet_file")
            this.cancel_file_upload(this.opened_order, "uploaded_paid_check_file")

            this.opened_order.new_comments = ""

            for (var i = 0; i < this.opened_order.items.length; i++) {
                this.cancel_file_upload(this.opened_order.items[i], "uploaded_qr_code")
            }
        },
        edit_order_form_submit() {
            if (!this.edit_order_form_is_submitting) {
                Swal.fire({
                    title: "Сохранить изменения?",
                    icon: "question",
                    showCancelButton: true,
                    confirmButtonColor: "#3085d6",
                    cancelButtonColor: "#d33",
                    confirmButtonText: "Да",
                    cancelButtonText: "Нет"
                }).then((result) => {
                    if (result.isConfirmed) {
                        this.edit_order_form_is_submitting = true

                        var data = {
                            id: this.opened_order.id,
                            new_comments: this.opened_order.new_comments,
                        }

                        for (var key in this.uploaded_files) {
                            data[key] = this.uploaded_files[key]
                        }

                        axios.post("/api/order/edit/", data, {
                            headers: {
                                'Content-Type': 'multipart/form-data',
                                "X-CSRFToken": $cookies.get("csrftoken")
                            }
                        }).then((response) => {
                            Swal.fire({
                              title: "Заказ исправлен",
                              icon: "success",
                            })
                            this.cancel_edit_order()
                        }).catch((err) => {
                            Swal.fire("Произошла какая-та ошибка!", "Свяжитесь с нами", "error")
                        }).finally(() => {
                            this.edit_order_form_is_submitting = false
                        })
                    }
                });
            }
        },
        file_is_uploaded(obj, label) {
            if (obj[label]) {
                return !(obj[label].startsWith("/media/"))
            }
        },
        get_uploaded_file_name(file_name) {
            return file_name.slice(file_name.indexOf(":") + 2, file_name.length)

        },
        handle_file_upload(extensions, event, obj, label, obj_name, obj_id_label="") {
            var file = event.target.files[0]

            if (file) {
                var label_for_uploaded_files_list = obj_name + "_" + label

                if (obj_id_label != "")
                    label_for_uploaded_files_list += "_" + obj_id_label

                label_for_uploaded_files_list += ": " + file.name

                obj[label] = label_for_uploaded_files_list
                this.uploaded_files[label_for_uploaded_files_list] = file

                for (var i = 0; i < extensions.length; i++) {
                    if (!file.name.toLowerCase().endsWith(extensions[i].toLowerCase())) {
                        Swal.fire('Неподдерживаемый тип файла ' + '".' + file.name.split(".").slice(-1) + '"', "", "warning")
                        this.cancel_file_upload(obj, label)
                    }
                }
            }
        },
        cancel_file_upload(obj, label) {
            if (this.file_is_uploaded(obj, label)) {
                delete this.uploaded_files[obj[label]]
                document.getElementById(obj[label].split(":")[0]).value = null
                delete obj[label]
            }
        },

        open_order(order) {
            this.opened_order = order
            this.websocket.send(JSON.stringify({"order_id": this.opened_order.id, "action": "open"}))
            document.body.style.overflow = 'hidden';
        },
        close_order() {
            if (this.opened_order != null) {
                this.websocket.send(JSON.stringify({"order_id": this.opened_order.id, "action": "close"}))
                this.opened_order = null
            }
            document.body.style.overflow = '';
        },
        handle_websocket_message(event) {
            var data = JSON.parse(event.data);
            var data = data["message"]

            if (data["action"] == "change_time_finished") {
                this.get_orders_change_times()
            } else if (data["action"] == "orders_count_changed") {
                this.select_orders_change_time()
                if (this.opened_order) {
                    if (data["order_id"] == this.opened_order.id) {
                        this.close_order()
                    }
                }
            } else if (data["action"] == "order_changed") {
                axios("/api/order/get_many/", {params: {filtration: JSON.stringify({id: data["order_id"]})}}).then((response) => {
                    var order = response.data[0]

                    for (var i = 0; i < this.orders.length; i++) {
                        if (this.orders[i].id == order.id) {
                            this.orders[i] = order
                            break
                        }
                    }

                    if (this.opened_order.id == order.id) {
                        this.opened_order = order
                    }
                })
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
                    return this.opened_by_others[i].user_fullname + " рассматривает заказ!"
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


orders_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_orders_app = orders_app.mount("#orders_section")
