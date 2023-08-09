class SiteSettingsServices {
    static get_contacts() {
        return axios.get("/api/site_settings/get_contacts/").then(response => response.data)
    }

    static save_contacts(contacts_form) {
        axios.post("/api/site_settings/save_contacts/", contacts_form, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        })
    }

    static get_about_us_text() {
        return axios.get("/api/site_settings/get_about_us_text/").then(response => response.data)
    }

    static save_about_us_text(text) {
        axios.post("/api/site_settings/save_about_us_text/", {text: text}, {
            headers: {
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        })
    }

    static save_guarantee_text(guarantee_form) {
        axios.post("/api/site_settings/save_guarantee_text/", guarantee_form, {
            headers: {
                'Content-Type': 'multipart/form-data',
                "X-CSRFToken": $cookies.get("csrftoken"),
            }
        })
    }
}