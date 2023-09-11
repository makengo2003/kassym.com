var base_staff_form_data = {
    id: 0,
    username: "",
    first_name: "",
    last_name: "",
    on_submit: false,
    errors: []
}


staffs_app = Vue.createApp({
    data() {
        return {
            staff_form: Object.assign({}, base_staff_form_data),
            staffs: [],
        }
    },
    methods: {
        open() {
            if (this.staffs.length == 0) {
                this.get_staffs()
            }
        },
        get_staffs() {
            axios("/api/staff/get_many/").then((response) => {
                this.staffs = response.data
            })
        },
        close() {},
        window_scroll_down_event_listener() {},
        open_staff_form(staff=null) {
            if (staff) {
                axios("/api/staff/get/", {params: {id: staff.id}}).then((response) => {
                    this.staff_form = Object.assign(this.staff_form, response.data)
                })
            } else {
                if (this.staff_form["id"] != 0) {
                    this.staff_form = Object.assign({}, base_staff_form_data)
                }
            }

            document.getElementById("staff_form_window").style.display = "block"
        },
        staff_form_submit() {
            if (!this.staff_form["on_submit"]) {
                this.staff_form["on_submit"] = true

                if (this.staff_form["id"]) {
                    var submit_url = "/api/staff/edit/"
                } else {
                    var submit_url = "/api/staff/add/"
                }

                axios.post(submit_url, this.staff_form, {
                    headers: {
                        "X-CSRFToken": $cookies.get("csrftoken")
                    }
                }).then((response) => {
                    document.getElementById("staff_form_window").style.display = "none"
                    this.staff_form = Object.assign({}, base_staff_form_data)
                    this.get_staffs()
                }).catch((error) => {
                    if (error.response) {
                        if (error.response.status == 400) {
                            this.staff_form.errors = []
                            for (var key in error.response.data) {
                                for (var err in error.response.data[key]) {
                                    this.staff_form.errors.push(error.response.data[key][err])
                                }
                            }
                        } else {
                            swal("Упс", "Что-то пошло не так!")
                        }
                    }
                }).finally(() => {
                    this.staff_form["on_submit"] = false
                })
            }
        },
        delete_staff() {
            swal({
              title: "Подтвердите ваше действия. Вы хотите удалить пользователя?",
              icon: "warning",
              buttons: true,
              dangerMode: true,
            }).then((will) => {
                if (will) {
                    axios.post("/api/staff/delete/", {id: this.staff_form.id}, {headers: {"X-CSRFToken": $cookies.get("csrftoken")}}).then((response) => {
                        document.getElementById("staff_form_window").style.display = "none"
                        this.staff_form = Object.assign({}, base_staff_form_data)
                        this.get_staffs()
                    })
                }
            })
        },
    },
})


staffs_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_staffs_app = staffs_app.mount("#staffs")


