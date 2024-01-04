sidebar_app = Vue.createApp({
    data() {
        return {
            opened_section: "",
            sections: {
                "orders": mounted_orders_app,
                "settings": {
                    open_section() {},
                    close_section() {},
                },
                "purchases": mounted_purchases_app,
                "sorting": mounted_sorting_app,
//                "delivering": mounted_delivering_app,
                "finance": mounted_finance_app,
                "is_being_considered": mounted_is_being_considered_app,
                "expenses": mounted_expenses_app,
                "supplier": mounted_supplier_app,
                "suppliers": mounted_suppliers_app,
                "tech_support": mounted_tech_support_app,
            }
        }
    },
    methods: {
        open_section(section) {
            if (this.opened_section) {
                this.sections[this.opened_section].close_section()
                document.getElementById(this.opened_section + "_section").style.display = "none"
            }

            this.opened_section = section
            window.location.hash = this.opened_section
            this.sections[this.opened_section].open_section()
            document.getElementById(this.opened_section + "_section").style.display = "block"
            document.getElementById("burger_btn").classList.remove("active")
            document.getElementById("sidebar").classList.remove("active")
            document.body.style.overflow = '';
        }
    },
    mounted() {
        if (window.location.hash) {
            this.open_section(window.location.hash.slice(1, window.location.hash.length))
        } else {
            if (window.location.href.includes("buyer")) {
                this.open_section("purchases")
            } else if (window.location.href.includes("supplier")) {
                this.open_section("supplier")
            } else {
                this.open_section("orders")
            }
        }
    }
})

sidebar_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_sidebar_app = sidebar_app.mount("#sidebar")
