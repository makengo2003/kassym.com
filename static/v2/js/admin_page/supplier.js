quill_modules = {
    'syntax': true,
    'toolbar': [
        ['bold', 'italic', 'underline', 'strike'],
        ['blockquote', 'code-block'],

        [{'header': 1}, {'header': 2}],
        [{'list': 'ordered'}, {'list': 'bullet'}],
        [{'script': 'sub'}, {'script': 'super'}],
        [{'indent': '-1'}, {'indent': '+1'}],
        [{'direction': 'rtl'}],

        [{'size': ['small', false, 'large', 'huge']}],
        [{'header': [1, 2, 3, 4, 5, 6, false]}],

        [{'color': []}, {'background': []}],
        [{'font': []}],
        [{'align': []}],

        ['link', 'video']
    ]
}


var base_opened_product = {
    category_id: null,
    code: null,
    name: null,
    count: null,
    description: "",
    supplier_price: null,
    height: null,
    width: null,
    length: null,
    images: [{image: ""}, {image: ""}, {image: ""}, {image: ""}],
}


supplier_app = Vue.createApp({
    data() {
        return {
            search_input: "",
            searched: false,
            products: [],
            opened_product: Object.assign({}, base_opened_product),
            categories: [],
            opened_ones: false,
            uploaded_images: {},
            is_getting_products: false,
            there_is_no_more_products: false,
            quill_editor: null,
            total_products_count: 0,
            saving_product: false
        }
    },
    methods: {
        open_section() {
            if (!this.opened_ones) {
                this.get_categories()
                this.get_products()
            }
        },
        close_section() {},

        get_categories() {
            this.opened_ones = true
            axios.get("/api/category/get_categories/").then((response) => {
                this.categories = response.data
            }).catch((error) => {
                Swal.fire({
                    title: "Произошла ошибка при получений категории",
                    icon: "error"
                }).then(() => {
                    window.location.reload()
                })
            })
        },
        get_products(current_products_count=0) {
            if (!this.is_getting_products) {
                this.is_getting_products = true
                var filtration = {offset: current_products_count}

                if (this.search_input) {
                    this.searched = true
                    filtration["search"] = this.search_input
                } else {
                    this.searched = false
                }

                axios.get("/api/supplier/get_products/", {params: filtration}).then((response) => {
                    this.uploaded_images = {}

                    if (current_products_count > 0) {
                        for (var i = 0; i < response.data["products"].length; i++) {
                            this.products.push(response.data["products"][i])
                        }
                    } else {
                        this.products = response.data["products"]
                    }

                    if (response.data["products"].length == 0) {
                        this.there_is_no_more_products = true
                    } else {
                        this.there_is_no_more_products = false
                    }

                    this.total_products_count = response.data["count"]
                }).catch((error) => {
                    Swal.fire({
                        title: "Произошла ошибка при получений товаров",
                        icon: "error"
                    }).then(() => {
                        window.location.reload()
                    })
                }).finally(() => {
                    this.is_getting_products = false
                })
            }
        },

        current_product_image(image) {
            if (image.image) {
                return image.image.startsWith("/media/")
            }
        },
        get_current_product_image(image) {
            return image.image.replace("/media/products_images/", "")

        },

        open_product(product=null) {
            if (product) {
                axios.get("/api/product/get_product/?product_id=" + product.id).then((response) => {
                    this.opened_product = response.data

                    if (this.opened_product.description) {
                        this.quill_editor.root.innerHTML = this.opened_product.description
                    } else {
                        this.quill_editor.root.innerHTML = ""
                    }
                })
            } else {
                this.opened_product = Object.assign({}, this.base_opened_product)
                this.opened_product["images"] = [{image: ""}, {image: ""}, {image: ""}, {image: ""}]

                if (this.opened_product.description) {
                    this.quill_editor.root.innerHTML = this.opened_product.description
                } else {
                    this.quill_editor.root.innerHTML = ""
                }
            }

            document.querySelectorAll("#supplier_section .product_window")[0].style.display = "block"
        },
        close_product() {
            this.uploaded_images = []
            document.querySelectorAll("#supplier_section .product_window")[0].style.display = "none"

            var uploads = document.getElementsByClassName("product_image_upload")
            for (var i = 0; i < uploads.length; i++) {
                uploads[i].value = null
            }
        },

        handle_product_image_upload(event, image, image_index) {
            var file = event.target.files[0]

            if (file) {
                image.image = "image_" + image_index + ": " + file.name
                this.uploaded_images[image.image] = file
            } else {
                delete this.uploaded_images[image.image]
                image.image = ""
            }
        },
        handle_scrolling() {
            var scrollTop = this.products_list_element.scrollTop;
            var scrollHeight = this.products_list_element.scrollHeight - this.products_list_element.clientHeight;
            var threshold = 900;

            if (scrollHeight - scrollTop < threshold && !this.there_is_no_more_products) {
                this.get_products(this.products.length)
            }
        },

        save_product() {
            if (!this.saving_product) {
                this.saving_product = true

                if (this.opened_product.id) {
                    var url = "/edit_product/"
                } else {
                    var url = "/add_product/"
                }

                if (this.opened_product["category_id"] != 7) {
                    this.opened_product["currency"] = "ru"
                }

                for (var i = 0; i < this.opened_product.images.length; i++) {
                    this.opened_product[this.opened_product.images[i]["image"]] = this.uploaded_images[this.opened_product.images[i]["image"]]
                }

                this.opened_product["description"] = this.quill_editor.root.innerHTML
                this.opened_product["images"] = JSON.stringify(this.opened_product.images)

                axios.post("/api/product" + url, this.opened_product, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        "X-CSRFToken": $cookies.get("csrftoken"),
                    }
                }).then((response) => {
                    if (this.opened_product.id) {
                        var product_id = this.opened_product.id
                    } else {
                        var product_id = response.data["product_id"]
                    }

                    axios.get("/api/supplier/get_products/", {params: {id: Number(product_id)}}).then((response) => {
                        if (this.opened_product.id) {
                            for (var i = 0; i < this.products.length; i++) {
                                if (this.products[i].id == this.opened_product.id) {
                                    this.products[i] = response.data["products"][0]
                                    break
                                }
                            }
                        } else {
                            this.products.unshift(response.data["products"][0])
                            this.total_products_count += 1
                        }
                    })

                    this.close_product()
                }).catch((error) => {
                    Swal.fire("Ошибка при сохранений товара", "", "error")
                }).finally(() => {
                    this.saving_product = false
                })
            }
        },
        delete_product() {
            Swal.fire({
                title: "Удалить товар?",
                icon: "question",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Да",
                cancelButtonText: "Нет"
            }).then((result) => {
                if (result.isConfirmed) {
                    axios.post("/api/product/delete_product/", {product_id: this.opened_product.id}, {
                        headers: {
                            "X-CSRFToken": $cookies.get("csrftoken"),
                        }
                    }).then((response) => {
                        for (var i = 0; i < this.products.length; i++) {
                            if (this.products[i].id == this.opened_product.id) {
                                this.products.splice(i, 1)
                                break
                            }
                        }

                        this.close_product()
                        this.total_products_count -= 1
                    }).catch((error) => {
                        Swal.fire("Ошибка при удалений товара", "Возможно, товар был заказан до этого момента", "error")
                    })
                }
            })
        }
    },
    mounted() {
        this.quill_editor = new Quill('#quill_editor', {
            theme: 'snow',
            modules: quill_modules
        })
        this.products_list_element = document.getElementById("supplier_products_list")
        this.products_list_element.onscroll = this.handle_scrolling
    }
})


supplier_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_supplier_app = supplier_app.mount("#supplier_section")
