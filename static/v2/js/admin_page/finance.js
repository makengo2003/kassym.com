finance_app = Vue.createApp({
    data() {
        return {
            selected_change_time: null,
            change_times: [],
            finance: {
                total_price: 0,
                total_products_price: 0,
            },
        }
    },
    methods: {
        open_section() {
            if (this.selected_change_time == null) {
                this.get_change_times()
            }
        },
        close_section() {},
        get_change_times() {
            axios("/api/change_time/get_many/").then((response) => {
                this.change_times = response.data
                this.selected_change_time = this.change_times[0].dt
                this.select_change_time()
            })
        },
        select_change_time() {
            axios("/api/user/get_finance/", {params: {change_time: this.selected_change_time.split(".").reverse().join("-")}}).then((response) => {
                this.finance = response.data
            })
        },
    },
})


finance_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_finance_app = finance_app.mount("#finance_section")
