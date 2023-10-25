settings_app = Vue.createApp({
    data() {
        return {
            contacts_form_is_opened: false,
            guarantee_form_is_opened: false,
            about_us_form_is_opened: false,
            about_us_quill: null,
            footer_contact_quill: null,
            slides: [],
            slides_form_is_opened: false,
            contacts_form: {
                phone_number: {
                    contact: "+7",
                },
                whatsapp: {
                    contact: "+7",
                },
                instagram: {
                    contact: "",
                },
                email: {
                    contact: "",
                },
                order_manager: {
                    contact: "",
                },
                footer: {
                    contact: "",
                },
                telegram_chat_id: {
                    contact: "",
                }
            },
            guarantee_form: {
                file: null,
            }
        }
    },
    methods: {
        open() {},
        close() {},
        window_scroll_down_event_listener() {},
        open_about_us_form() {
            this.about_us_form_is_opened = true
            SiteSettingsServices.get_about_us_text().then((data) => {
                document.getElementById("about_us_quill").innerHTML = data["about_us"]
                this.about_us_quill = new Quill('#about_us_quill', {
                    theme: 'snow',
                    modules: quill_modules
                })
            })
        },
        about_us_form_submit() {
            SiteSettingsServices.save_about_us_text(this.about_us_quill.root.innerHTML)
            this.about_us_form_is_opened = false
        },
        open_guarantee_form() {
            this.guarantee_form_is_opened = true

        },
        guarantee_form_submit() {
            if (this.guarantee_form["file"]) {
                SiteSettingsServices.save_guarantee_text(this.guarantee_form)
            }
            this.guarantee_form_is_opened = false
        },
        handle_guarantee_file_upload(event) {
            var file = event.target.files[0]

            if (file) {
                delete this.guarantee_form["file"]
                this.guarantee_form["file"] = file
            } else {
                delete this.guarantee_form["file"]
            }
        },
        open_contacts_form() {
            this.contacts_form_is_opened = true
            SiteSettingsServices.get_contacts().then((data) => {
                for (var i = 0; i < data.length; i++) {
                    this.contacts_form[data[i]["type"]] = {
                        contact: data[i]["contact"]
                    }
                }
                if (!this.footer_contact_quill) {
                    this.footer_contact_quill = new Quill('#footer_contact_quill', {
                        theme: 'snow',
                        modules: {
                            'syntax': true,
                            'toolbar': [
                                [{ 'size': [] }],
                                [ 'bold', 'italic', 'underline', 'strike' ],
                                [ 'link' ]
                            ]
                        }
                    })
                }
                this.footer_contact_quill.root.innerHTML = this.contacts_form["footer"]["contact"]
            })
        },
        save_contacts() {
            this.contacts_form["footer"]["contact"] = this.footer_contact_quill.root.innerHTML
            var contacts_form = []
            for (var key in this.contacts_form) {
                var link = ""

                if (key == "phone_number") {
                    link += "tel:"
                } else if (key == "email") {
                    link += "mailto:"
                } else if (key == "whatsapp" || key == "order_manager") {
                    link += "https://wa.me/"
                } else if (key == "instagram") {
                    link += "https://www.instagram.com/"
                }

                link += this.contacts_form[key]["contact"]
                contacts_form.push({type: key, contact: this.contacts_form[key]["contact"], link: link})
            }
            SiteSettingsServices.save_contacts({contacts: contacts_form})
            this.contacts_form_is_opened = false
        },
        add_slide() {
            this.slides.push({image: "", link: ""})

        },
        delete_slide(key) {
            this.slides.splice(key, 1)

        },
        open_slides_form() {
            this.slides_form_is_opened = true
            axios("/api/site_settings/get_slides/").then((response) => {
                this.slides = response.data
            })
            this.uploaded_slides = {}
        },
        slides_form_submit() {
            var form_data = new FormData()
            this.uploaded_slides['slides'] = JSON.stringify(this.slides)

            for (var key in this.uploaded_slides) {
                form_data.append(key, this.uploaded_slides[key]);
            }

            return axios.post("/api/site_settings/save_slides/", form_data, {
                headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
                }
            }).then((response) => {
                this.slides = []
                this.slides_form_is_opened = false
                this.uploaded_slides = {}
                this.open()
            })
        },
        slide_is_uploaded_to_input(slide) {
            return !(slide.image.startsWith("slide_images/"))

        },
        handle_file_upload(slide, event) {
            var file = event.target.files[0]
            if (file) {
                slide["image"] = file.name
                this.uploaded_slides["image: " + file.name] = file
            }
        },
    },
    computed: {
        settings_section_is_opened() {
            return (this.contacts_form_is_opened || this.slides_form_is_opened || this.about_us_form_is_opened || this.guarantee_form_is_opened)
        }
    }
})


settings_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_settings_app = settings_app.mount("#settings")
