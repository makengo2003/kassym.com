expenses_app = Vue.createApp({
    data() {
        return {
            selected_change_time: null,
            change_times: [],
            expenses: [],
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
            axios("/api/user/get_expenses/", {params: {change_time: this.selected_change_time.split(".").reverse().join("-")}}).then((response) => {
                this.expenses = response.data
            })
        },
        selected_change_time_is_today() {
            return this.change_times.slice(-1) == this.selected_change_time
        },
    },
})


expenses_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_expenses_app = expenses_app.mount("#expenses_section")
