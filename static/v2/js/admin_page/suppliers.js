suppliers_app = Vue.createApp({
    data() {
        return {
            suppliers: [],
        }
    },
    methods: {
        open_section() {
            this.get_suppliers()
        },
        close_section() {},
        get_suppliers() {
            axios("/api/supplier/get_suppliers/").then((response) => {
                this.suppliers = response.data
            })
        },
    },
})


suppliers_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_suppliers_app = suppliers_app.mount("#suppliers_section")
