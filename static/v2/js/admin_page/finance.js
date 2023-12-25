finance_app = Vue.createApp({
    data() {
        return {
            selected_change_time: null,
            change_times: [],
            finance: {},

            selected_employee: "",
            employee_expenses: [],
            employees: [],

            total_expenses_sum_in_ruble: 0,
            total_expenses_sum_in_tenge: 0,
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
                this.selected_employee = ""
                this.select_employee()

                this.employees = []

                for (var i = 0; i < this.finance["expenses"].length; i++) {
                    if (!this.employees.includes(this.finance["expenses"][i]["employee_fullname"])) {
                        this.employees.push(this.finance["expenses"][i]["employee_fullname"])
                    }
                }
            })
        },
        select_employee() {
            this.employee_expenses = []
            this.total_expenses_sum_in_ruble = 0
            this.total_expenses_sum_in_tenge = 0

            if (this.selected_employee) {
                for (var i = 0; i < this.finance["expenses"].length; i++) {
                    if (this.finance["expenses"][i]["employee_fullname"] == this.selected_employee) {
                        this.employee_expenses.push(this.finance["expenses"][i])
                    }
                }
            } else {
                this.employee_expenses = Array.from(this.finance["expenses"])
            }

            for (var i = 0; i < this.employee_expenses.length; i++) {
                if (this.employee_expenses[i]["currency"] == "рубль") {
                    this.total_expenses_sum_in_ruble += this.employee_expenses[i]["sum"]
                } else {
                    this.total_expenses_sum_in_tenge += this.employee_expenses[i]["sum"]
                }
            }
        },
    },
})


finance_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_finance_app = finance_app.mount("#finance_section")
