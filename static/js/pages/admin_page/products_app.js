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

        ['link', 'image', 'video']
    ],
    "imageResize": {
        "modules": ['Resize', 'DisplaySize', 'Toolbar']
    }
}


products_app = Vue.createApp({
    data() {
        return {
            current_section: "all_products",
            categories: [],
            current_category: null,
            products: [],
            category_form: {
                category_id: 0,
                name: "",
                poster: "",
                is_available: false,
                filtration: [{name: "", values: []}],
                on_submit: false,
            },
            product_form: {
                product_id: 0,
                category_id: 0,
                name: "",
                description: "",
                price: 0,
                count: 0,
                is_available: false,
                code: "",
                vendor_number: "",
                currency: "ru",
                images: [{image: "", "default": true}, {image: "", "default": false}, {image: "", "default": false}, {image: "", "default": false}],
                options: [],
                on_submit: false,
                category_filtration: []
            },
            product_form_description_editor: null,
            product_form_short_description_editor: null,
            drag_and_drop: {
                index: null,
                list: null,
            },
            is_getting_products: false,
            admin_searched_products: false,
            search_products_input: "",
            order_form: {
                product: {},
                date: "",
                count: 1,
                company_name: ""
            },
            order_form_is_submitting: false
        }
    },
    methods: {
        open() {
            if (this.products.length == 0) {
                this.open_section()
            }
        },
        close() {},
        open_section() {
            if (this.categories.length == 0) {
                CategoryServices.get_categories().then((data) => {
                    this.categories = data
                })
            }

            if (this.current_section == "all_products") {
                this.products = []
                ProductServices.get_products({
                }).then((response) => {
                    if (response["data"].length == 0) {
                        this.there_is_no_more_products = true
                    } else {
                        this.there_is_no_more_products = false
                    }
                })
            } else {
                this.products = []

                if (this.current_category == null) {
                    if (this.categories.length > 0) {
                        this.current_category = this.categories[0]
                    }
                }

                if (this.current_category) {
                    ProductServices.get_products({
                        products_filtration: JSON.stringify({category_id: this.current_category.id})
                    }).then((response) => {
                        if (response["data"].length == 0) {
                            this.there_is_no_more_products = true
                        } else {
                            this.there_is_no_more_products = false
                        }
                    })
                }
            }
        },
        get_category_products() {
            this.products = []
            ProductServices.get_products({
                products_filtration: JSON.stringify({category_id: this.current_category.id})
            }).then((response) => {
                if (response["data"].length == 0) {
                    this.there_is_no_more_products = true
                } else {
                    this.there_is_no_more_products = false
                }
            })
        },
        open_category_form(category=null) {
            for (var key in this.category_form) {
                if (key.startsWith("poster: ")) {
                    delete this.category_form[key]
                }
            }

            var product_form_image_inputs = document.getElementsByClassName("product_form_image_input")

            for (var i = 0; i < product_form_image_inputs.length; i++) {
                product_form_image_inputs[i].value = null
            }

            if (category) {
                CategoryServices.get_category(category.id).then((data) => {
                    this.category_form = {
                        category_id: category.id,
                        name: category.name,
                        poster: category.poster,
                        is_available: data["is_available"],
                        filtration: data["filtration"],
                        on_submit: false,
                    }

                    for (var i = 0; i < this.category_form["filtration"].length; i++) {
                        var values = this.category_form["filtration"][i]["values"][0].value

                        for (var j = 1; j < this.category_form["filtration"][i]["values"].length; j++) {
                            values += "; " + this.category_form["filtration"][i]["values"][j].value
                        }

                        this.category_form["filtration"][i]["values"] = values
                    }

                    window.location.hash = "category_form_window"
                })
            } else {
                if (this.category_form["category_id"] != 0) {
                    this.category_form = {
                        category_id: 0,
                        name: "",
                        poster: "",
                        is_available: false,
                        filtration: [{name: "", values: []}],
                        on_submit: false,
                    }
                }
                window.location.hash = "category_form_window"
            }
        },
        open_product_form(product=null) {
            if (product) {
                ProductServices.get_product(product.id).then((data) => {
                    this.product_form = {
                        product_id: product.id,
                        category_id: data["category_id"],
                        name: data["name"],
                        description: data["description"],
                        price: data["price"],
                        count: data["count"],
                        is_available: data["is_available"],
                        code: data["code"],
                        vendor_number: data["vendor_number"],
                        images: data["images"],
                        options: data["options"],
                        on_submit: false,
                        category_filtration: [],
                        height: data["height"],
                        width: data["width"],
                        length: data["length"],
                        currency: data["currency"]
                    }

                    if (this.product_form_description_editor == null) {
                        this.product_form_description_editor = new Quill('#product_form_description_editor', {
                            theme: 'snow',
                            modules: quill_modules
                        })
                    }
                    this.product_form_description_editor.root.innerHTML = this.product_form["description"]

                    document.getElementById("product_form_window").style.display = "block"

                    this.set_category_filtration()

                    for (var i = 0; i < this.product_form["options"].length; i++) {
                        if (this.get_option_values(this.product_form["options"][i]).length == 0) {
                            this.product_form["options"][i]["values_text"] = this.product_form["options"][i]["values"][0]["value"]
                            this.product_form["options"][i]["values"] = []
                        }
                    }

                    for (var i = 0; i < this.product_form["images"].length; i++) {
                        if (this.product_form["images"][i]["default"]) {
                            var temp = this.product_form["images"][i]
                            this.product_form["images"][i] = this.product_form["images"][0]
                            this.product_form["images"][0] = temp
                            break
                        }
                    }
                })
            } else {
                if (this.product_form["product_id"] != 0) {
                    this.product_form = {
                        product_id: 0,
                        category_id: 0,
                        name: "",
                        description: "",
                        price: 0,
                        count: 0,
                        is_available: false,
                        code: "",
                        vendor_number: "",
                        currency: "ru",
                        images: [{image: "", "default": true}, {image: "", "default": false}, {image: "", "default": false}, {image: "", "default": false}],
                        options: [],
                        on_submit: false,
                        category_filtration: []
                    }
                }

                if (this.product_form_description_editor == null) {
                    this.product_form_description_editor = new Quill('#product_form_description_editor', {
                        theme: 'snow',
                        modules: quill_modules
                    })
                }
                this.product_form_description_editor.root.innerHTML = this.product_form["description"]

                document.getElementById("product_form_window").style.display = "block"
            }

            var product_form_image_inputs = document.getElementsByClassName("product_form_image_input")

            for (var i = 0; i < product_form_image_inputs.length; i++) {
                product_form_image_inputs[i].value = null

            }

            for (var key in this.product_form) {
                if (key.startsWith("image: ")) {
                    delete this.product_form[key]
                }
            }
        },
        change_product_is_available_status(product) {
            ProductServices.change_product_is_available_status(product.id)

        },
        category_form_submit() {
            category_form["on_submit"] = true
            this.category_form["filtration"] = []

            for (var i = 0; i < this.category_form["filtration"].length; i++) {
                this.category_form["filtration"][i]["values"] = this.category_form["filtration"][i]["values"].trim().split(";")

                if (this.category_form["filtration"][i]["values"][this.category_form["filtration"][i]["values"].length - 1] == "") {
                    this.category_form["filtration"][i]["values"].splice(this.category_form["filtration"][i]["values"].length - 1, 1)
                }

                for (var j = 0; j < this.category_form["filtration"][i]["values"].length; j++) {
                    this.category_form["filtration"][i]["values"][j] = {value: this.category_form["filtration"][i]["values"][j].trim()}
                }
            }

            this.category_form["filtration"] = JSON.stringify(this.category_form["filtration"])

            if (this.category_form["category_id"] == 0) {
                CategoryServices.add_category(this.category_form).then((response) => {
                    CategoryServices.get_categories().then((data) => {
                        this.categories = data
                    })
                })
            } else {
                CategoryServices.edit_category(this.category_form).then((response) => {
                    CategoryServices.get_categories().then((data) => {
                        this.categories = data
                    })
                })
            }

            window.location.hash = ""
            this.category_form = {
                category_id: 0,
                name: "",
                poster: "",
                is_available: false,
                filtration: [{name: "", values: []}],
                on_submit: false,
            }
        },
        product_form_submit() {
            if (this.product_form["category_id"] != this.main_category_id) {
                this.product_form["currency"] = "ru"
            }

            for (var i = 0; i < this.product_form["options"].length; i++) {
                if (this.get_option_values(this.product_form["options"][i]).length > 0 && this.product_form["options"][i]["values"].length == 0) {
                    alert("Выберите значения для характеристики " + this.product_form["options"][i]["name"])
                    return
                }
            }

            for (var i = 0; i < this.product_form["options"].length; i++) {
                if (this.product_form["options"][i]["values"].length == 0 && this.product_form["options"][i]["values_text"] != "") {
                    this.product_form["options"][i]["values"] = [{value: this.product_form["options"][i]["values_text"]}]
                }

                delete this.product_form["options"][i]["values_text"]
            }

            this.product_form["on_submit"] = true
            this.product_form["description"] = this.product_form_description_editor.root.innerHTML
            if (this.product_form["product_id"] == 0) {
                ProductServices.add_product(this.product_form).then((result) => {
                    if (result["success"]) {
                        document.getElementById("product_form_window").style.display = "none"
                        ProductServices.get_products({
                            products_filtration: JSON.stringify({
                                id: result["product_id"],
                            }),
                            last_obj_id: result["product_id"] + 1,
                        }).then((response) => {
                            this.products.unshift(response["data"][0])
                            this.products.splice(this.products.length - 1, 1)

                            this.product_form = {
                                product_id: 0,
                                category_id: 0,
                                name: "",
                                description: "",
                                price: 0,
                                count: 0,
                                is_available: false,
                                code: "",
                                vendor_number: "",
                                currency: "ru",
                                images: [{image: "", "default": true}, {image: "", "default": false}, {image: "", "default": false}, {image: "", "default": false}],
                                options: [],
                                on_submit: false,
                                category_filtration: []
                            }
                        })
                    }
                })
            } else {
                ProductServices.edit_product(this.product_form).then((result) => {
                    if (result["success"]) {
                        document.getElementById("product_form_window").style.display = "none"
                        ProductServices.get_products({
                            products_filtration: JSON.stringify({
                                id: this.product_form["product_id"],
                            }),
                            last_obj_id: this.product_form["product_id"] + 1,
                        }).then((response) => {
                            this.products.splice(this.products.length - 1, 1)
                            for (var i = 0; i < this.products.length; i++) {
                                if (this.products[i]["id"] == this.product_form["product_id"]) {
                                    this.products[i] = response["data"][0]
                                    break
                                }
                            }

                            this.product_form = {
                                product_id: 0,
                                category_id: 0,
                                name: "",
                                description: "",
                                price: 0,
                                count: 0,
                                is_available: false,
                                code: "",
                                vendor_number: "",
                                currency: "ru",
                                images: [{image: "", "default": true}, {image: "", "default": false}, {image: "", "default": false}, {image: "", "default": false}],
                                options: [],
                                on_submit: false,
                                category_filtration: []
                            }
                        })
                    }
                })
            }
        },
        delete_filtration(filtration) {
            this.category_form["filtration"].splice(this.category_form["filtration"].indexOf(filtration), 1)

        },
        add_filtration() {
            this.category_form["filtration"].push({name: "", values: ""})

        },
        delete_category() {
            swal({
              title: "Подтвердите ваше действия. Вы хотите удалить категорию?",
              icon: "warning",
              buttons: true,
              dangerMode: true,
            }).then((will) => {
                if (will) {
                    if (this.current_category) {
                        if (this.category_form["category_id"] == this.current_category.id) {
                            this.current_category = null
                            this.products = []
                        }
                    }
                    CategoryServices.delete_category(this.category_form["category_id"]).then((response) => {
                        CategoryServices.get_categories().then((data) => {
                            this.categories = data
                        })
                    })
                    window.location.hash = ""
                    this.category_form = {
                        category_id: 0,
                        name: "",
                        poster: "",
                        is_available: false,
                        filtration: [{name: "", values: []}],
                        on_submit: false,
                    }
                }
            })
        },
        set_category_filtration() {
            for (var i = 0; i < this.categories.length; i++) {
                if (this.categories[i]["id"] == this.product_form["category_id"]) {
                    this.product_form["category_filtration"] = this.categories[i]["filtration"]
                    break
                }
            }
        },
        handle_file_upload(image, event) {
            var file = event.target.files[0]
            if (file) {
                image["image"] = file.name
                this.product_form["image: " + file.name] = file
            }
        },
        handle_category_poster_upload(event) {
            var file = event.target.files[0]
            if (file) {
                this.category_form["poster"] = file.name
                this.category_form["poster: " + file.name] = file
            }
        },
        delete_option(option) {
            this.product_form["options"].splice(this.product_form["options"].indexOf(option), 1)

        },
        get_option_values(option) {
            var option_values = []

            for (var i = 0; i < this.product_form["category_filtration"].length; i++) {
                if (this.product_form["category_filtration"][i]["name"] == option.name) {
                    option_values = this.product_form["category_filtration"][i]["values"]
                    break
                }
            }

            return option_values
        },
        set_option_value(option, filtration_value) {
            var found = false

            for (var i = 0; i < option["values"].length; i++) {
                if (option["values"][i]["value"] == filtration_value.value) {
                    option["values"].splice(i, 1)
                    found = true
                    break
                }
            }

            if (!found) {
                option["values"].push({value: filtration_value.value})
            }

            option["values_text"] = ""
        },
        set_option_values_text(option, event) {
            option["values_text"] = event.target.value
            option["values"] = []
        },
        product_option_includes_value(option, filtration_value) {
            for (var i = 0; i < option["values"].length; i++) {
                if (option["values"][i]["value"] == filtration_value.value) {
                    return true
                }
            }
            return false
        },
        add_product_option() {
            this.product_form["options"].push({name: "", values: [], values_text: ""})

        },
        delete_product() {
            swal({
              title: "Подтвердите ваше действия. Вы хотите удалить товар?",
              icon: "warning",
              buttons: true,
              dangerMode: true,
            }).then((will) => {
                if (will) {
                    ProductServices.delete_product(this.product_form["product_id"]).then((response) => {
                        document.getElementById("product_form_window").style.display = "none"
                        for (var i = 0; i < this.products.length; i++) {
                            if (this.products[i]["id"] == this.product_form["product_id"]) {
                                this.products.splice(i, 1)
                                break
                            }
                        }
                        this.product_form = {
                            product_id: 0,
                            category_id: 0,
                            name: "",
                            description: "",
                            price: 0,
                            count: 0,
                            is_available: false,
                            code: "",
                            vendor_number: "",
                            currency: "ru",
                            images: [{image: "", "default": true}, {image: "", "default": false}, {image: "", "default": false}, {image: "", "default": false}],
                            options: [],
                            on_submit: false,
                            category_filtration: []
                        }
                    })
                }
            })
        },
        image_is_uploaded_to_input(image) {
            return !(image.image.startsWith("/media/"))

        },
        category_poster_is_uploaded_to_input() {
            return !(this.category_form["poster"].startsWith("/media/"))

        },
        window_scroll_down_event_listener() {
            if (!this.is_getting_products && !this.there_is_no_more_products) {
                this.is_getting_products = true
                var get_products_request_schema = {}

                if (this.current_section != "all_products") {
                    get_products_request_schema["products_filtration"] = JSON.stringify({category_id: this.current_category.id})
                }

                ProductServices.get_products(get_products_request_schema).then((response) => {
                    this.is_getting_products = false
                    if (response["data"].length == 0) {
                        this.there_is_no_more_products = true
                    } else {
                        this.there_is_no_more_products = false
                    }
                })
            }
        },
        drag_start(event) {
            var category_item = event.target.parentNode
            var target = event.target
            if (category_item.tagName == "LABEL") {
                category_item = category_item.parentNode.parentNode
                target = target.parentNode.parentNode
            }
            var dragged = target;
            this.drag_and_drop["list"] = category_item.children;
            for(var i = 0; i < this.drag_and_drop["list"].length; i += 1) {
                if(this.drag_and_drop["list"][i] === dragged){
                    this.drag_and_drop["index"] = i;
                }
            }
        },
        drag_over(event) {
            event.preventDefault();

        },
        drop(event) {
            event.preventDefault()
            var category_item = event.target.parentNode
            if (category_item.tagName == "LABEL") {
                category_item = category_item.parentNode
            }
            if(category_item.className.includes("dropzone")) {
                var indexDrop = 0

                for(var i = 0; i < this.drag_and_drop["list"].length; i += 1) {
                    if(this.drag_and_drop["list"][i] === category_item){
                        indexDrop = i;
                    }
                }

                var category = this.categories[this.drag_and_drop["index"]]
                this.categories.splice(this.drag_and_drop["index"], 1)
                this.categories.splice(indexDrop, 0, category)
                var categories_order = []

                for (var i = 0 ; i < this.categories.length; i++) {
                    categories_order.push({id: this.categories[i]["id"], index: i})
                    if (this.current_category["id"] == this.categories[i]["id"]) {
                        document.getElementsByClassName("category_select_radio")[i].checked = true
                    }
                }

                CategoryServices.save_categories_order(categories_order)
            }
        },
        search_products() {
            this.is_getting_products = true

            axios("/api/product/search_products/", {
                params: {
                    search_input: this.search_products_input,
                }
            }).then((response) => {
                this.admin_searched_products = true
                this.products = []

                for (var i = 0; i < response["data"].length; i++) {
                    this.products.push(response["data"][i])
                }
            })
        },
        cancel_searching() {
            this.admin_searched_products = false
            this.is_getting_products = false
            this.last_obj_id = 0
            this.there_is_no_more_products = false
            this.products = []
            this.search_products_input = ""
            this.open_section()
        },
        get_product_price_with_currency(product) {
            if (product.currency == "kz") {
                var currency = "Тг"
            } else {
                var currency = "₽"
            }
            return product.price + " " + currency
        },
        open_order_form(product) {
            var currentDate = new Date();

            var year = currentDate.getFullYear();
            var month = String(currentDate.getMonth() + 1).padStart(2, '0'); // Months are zero-indexed, so add 1
            var day = String(currentDate.getDate()).padStart(2, '0');

            var formattedDate = `${year}-${month}-${day}`;

            this.order_form = {
                product: product,
                date: formattedDate,
                count: 1,
                company_name: ""
            }

            document.getElementById("order_form_window").style.display = "block"
        },
        order_form_submit() {
            this.order_form["product"] = JSON.stringify(this.order_form["product"])
            axios.post("/api/staff/add_order/", this.order_form, {
                headers: {
                    "X-CSRFToken": $cookies.get("csrftoken")
                }
            }).finally(() => {
                alert("Заказ добавлен в Google Sheet")
                document.getElementById("order_form_window").style.display = "none"
            })
        }
    },
    mounted() {
        this.main_category_id = main_category_id
    }
})


products_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_products_app = products_app.mount("#products")
