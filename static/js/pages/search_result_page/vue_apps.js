search_result_app = Vue.createApp({
    data() {
        return {
	    search_input: "",
            is_getting_products: false,
            there_is_no_more_products: false
        }
    },
    methods: {
        get_products_request() {
            if (!this.there_is_no_more_products) {
                this.is_getting_products = true

                ProductServices.get_products({
		   products_filtration: JSON.stringify({
			already_fetched_products_count: mounted_products_app.products.length,
			search_input: this.search_input
		   })
		}).then((data) => {
                    if (data["success"]) {
                        if (data["data"].length == 0) {
                            this.there_is_no_more_products = true
                        }

                        this.is_getting_products = false
                    }
                })
            }
        },
    },
    mounted() {
        var url_params = new URLSearchParams(window.location.search);
	this.search_input = url_params.get('search_input')
	this.get_products_request()

        window.onscroll = () => {
            if (!this.is_getting_products && mounted_products_app.products.length != 0 && !this.there_is_no_more_products) {
                if (window.scrollY + window.innerHeight + 630 >= document.body.scrollHeight) {
                    this.get_products_request()
                }
            }
        }
    }
})

search_result_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_search_result_app = search_result_app.mount("#search_result_app")
