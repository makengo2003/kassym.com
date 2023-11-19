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
        }
    },
    mounted() {
        if (window.location.hash) {
            this.open_section(window.location.hash.slice(1, window.location.hash.length))
        } else {
            this.open_section("orders")
        }
    }
})

sidebar_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_sidebar_app = sidebar_app.mount("#sidebar")
