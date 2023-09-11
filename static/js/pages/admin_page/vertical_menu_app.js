vertical_menu_app = Vue.createApp({
    data() {
        return {
            current_section: "products",
            previous_section: "",
            section_apps: {
                products: mounted_products_app,
                clients: mounted_clients_app,
                settings: mounted_settings_app,
                courses: mounted_courses_app,
                staffs: mounted_staffs_app
            }
        }
    },
    methods: {
        open_section() {
            if (this.previous_section != "") {
                document.getElementById(this.previous_section).style.display = "none"
                this.section_apps[this.previous_section].close()
            }
            document.getElementById(this.current_section).style.display = "block"
            this.previous_section = this.current_section
            this.section_apps[this.current_section].open()

            if (history.pushState) {
                var params = new URLSearchParams(window.location.search)
                params.set("section", this.current_section)

                var new_url = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + params.toString();
                window.history.pushState({path: new_url},'',new_url);
            }
        }
    },
    mounted() {
        var url_params = new URLSearchParams(window.location.search);
        var section = url_params.get('section');

        if (section) {
            this.current_section = section
        }

        this.open_section()

        window.onscroll = () => {
            if (window.scrollY + window.innerHeight + 630 >= document.body.scrollHeight) {
                this.section_apps[this.current_section].window_scroll_down_event_listener()
            }
        };
    }
})


vertical_menu_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_vertical_menu_app = vertical_menu_app.mount("#vertical_menu_app")

