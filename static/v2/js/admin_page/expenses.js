expenses_app = Vue.createApp({
    data() {
        return {
            selected_change_time: null,
            change_times: [],
            expenses: [],
            total_expenses_sum_in_ruble: 0,
            total_expenses_sum_in_tenge: 0,
            opened_expense_form: null
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
            axios("/api/expense/get_expenses/", {params: {change_time: this.selected_change_time.split(".").reverse().join("-")}}).then((response) => {
                this.expenses = response.data["expenses"]
                this.total_expenses_sum_in_ruble = response.data["total_expenses_sum_in_ruble"]
                this.total_expenses_sum_in_tenge = response.data["total_expenses_sum_in_tenge"]
            })
        },
        selected_change_time_is_today() {
            if (this.change_times[0]) {
                return this.change_times[0].dt == this.selected_change_time
            }
        },
        open_expense_form() {
            this.opened_expense_form = {
                sum: "",
                description: "",
                change_time: this.selected_change_time.split(".").reverse().join("-"),
                currency: ""
            }
        },
        close_expense_form() {
            this.opened_expense_form = null

        },
        save_expense() {
            Swal.fire({
                title: "Сохранить?",
                icon: "question",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Да",
                cancelButtonText: "Нет"
            }).then((result) => {
                if (result.isConfirmed) {
                    axios.post("/api/expense/save/", this.opened_expense_form, {
                        headers: {
                            "X-CSRFToken": $cookies.get("csrftoken"),
                        }
                    }).then((response) => {
                        Swal.fire("Сохранен", "", "success")
                        this.close_expense_form()
                        this.select_change_time()
                    }).catch((error) => {
                        Swal.fire("Ошибка", "Не удалось сохранить расходы", "error")
                    })
                }
            })
        }
    },
})


expenses_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_expenses_app = expenses_app.mount("#expenses_section")
