var websocket_prefix = "ws://"

if (window.location.host == "kassym.com") {
    websocket_prefix = "wss://"
}


purchases_app = Vue.createApp({
    data() {
        return {
            section_is_opened_ones: false,
            purchase_is_making: false,
            purchasing_is_available: false,

            change_times: [],
            purchases: [],
            opened_by_others: [],
            opened_product_image: '',

            purchases_counts: {
                sadovod: 0,
                yuzhnye_vorota: 0,
            },
            purchase_form: {
                price_per_count: 0,
                purchased_count: 0,
                replaced_count: 0,
                not_available_count: 0,
                will_be_tomorrow_count: 0,
                replaced_by_product_id: 0,
                replaced_by_product_image: ''
            },
            base_purchase_form: {
                price_per_count: 0,
                purchased_count: 0,
                replaced_count: 0,
                not_available_count: 0,
                will_be_tomorrow_count: 0,
                replaced_by_product_image: 0,
            },
            uploaded_files: {},

            opened_market: "sadovod",
            opened_purchase: null,

            selected_status: "new",
            selected_change_time: null,

            websocket: new WebSocket(websocket_prefix + window.location.host + '/ws/purchase/'),
            is_being_considered_report: null,
            is_being_considered_form: null,
            is_being_considered: null,
            is_submitting_is_being_considered_form: null,
            comments: null,
        }
    },
    methods: {
        open_section() {
            if (!this.section_is_opened_ones) {
                this.get_change_times()
            }
        },
        close_section() {},

        get_purchases_list() {
            var filtration = {
                change_time: this.reformat_selected_change_time(),
                market: this.opened_market,
                status: this.selected_status,
            }

            axios("/api/purchase/get_purchases/", {
                params: filtration
            }).then((response) => {
                this.purchases = response.data
            })
        },
        set_purchases_counts() {
            var selected_change_time = this.reformat_selected_change_time()

            axios("/api/purchase/get_purchases_counts/", {
                params: {change_time: this.reformat_selected_change_time()}
            }).then((response) => {
                this.purchases_counts = response.data
            })
        },

        get_change_times() {
            axios("/api/change_time/get_many/").then((response) => {
                this.change_times = response.data.slice(1, response.data.length)

                if (!this.section_is_opened_ones) {
                    this.selected_change_time = this.change_times[0].dt
                    this.select_change_time()
                    this.section_is_opened_ones = true
                }
            })
        },
        selected_change_time_is_today() {
            if (this.change_times.length > 0) {
                return this.change_times[0].dt == this.selected_change_time
            }

            return false
        },
        reformat_selected_change_time() {
            return this.selected_change_time.split(".").reverse().join("-")

        },

        open_market(market) {
            this.opened_market = market
            this.get_purchases_list()
        },
        select_status(status) {
            this.selected_status = status
            this.get_purchases_list()
        },
        select_change_time() {
            this.get_purchases_list()
            this.set_purchases_counts()
        },

        close_is_being_considered_form () {
            this.is_being_considered_form = null
            this.is_being_considered = false
            this.is_submitting_is_being_considered_form = false
            document.body.style.overflow = '';
        },
        submit_is_being_considered_form () {
            if (!this.is_submitting_is_being_considered_form) {
                this.is_submitting_is_being_considered_form = true

                axios.post("/api/purchase/save_is_being_considered_purchases/", this.is_being_considered_form["request_data"], {
                    headers: {"X-CSRFToken": $cookies.get("csrftoken")}
                }).then((response) => {
                    Swal.fire("Куплено", "", "success")
                    this.close_is_being_considered_form()
                }).catch((error) => {
                    Swal.fire("Ошибка", "", "error")
                }).finally(() => {
                    this.is_submitting_is_being_considered_form = false
                })
            }
        },
        save_is_being_considered_form () {
            this.is_being_considered_form["request_data"] = {
                product_id: this.is_being_considered_form["product_id"],
                price_per_count: this.is_being_considered_form["price_per_count"],
                replaced_purchases_ids: [],
                not_available_purchases_ids: [],
            }

            for (var i = 0; i < this.is_being_considered_form["purchases"].length; i++) {
                var purchase = this.is_being_considered_form["purchases"][i]

                if (purchase["status"] == "replaced") {
                    this.is_being_considered_form["request_data"]["replaced_purchases_ids"].push(purchase.id)

                    if (!(this.is_being_considered_form["price_per_count"] > 0)) {
                        Swal.fire("Вы забыли указать цену за штук", "", "error")
                        return
                    }
                } else {
                    this.is_being_considered_form["request_data"]["not_available_purchases_ids"].push(purchase.id)
                }
            }

            this.is_being_considered = true
            Swal.fire("Пожалуйста, внимательно проверьте введенные данные", "", "warning")
        },
        cancel_is_being_considered_form () {
            this.is_being_considered = false
        },

        open_purchase(purchase) {
            if (this.selected_status == "is_being_considered") {
                var filtration = {
                    id: purchase.product_id,
                    change_time: this.reformat_selected_change_time(),
                }

                axios("/api/purchase/get_is_being_considered_purchase/", {params: filtration}).then((response) => {
                    this.is_being_considered_form = response.data
                    this.is_being_considered_form["product_id"] = purchase.product_id
                    document.body.style.overflow = 'hidden';
                })
            } else {
                this.opened_purchase = purchase
                this.websocket.send(JSON.stringify({"product_id": this.opened_purchase.product_id, "action": "open"}))
                document.body.style.overflow = 'hidden';
            }
        },
        close_purchase_window() {
            document.body.style.overflow = '';

            if (this.opened_purchase != null) {
                this.websocket.send(JSON.stringify({"product_id": this.opened_purchase.product_id, "action": "close"}))
                this.opened_purchase = null
            }

            this.purchase_form = Object.assign({}, this.base_purchase_form)
            var replaced_by_product_image_upload_input = document.getElementById("replaced_by_product_image")

            if (replaced_by_product_image_upload_input) {
                replaced_by_product_image_upload_input.value = null
            }

            this.uploaded_files = {}
            this.cancel_purchasing()
        },

        paste_replaced_by_product_id() {
            this.purchase_form["replaced_by_product_id"] = localStorage.getItem("copied_replaced_by_product_id") || ""

            if (!this.purchase_form["replaced_by_product_id"]) {
                window.open("/", "_blank")
            }
        },
        check_purchase_inputted_data () {
            if (Number(this.purchase_form["purchased_count"]) + Number(this.purchase_form["replaced_count"]) + Number(this.purchase_form["not_available_count"]) + Number(this.purchase_form["will_be_tomorrow_count"]) != this.opened_purchase["count"]) {
                Swal.fire("Вам необходимо указать статусы для всего количества товаров", "", "error")
                return
            }

            if (this.purchase_form["replaced_count"] > 0 && !this.purchase_form["replaced_by_product_image"]) {
                Swal.fire("Загрузите фото товара (заменён)", "", "error")
                return
            }

            if (!(this.purchase_form["price_per_count"] > 0)) {
                Swal.fire("Вы забыли указать цену за штук", "", "error")
                return
            }

            Swal.fire({
                title: "Пожалуйста, внимательно проверьте введенные данные",
                icon: "warning",
            })
            this.purchasing_is_available = true
        },
        cancel_purchasing() {
            this.purchasing_is_available = false

        },
        make_purchase() {
            if (!this.purchase_is_making) {
                this.purchase_is_making = true

                var data = {
                    product_id: this.opened_purchase.product_id,
                    status: this.selected_status,
                    change_time: this.reformat_selected_change_time(),
                }

                data[this.purchase_form['replaced_by_product_image']] = this.uploaded_files[this.purchase_form['replaced_by_product_image']]

                axios.post("/api/purchase/make/",
                    Object.assign({}, data, this.purchase_form),
                    {
                        headers: {
                            "X-CSRFToken": $cookies.get("csrftoken"),
                            'Content-Type': 'multipart/form-data'
                        }
                    }
                ).then((response) => {
                    if (response.data["is_being_considered_report"]) {
                        this.is_being_considered_report = response.data["is_being_considered_report"]
                        document.body.style.overflow = 'hidden';
                    } else {
                        Swal.fire("Куплено", "", "success")
                    }

                    this.close_purchase_window()
                    this.cancel_purchasing()
                }).catch((err) => {
                    Swal.fire("Ошибка", "", "error")
                }).finally(() => {
                    this.purchase_is_making = false
                })
            }
        },
        close_is_being_considered_report() {
            this.is_being_considered_report = null
            document.body.style.overflow = '';
        },

        get_opened_by_other_fullname() {
            var not_found = true

            for (var i = 0; i < this.opened_by_others.length; i++) {
                if (this.opened_by_others[i].product_id == this.opened_purchase.product_id && this.opened_by_others[i].user_id != user_id) {
                    return this.opened_by_others[i].user_fullname + " рассматривает товар!"
                }
            }

            if (not_found) {
                this.open_purchase(this.opened_purchase)
            }
        },
        handle_websocket_message(event) {
            var data = JSON.parse(event.data);
            var data = data["message"]

            if (data["action"] == "purchases_count_changed") {
                this.select_change_time()
                if (this.opened_purchase) {
                    if (this.opened_purchase.product_id == data["product_id"]) {
                        this.close_purchase_window()
                        this.close_is_being_considered_form()
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
        purchase_actions_are_available() {
            return this.selected_change_time_is_today() && this.selected_status != "purchased" && this.selected_status != "replaced"

        },

        handle_file_upload(event) {
            var file = event.target.files[0]

            if (file) {
                this.purchase_form['replaced_by_product_image'] = file.name
                this.uploaded_files[file.name] = file
            }
        },

        open_product() {
            window.open("/product/?product_id=" + this.opened_purchase.product_id, "_blank")
        },

        get_comments() {
            axios("/api/purchase/get_purchase_comments/", {params: {
                product_id: this.opened_purchase.product_id,
                status: this.selected_status,
                change_time: this.reformat_selected_change_time()
            }}).then(
                (response) => {
                    this.comments = response.data
                }
            )
        }
    },
    mounted() {
        this.websocket.addEventListener('message', this.handle_websocket_message);
        this.websocket.addEventListener('close', this.handle_websocket_close);
        this.websocket.addEventListener('error', this.handle_websocket_close);
    }
})


purchases_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_purchases_app = purchases_app.mount("#purchases_section")
