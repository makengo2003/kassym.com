products_app = Vue.createApp({
    data() {
        return {
            products: [],
	   scroll_position: 0,
	   div_display_style: "",
            actionable_element_is_in_action: false,
        }
    },
    methods: {
        get_products(GetProductsRequestSchema) {
            ProductServices.get_products(GetProductsRequestSchema)
        },
        update_product_is_favourite_field(product) {
            if (product.is_favourite) {
                UserServices.add_products_to_favourites([product.id])
            } else {
                UserServices.remove_product_from_favourites(product.id)
            }
        },
        open_product_page(event, product) {
            if (!this.actionable_element_is_in_action) {
		event.preventDefault()
                this.scroll_position = window.scrollY
                this.div_display_style = document.getElementById("div_closes_when_product_opens").getAttribute('style')
		document.getElementById("div_closes_when_product_opens").style.display = "none"
		document.getElementById("product_preview").style.display = "initial"
		mounted_product_app.product["id"] = Number(product.id)
		mounted_product_app.get_product()
		window.scrollTo(0, 0)
            }
        },
        actionable_element_mouse_over() {
            this.actionable_element_is_in_action = true

        },
        actionable_element_mouse_out() {
            this.actionable_element_is_in_action = false

        },
    }
})

products_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_products_app = products_app.mount("#products_app")
