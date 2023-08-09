product_app = Vue.createApp({
    data() {
        return {
            product: {},
            current_image: "",
        }
    },
    methods: {
        get_product() {
            ProductServices.get_product(this.product["id"]).then((data) => {
                this.product = data

                for (var i = 0; i < data["images"].length; i++) {
                    if (data["images"][i]["default"]) {
                        this.current_image = data["images"][i]["image"]
                        break
                    }
                }

                if (!user_is_authenticated) {
                    this.product["is_favourite"] = false

                    var favourite_products = this.get_local_favourite_products()
                    for (var i = 0; i < favourite_products.length; i++) {
                        if (favourite_products[i] == this.product["id"]) {
                            this.product["is_favourite"] = true
                            break
                        }
                    }
                }

                var quill = new Quill('#product_description', {});
                quill.enable(false)

                quill.root.innerHTML = data["description"]
            })
        },
        open_current_image() {
            window.location.hash = "main_image_window"
            document.getElementById("current_image").src = this.current_image
        },
        show_product_image(image) {
            this.current_image = image
        },
    },
    mounted() {
        var url_params = new URLSearchParams(window.location.search);
        this.product["id"] = Number(url_params.get('product_id'))
        this.get_product()
    }
})

product_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_product_app = product_app.mount("#product_app")
