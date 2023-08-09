filter_app = Vue.createApp({
    data() {
        return {
            categories: [],
            current_category: {
                id: 0,
                filtration: [],
                min_price: 0,
                max_price: 0,
            },
            filtration: [],
            price_filtration: {
                max_price: 0,
                min_price: 0
            },
            price_filtration_slider_minimum_difference: 1000,
            order_by: "-id",
            products_filtration: {},
            is_getting_products: false,
            there_is_no_more_products: false
        }
    },
    methods: {
        get_products_request() {
            if (!this.there_is_no_more_products) {
                this.is_getting_products = true
                this.products_filtration["already_fetched_products_count"] = mounted_products_app.products.length
                this.products_filtration["category_id"] = this.current_category["id"]
                this.products_filtration["price__range"] = [this.price_filtration["min_price"], this.price_filtration["max_price"]]
                ProductServices.get_products({
                    products_filtration: JSON.stringify(this.products_filtration),
                    products_options_filtration: JSON.stringify(this.filtration),
                    products_order_by: this.order_by
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
        reset_then_get_products() {
            this.there_is_no_more_products = false
            mounted_products_app.products = []
            this.get_products_request()
        },
        get_category(category_id) {
            this.current_category["id"] = category_id
            this.filtration = []

            var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?category_id=' + category_id;
            window.history.pushState({path:newurl},'',newurl);

            CategoryServices.get_category(category_id).then((data) => {
                this.current_category = data

                this.price_filtration["min_price"] = data["min_price"]
                this.price_filtration["max_price"] = data["max_price"]
                this.price_filtration_slider_minimum_difference = data["max_price"] * 0.1

                this.reset_then_get_products()
            })
        },
        get_products(option_name, value) {
            var found = false

            for (var i = 0; i < this.filtration.length; i++) {
                if (this.filtration[i]["option_name"] == option_name) {
                    found = true

                    if (this.filtration[i]["values"].indexOf(value) == -1) {
                        this.filtration[i]["values"].push(value)
                    } else {
                        this.filtration[i]["values"].splice(this.filtration[i]["values"].indexOf(value), 1)

                        if (this.filtration[i]["values"].length == 0) {
                            this.filtration.splice(i, 1)
                        }
                    }

                    break
                }
            }

            if (!found) {
                this.filtration.push({option_name: option_name, values: [value]})
            }

            this.reset_then_get_products()
        },
        slide_one() {
            if(parseInt(this.price_filtration["max_price"]) - parseInt(this.price_filtration["min_price"]) <= this.price_filtration_slider_minimum_difference){
                this.price_filtration["min_price"] = parseInt(this.price_filtration["max_price"]) - this.price_filtration_slider_minimum_difference;
            }
            this.price_filtration["min_price"] = Number(this.price_filtration["min_price"])
        },
        slide_two() {
            if(parseInt(this.price_filtration["max_price"]) - parseInt(this.price_filtration["min_price"]) <= this.price_filtration_slider_minimum_difference){
                this.price_filtration["max_price"] = parseInt(this.price_filtration["min_price"]) + this.price_filtration_slider_minimum_difference;
            }
            this.price_filtration["max_price"] = Number(this.price_filtration["max_price"])
        }
    },
    mounted() {
        CategoryServices.get_categories().then(data => this.categories = data)

        var url_params = new URLSearchParams(window.location.search);
        this.get_category(Number(url_params.get('category_id')))

        window.onscroll = () => {
		console.log(window.scrollY, window.innerHeight)
            if (!this.is_getting_products && mounted_products_app.products.length != 0 && !this.there_is_no_more_products) {
                if (window.scrollY + window.innerHeight + 630 >= document.body.scrollHeight) {
                    this.get_products_request()
                }
            }
        }
    }
})

filter_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_filter_app = filter_app.mount("#filter_app")
