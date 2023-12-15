var websocket_prefix = "ws://"

if (window.location.host == "kassym.com") {
    websocket_prefix = "wss://"
}


sorting_app = Vue.createApp({
    data() {
        return {
            orders: [],
            search_input: "",
            searched: false,

            selected_status: "accepted",
            websocket: new WebSocket(websocket_prefix + window.location.host + '/ws/sorting/'),
            opened_order: null,
            finish_sorting_requesting: false,
            is_saving_changes: false,
            uploaded_reports: {},
            opened_image: null,
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
            this.opened_order = {}
            this.is_saving_changes = false

            document.body.style.overflow = 'hidden';

            axios("/api/sorting/get_order/", {params: {id: order.id}}).then((response) => {
                this.opened_order = response.data
            })
        },
        close_order() {
            if (this.opened_order != null) {
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
                "sorted": [],
                "reports": [],
            }

            for (var i = 0; i < this.opened_order.order_items.length; i++) {
                for (var j = 0; j < this.opened_order.order_items[i].purchases.length; j++) {
                    if (this.opened_order.order_items[i].purchases[j].is_sorted) {
                        this.opened_order["save_sorting_form"]["sorted"].push(this.opened_order.order_items[i].purchases[j].id)
                    }
                }
            }

            for (var i = 0; i < this.opened_order.reports.length; i++) {
                 if (this.report_is_new(this.opened_order.reports[i])) {
                    if (this.report_is_uploaded(this.opened_order.reports[i])) {
                        this.opened_order["save_sorting_form"]["reports"].push(this.opened_order.reports[i])
                    } else {
                        Swal.fire("Фото отчет не загружен", "", "warning")
                        return false
                    }
                 }
            }

            if (this.opened_order["save_sorting_form"]["sorted"].length == 0) {
                Swal.fire("Выберите сортированный товар", "", "warning")
                return false
            }

            return true
        },
        get_save_sorting_form() {
            var data = {
                order_id: this.opened_order.id,
                sorted_purchases: JSON.stringify(this.opened_order["save_sorting_form"]["sorted"]),
                reports: JSON.stringify(this.opened_order["save_sorting_form"]["reports"]),
            }

            for (var i = 0; i < this.opened_order["save_sorting_form"]["reports"].length; i++) {
                data[this.opened_order["save_sorting_form"]["reports"][i]] = this.uploaded_reports[this.opened_order["save_sorting_form"]["reports"][i]]
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
                Swal.fire({
                    title: "Сохранение...",
                    text: "Не закрывайте страницу",
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    didOpen: () => {
                        Swal.showLoading();
                        window.addEventListener('beforeunload', this.window_close_warning);

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
                            window.removeEventListener('beforeunload', this.window_close_warning);
                        })
                    }
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

                if (this.opened_order.reports.length == 0) {
                    Swal.fire("Требуется фотоотчет", "", "warning")
                    return
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
                            Swal.fire({
                                title: "Сохранение...",
                                text: "Не закрывайте страницу",
                                allowOutsideClick: false,
                                allowEscapeKey: false,
                                didOpen: () => {
                                    Swal.showLoading();
                                    window.addEventListener('beforeunload', this.window_close_warning);

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
                                        },
                                        {
                                            headers: {
                                                "X-CSRFToken": $cookies.get("csrftoken"),
                                            }
                                        }).then((response) => {
                                            Swal.fire("Сортирован", "", "success")
                                        }).catch((error) => {
                                            Swal.fire("Ошибка", "", "error")
                                        }).finally(() => {
                                            this.finish_sorting_requesting = false
                                            window.removeEventListener('beforeunload', this.window_close_warning);
                                        })
                                    }).catch((error) => {
                                        Swal.fire("Ошибка", "", "error")
                                    }).finally(() => {
                                        this.finish_sorting_requesting = false
                                        window.removeEventListener('beforeunload', this.window_close_warning);
                                    })
                                }
                            })
                        }
                    })
                }
            }
        },

        window_close_warning(event) {
            if (typeof event == 'undefined') {
                event = window.event;
            }
            if (event) {
                event.returnValue = 'Изменения сохраняется...';
            }
        },

        get_order_reports() {
            if (this.opened_order.reports) {
                return this.opened_order.reports
            }
            return []
        },
        add_report() {
            if (this.opened_order.reports) {
                this.opened_order.reports.push("")
            } else {
                this.opened_order.reports = [""]
            }
        },
        remove_report(report_index) {
            delete this.uploaded_reports[this.opened_order.reports[report_index]]
            this.opened_order.reports.splice(report_index, 1)
        },
        report_is_new(report) {
            return !report.startsWith("/media/")

        },
        report_is_uploaded(report) {
            return report != ""

        },
        handle_report_upload(event, report_index) {
            var file = event.target.files[0]

            if (file) {
                if (this.opened_order.reports[report_index] != "") {
                    delete this.uploaded_reports[this.opened_order.reports[report_index]]
                }

                this.opened_order.reports[report_index] = file.name
                this.uploaded_reports[file.name] = file
            }
        },

        handle_websocket_message(event) {
            var data = JSON.parse(event.data);
            var data = data["message"]

            if (data["action"] == "orders_count_changed") {
                this.get_orders()
                if (this.opened_order) {
                    if (data["order_id"] == this.opened_order.id) {
                        axios("/api/sorting/get_order/", {params: {id: data["order_id"]}}).then((response) => {
                            this.opened_order = response.data
                        })
                    }
                }
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
        },
        start_to_sort_available() {
            for (var i = 0; i < this.opened_order.order_items.length; i++) {
                for (var j = 0; j < this.opened_order.order_items[i].purchases.length; j++) {
                    if (this.opened_order.order_items[i].purchases[j].status == "purchased" || this.opened_order.order_items[i].purchases[j].status == "replaced") {
                        return true
                    }
                }
            }

            return false
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
