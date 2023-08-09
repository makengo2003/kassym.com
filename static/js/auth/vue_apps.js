sign_up_app = Vue.createApp({
    data() {
        return {
            SignUpRequestSchema: {
                first_name: "",
                last_name: "",
                username: "",
                password1: "",
                password2: "",
            },
            sign_up_form_errors: []
        }
    },
    methods: {
        sign_up_request() {
            this.sign_up_form_errors = []
            document.getElementById("sign_up_form_submit_btn").disabled = true
            UserServices.sign_up(this.SignUpRequestSchema)
        }
    }
})

sign_up_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_sign_up_app = sign_up_app.mount("#reg_window")



confirm_sign_up_app = Vue.createApp({
    data() {
        return {
            ConfirmSignUpRequestSchema: {
                succ_token: "",
                confirmation_code: 0,
            }
        }
    },
    methods: {
        re_send_succ_request() {
            document.getElementById("re_send_is_available_after_seconds").style.display = "block"
            document.getElementById("re_send_succ_btn").style.display = "none"
            UserServices.re_send_succ(this.ConfirmSignUpRequestSchema)
        },
        confirm_sign_up_request() {
            document.getElementById("invalid_succ_err_msg").style.display = "none"
            document.getElementById("confirm_sign_up_form_submit_btn").disabled = true
            UserServices.confirm_sign_up(this.ConfirmSignUpRequestSchema)
        },
        cancel_confirm_sign_up() {
            UserServices.cancel_confirm_sign_up()
        }
    }
})

confirm_sign_up_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_confirm_sign_up_app = confirm_sign_up_app.mount("#conf_window")





login_app = Vue.createApp({
    data() {
        return {
            LoginRequestSchema: {
                username: "",
                password: "",
            },
            login_form_errors: []
        }
    },
    methods: {
        login_request() {
            this.login_form_errors = []
            document.getElementById("login_form_submit_btn").disabled = true
            this.LoginRequestSchema["product_id_for_buying_now"] = product_id_for_buying_now
            this.LoginRequestSchema["product_count_for_buying_now"] = product_count_for_buying_now
            this.LoginRequestSchema["cart_id_for_buying_now"] = cart_id_for_buying_now
            UserServices.login(this.LoginRequestSchema)
        }
    }
})

login_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_login_app = login_app.mount("#log_window")






change_password_app = Vue.createApp({
    data() {
        return {
            ChangePasswordRequestSchema: {
                old_password: '',
                new_password1: '',
                new_password2: '',
            },
            change_password_form_errors: []
        }
    },
    methods: {
        change_password_request() {
            this.change_password_form_errors = []
            document.getElementById("change_password_form_submit_btn").disabled = true
            UserServices.change_password(this.ChangePasswordRequestSchema)
        }
    }
})

change_password_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_change_password_app = change_password_app.mount("#change_password_window")


forget_password_app = Vue.createApp({
    data() {
        return {
            forget_password_form: {
                phone_number: '',
            }
        }
    },
    methods: {
        forget_password_form_submit() {
            document.getElementById("forget_password_form_submit_btn").disabled = true

            UserServices.forget_password(this.forget_password_form).then((data) => {
                if (data["success"]) {
                    swal("Пароль успешно отправлен на номер!")
                    this.forget_password_form["phone_number"] = ""
                } else {
                    swal("Пользователь не найден!")
                }

                document.getElementById("forget_password_form_submit_btn").disabled = false
            })
        }
    }
})


forget_password_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_forget_password_app = forget_password_app.mount("#forget_password_window")
