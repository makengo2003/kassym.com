is_being_considered_app = Vue.createApp({
    data() {
        return {
            purchases: [],
            opened_purchase: null,

            change_times: [],
            selected_change_time: null,

            selected_status: "not_available",
            opened_product_image: ""
        }
    },
    methods: {
        open_section() {
            this.select_change_time()

        },
        close_section() {},

        select_status(status) {
            this.selected_status = status
            this.get_purchases()
        },
        select_change_time() {
            if (this.selected_change_time) {
                this.get_purchases()
            } else {
                axios("/api/change_time/get_many/").then((response) => {
                    this.change_times = response.data.slice(1, -1)
                    this.selected_change_time = this.change_times[0]["dt"]
                    this.get_purchases()
                })
            }
        },

        get_change_time() {
            return this.selected_change_time.split(".").reverse().join("-")

        },

        get_purchases() {
            axios("/api/purchase/get_purchases/", {
                params: {
                    status: this.selected_status,
                    change_time: this.get_change_time()
                }
            }).then((response) => {
                this.purchases = response.data
            })
        },

        open_purchase(purchase) {
            var filtration = {
                product_id: purchase.product_id,
                change_time: this.get_change_time(),
                status: this.selected_status
            }

            axios("/api/purchase/get_purchase_for_manager/", {params: filtration}).then((response) => {
                this.opened_purchase = response.data
            })
        },
    }
})


is_being_considered_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_is_being_considered_app = is_being_considered_app.mount("#is_being_considered_section")
