var websocket_prefix = "ws://"

if (window.location.host == "kassym.com") {
    websocket_prefix = "wss://"
}


sorting_app = Vue.createApp({
    data() {
        return {
            orders: [],
            opened_by_others: [],
            search_input: "",
            searched: false,

            selected_status: "accepted",
            websocket: new WebSocket(websocket_prefix + window.location.host + '/ws/sorting/'),
            opened_order: null,
            finish_sorting_requesting: false,
            uploaded_replaced_by_images: [],
            is_saving_changes: false
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

            axios("/api/sorting/get_orders/", {params: filtration}).then((response) => {
                this.orders = response.data
            })
        },

        open_object_file(obj, file) {
            window.open(obj[file], "_blank")

        },

        open_order(order) {
            this.opened_order = order
            this.websocket.send(JSON.stringify({"order_id": this.opened_order.id, "action": "open"}))

            var file_inputs = document.getElementsByClassName('replaced_by_product_image_upload_input')
            for (var i = 0; i < file_inputs.length; i++) {
                file_inputs[i].value = null
            }

            this.uploaded_replaced_by_images = []
            this.is_saving_changes = false

            document.body.style.overflow = 'hidden';
        },
        close_order() {
            if (this.opened_order != null) {
                this.websocket.send(JSON.stringify({"order_id": this.opened_order.id, "action": "close"}))
                this.opened_order = null
            }
            document.body.style.overflow = '';
        },

        start_to_sort() {
            Swal.fire({
                title: "Начать сортировку?",
                icon: "question",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Да",
                cancelButtonText: "Нет"
            }).then((result) => {
                if (result.isConfirmed) {
                    axios.post("/api/sorting/start_to_sort/", {id: this.opened_order.id}, {headers: {"X-CSRFToken": $cookies.get("csrftoken")}})
                }
            });
        },
        check_sorting() {
            this.opened_order["save_sorting_form"] = {
                "replaced": [],
                "sorted": [],
                "not_available": [],
            }

            for (var i = 0; i < this.opened_order.order_items.length; i++) {
                for (var j = 0; j < this.opened_order.order_items[i].purchases.length; j++) {
                    if (this.opened_order.order_items[i].product.category == 7 && this.opened_order.order_items[i].purchases[j].status == "replaced" && !this.purchase_was_replaced_by(this.opened_order.order_items[i].purchases[j])) {
                        if (!this.get_uploaded_replaced_by_image(this.opened_order.order_items[i].purchases[j])) {
                            Swal.fire("Фото товара(заменён) не найдена", "", "error")
                            return
                        } else {
                            this.opened_order["save_sorting_form"]["replaced"].push(this.opened_order.order_items[i].purchases[j].id)
                            this.opened_order["save_sorting_form"]["replaced_" + this.opened_order.order_items[i].purchases[j].id] = this.uploaded_replaced_by_images[this.opened_order.order_items[i].purchases[j].replaced_by_product_image]
                        }
                    }

                    if (this.opened_order.order_items[i].purchases[j].is_sorted) {
                        this.opened_order["save_sorting_form"]["sorted"].push(this.opened_order.order_items[i].purchases[j].id)
                    }

                    if (this.opened_order.order_items[i].product.category == 7 && this.opened_order.order_items[i].purchases[j].status == "not_available") {
                        this.opened_order["save_sorting_form"]["not_available"].push(this.opened_order.order_items[i].purchases[j].id)
                    }
                }
            }

            return true
        },
        get_save_sorting_form() {
            var data = {
                order_id: this.opened_order.id,
                sorted_purchases: JSON.stringify(this.opened_order["save_sorting_form"]["sorted"]),
                replaced_purchases: JSON.stringify(this.opened_order["save_sorting_form"]["replaced"]),
                not_available_purchases: JSON.stringify(this.opened_order["save_sorting_form"]["not_available"]),
            }

            for (var key in this.opened_order["save_sorting_form"]) {
                if (key == "sorted" || key == "replaced" || key == "not_available") {
                    continue
                }

                data[key] = this.opened_order["save_sorting_form"][key]
            }

            return data
        },
        save_sorting() {
            if (!this.is_saving_changes) {
                if (this.check_sorting()) {
                    Swal.fire("Пожалуйста, внимательно проверьте введенные данные", "", "warning")
                    this.is_saving_changes = true
                }
            } else {
                var data = this.get_save_sorting_form()

                axios.post("/api/sorting/save_sorting/", data, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        "X-CSRFToken": $cookies.get("csrftoken"),
                    }
                }).then((response) => {
                    Swal.fire("Сохранено", "", "success")
                }).catch((error) => {
                    Swal.fire("Ошибка", "", "error")
                }).finally(() => {
                    this.is_saving_changes = false
                })
            }
        },
        finish_sorting() {
            if (this.check_sorting()) {
                for (var i = 0; i < this.opened_order.order_items.length; i++) {
                    for (var j = 0; j < this.opened_order.order_items[i].purchases.length; j++) {
                        if (this.opened_order.order_items[i].purchases[j].status != 'not_available') {
                            if (!this.opened_order.order_items[i].purchases[j].is_sorted || this.opened_order.order_items[i].purchases[j].status == "В обработке" || this.opened_order.order_items[i].purchases[j].status == "Будет завтра") {
                                Swal.fire("Нужно сортировать все товары", "", "warning")
                                return
                            }
                        }
                    }
                }

                if (!this.finish_sorting_requesting) {
                    Swal.fire({
                        title: "Завершить сортировку?",
                        icon: "question",
                        showCancelButton: true,
                        confirmButtonColor: "#3085d6",
                        cancelButtonColor: "#d33",
                        confirmButtonText: "Да",
                        cancelButtonText: "Нет"
                    }).then((result) => {
                        if (result.isConfirmed) {
                            document.getElementById("sorted_report_upload_input").click()
                        }
                    });
                }
            }
        },

        handle_sorted_report_upload_input($event) {
            var file = event.target.files[0]

            if (file) {
                this.finish_sorting_requesting = true

                var data = this.get_save_sorting_form()
                axios.post("/api/sorting/save_sorting/", data, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        "X-CSRFToken": $cookies.get("csrftoken"),
                    }
                }).then((response) => {
                    axios.post("/api/sorting/finish_sorting/",
                    {
                        id: this.opened_order.id,
                        sorted_report: file
                    },
                    {
                        headers: {
                            "X-CSRFToken": $cookies.get("csrftoken"),
                            'Content-Type': 'multipart/form-data',
                        }
                    }).then((response) => {
                        Swal.fire("Сортирован", "", "success")
                    }).catch((error) => {
                        Swal.fire("Ошибка", "", "error")
                    }).finally(() => {
                        this.finish_sorting_requesting = false
                    })
                }).catch((error) => {
                    Swal.fire("Ошибка", "", "error")
                }).finally(() => {
                    this.finish_sorting_requesting = false
                })
            }
        },

        handle_websocket_message(event) {
            var data = JSON.parse(event.data);
            var data = data["message"]

            if (data["action"] == "orders_count_changed") {
                this.get_orders()
                if (this.opened_order) {
                    if (data["order_id"] == this.opened_order.id) {
                        axios("/api/sorting/get_orders/", {params: {id: data["order_id"]}}).then((response) => {
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
        },

        purchase_was_replaced_by(purchase) {
            if (purchase.replaced_by_product_image) {
                return purchase.replaced_by_product_image.startsWith("/media/")
            }
        },

        get_uploaded_replaced_by_image(purchase) {
            if (purchase.replaced_by_product_image) {
                return purchase.replaced_by_product_image.split(": ")[1]
            }
        },

        handle_replaced_by_upload(event, purchase, order_item_index, purchase_index) {
            var file = event.target.files[0]

            if (file) {
                var label = order_item_index + "_" + purchase_index + ": " + file.name
                purchase["replaced_by_product_image"] = label
                this.uploaded_replaced_by_images[label] = file
            }
        },

        delete_uploaded_replaced_by(purchase) {
            delete this.uploaded_replaced_by_images[purchase["replaced_by_product_image"]]
            document.getElementById('purchase_replaced_input_' + purchase["replaced_by_product_image"].split(":")[0]).value = null
            purchase["replaced_by_product_image"] = ""
        },

        sorting_disabled(purchase) {
            return this.opened_order.status != 'is_sorting' || purchase.status == 'new' || purchase.status == 'will_be_tomorrow' || purchase.status == 'not_available' || purchase.status == "is_being_considered" || this.is_saving_changes
        },

        get_previous_purchases_count(order_item_index) {
            var order_items = this.opened_order.order_items.slice(0, order_item_index)
            var count = 0

            for (var i = 0; i < order_items.length; i++) {
                count += order_items[i].purchases.length
            }

            return count
        }
    },
    mounted() {
        this.websocket.addEventListener('message', this.handle_websocket_message);
        this.websocket.addEventListener('close', this.handle_websocket_close);
        this.websocket.addEventListener('error', this.handle_websocket_close);
    }
})


sorting_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_sorting_app = sorting_app.mount("#sorting_section")
