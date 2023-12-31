cart_app = Vue.createApp({
    data() {
        return {
            cart: [],
            express_checkbox: false,
            comments: "",
            payment_info: {},
            current_page: "cart",
            uploaded_files: [],
            deliveries_qr_code: {
                file: null
            },
            selection_sheet: {
                file: null
            },
            paid_check_pdf: {
                file: null
            },
            is_calculating_price: false,
            is_confirming_cart: false,
            cart_is_confirmed: false,
            is_making_order: false,
            order_making_is_available: false,
            time_is_until_18px: false,
            open_tutorial: false,
            additional_selection_lists: []
        }
    },
    methods: {
        clear_cart() {
            Swal.fire({
                title: "Очистить корзину?",
                icon: "question",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Да",
                cancelButtonText: "Нет"
            }).then((result) => {
                if (result.isConfirmed) {
                    axios.post("/api/cart/clear/", {}, {headers: {"X-CSRFToken": $cookies.get("csrftoken")}})
                    this.cart = []
                }
            });
        },
        minus_count(cart_item) {
            cart_item.count -= 1

            if (cart_item.count < 1) {
                cart_item.count = 1
            }

            axios.post("/api/cart/update_fields/", {"id": cart_item.id, "count": cart_item.count}, {headers: {"X-CSRFToken": $cookies.get("csrftoken")}})
        },
        plus_count(cart_item) {
            cart_item.count += 1
            axios.post("/api/cart/update_fields/", {"id": cart_item.id, "count": cart_item.count}, {headers: {"X-CSRFToken": $cookies.get("csrftoken")}})
        },
        get_sum(cart_item) {
            return cart_item.product_price * cart_item.count

        },
        remove_cart_item(cart_item) {
            axios.post("/api/cart/delete/", {id: cart_item.id}, {headers: {"X-CSRFToken": $cookies.get("csrftoken")}})
            this.cancel_file_upload(cart_item, "qr_code")
            this.cart.splice(this.cart.indexOf(cart_item), 1)
        },
        handle_file_upload(extensions, event, obj, label, obj_name, obj_id_label=null) {
            var file = event.target.files[0]

            if (file) {
                var label_for_uploaded_files_list = obj_name + "_" + label

                if (obj_id_label != null)
                    label_for_uploaded_files_list += "_" + obj_id_label

                label_for_uploaded_files_list += ": " + file.name


                obj[label] = label_for_uploaded_files_list
                this.uploaded_files[label_for_uploaded_files_list] = file

                for (var i = 0; i < extensions.length; i++) {
                    if (!file.name.toLowerCase().endsWith(extensions[i].toLowerCase())) {
                        Swal.fire('Неподдерживаемый тип файла ' + '".' + file.name.split(".").slice(-1) + '"', "", "warning")
                        this.cancel_file_upload(obj, label)
                    }
                }
            }
        },
        file_is_uploaded(obj, label) {
            return obj[label] != null

        },
        cancel_file_upload(obj, label) {
            if (this.file_is_uploaded(obj, label)) {
                delete this.uploaded_files[obj[label]]
                document.getElementById(obj[label].split(":")[0]).value = null
                delete obj[label]
            }
        },
        cart_is_empty() {
            return this.cart.length == 0

        },
        get_cart_items_count() {
            return this.cart.length

        },
        go_to_cart() {
            this.cancel_file_upload(this.paid_check_pdf, "file")
            this.current_page = "cart"
            this.cart_is_confirmed = false
            this.is_confirming_cart = false
        },
        go_to_payment() {
            var astana_current_time = moment.tz("Asia/Almaty").hour()
            var astana_current_time_minutes = moment.tz("Asia/Almaty").minutes()
            this.order_making_is_available = astana_current_time < 24 && astana_current_time > -1
            this.time_is_until_18px = astana_current_time < -1 && astana_current_time > 25

            if (this.order_making_is_available) {
                for (var i = 0; i < this.cart.length; i++) {
                    if (this.cart[i]["qr_code"] == null) {
                        Swal.fire("Все QR-коды товаров должны быть загружены.", "", "warning")
                        return
                    }
                }

                if (this.deliveries_qr_code["file"] == null) {
                    Swal.fire("Вы забыли загрузить QR поставки.", "", "warning")
                    return
                }

                if (this.selection_sheet["file"] == null) {
                    Swal.fire("Необходимо загрузить лист подбора.", "", "warning")
                    return
                }

                for (var i = 0; i < this.additional_selection_lists.length; i++) {
                    if (this.additional_selection_lists[i]["file"] == null) {
                        Swal.fire("Необходимо загрузить лист подбора.", "", "warning")
                        return
                    }
                }

                if (this.is_confirming_cart) {
                    this.is_confirming_cart = false
                    this.cart_is_confirmed = true
                } else {
                    this.cart_is_confirmed = false
                    this.is_confirming_cart = true

                    Swal.fire("Пожалуйста", 'Прежде чем оплатить, еще раз проверьте корзину и загруженные файлы', "warning")
                }

                if (this.express_checkbox && this.time_is_until_18px) {
                    this.express_checkbox = true
                } else {
                    this.express_checkbox = false
                }

                if (this.cart_is_confirmed) {
                    this.is_calculating_price = true
                    var data = {
                        is_express: this.express_checkbox,
                        check_defects: {},
                        with_gift: {},
                    }

                    for (var i = 0; i < this.cart.length; i++) {
                        data["check_defects"][this.cart[i]["id"]] = this.cart[i]["check_defects"]
                        data["with_gift"][this.cart[i]["id"]] = this.cart[i]["with_gift"]
                    }

                    data["check_defects"] = JSON.stringify(data["check_defects"])
                    data["with_gift"] = JSON.stringify(data["with_gift"])

                    axios("/api/order/calculate/", {params: data}).then((response) => {
                        this.payment_info = response.data
                        this.current_page = "payment"
                        window.scrollTo({top: 0, behavior: "smooth"});

                        if (response.data["is_same_with_last_order"]) {
                            Swal.fire({
                                title: "Внимание",
                                text: "Текущая корзина абсолютно идентична вашему последнему заказу.\nПродолжить заказ?",
                                icon: "warning",
                                showCancelButton: true,
                                confirmButtonColor: "#3085d6",
                                cancelButtonColor: "#d33",
                                confirmButtonText: "Продолжить",
                                cancelButtonText: "Отменить"
                            }).then((result) => {
                                if (!result.isConfirmed) {
                                    this.go_to_cart()
                                }
                            })
                        }
                    }).catch((err) => {
                        this.is_confirming_cart = true
                        Swal.fire("Ошибка", "Свяжитесь с менеджерами", "error")
                    }).finally(() => {
                        this.is_calculating_price = false
                    })
                }
            }
        },
        make_order() {
            if (!this.is_making_order) {
                if (this.paid_check_pdf["file"] == null) {
                    Swal.fire("Вы забыли загрузить чек с kaspi.kz.", "", "warning")
                    return
                }

                this.is_making_order = true

                var astana_current_time = moment.tz("Asia/Almaty").hour()
                if (this.express_checkbox && astana_current_time < -1 && astana_current_time > 25) {
                    this.express_checkbox = true
                } else {
                    this.express_checkbox = false
                }

                var data = {
                    is_express: this.express_checkbox,
                    comments: {},
                    check_defects: {},
                    with_gift: {},
                    order_comments: this.comments,
                    deliveries_qr_code: this.uploaded_files[this.deliveries_qr_code["file"]],
                    selection_sheet_file: this.uploaded_files[this.selection_sheet["file"]],
                    paid_check_file: this.uploaded_files[this.paid_check_pdf["file"]],
                }

                for (var i = 0; i < this.cart.length; i++) {
                    var qr_code = this.cart[i]["qr_code"].slice(0, this.cart[i]["qr_code"].indexOf(":"))
                    data[qr_code] = this.uploaded_files[this.cart[i]["qr_code"]]
                    data["comments"][this.cart[i]["id"]] = this.cart[i]["comments"]
                    data["check_defects"][this.cart[i]["id"]] = this.cart[i]["check_defects"]
                    data["with_gift"][this.cart[i]["id"]] = this.cart[i]["with_gift"]
                }

                data["comments"] = JSON.stringify(data["comments"])
                data["check_defects"] = JSON.stringify(data["check_defects"])
                data["with_gift"] = JSON.stringify(data["with_gift"])

                for (var i = 0; i < this.additional_selection_lists.length; i++) {
                    data[this.additional_selection_lists[i]["file"]] = this.uploaded_files[this.additional_selection_lists[i]["file"]]
                }

                axios.post("/api/order/add/", data, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        "X-CSRFToken": $cookies.get("csrftoken")
                    }
                }).then((response) => {
                    Swal.fire({
                      title: "Заказ принят",
                      icon: "success",
                    }).then((result) => {
                      window.location.href = '/my_orders/';
                    });
                }).catch((err) => {
                    Swal.fire("Произошла какая-та ошибка!", "Свяжитесь с менеджерами", "error")
                }).finally(() => {
                    this.is_making_order = false
                })
            }
        },
        get_uploaded_file_name(file_name) {
            return file_name.slice(file_name.indexOf(":") + 1, file_name.length)
        },
        close_tutorial() {
            document.getElementById("make_order_tutorial_video").pause();
            this.open_tutorial = false
        },

        add_selection_list() {
            this.additional_selection_lists.push({id: generateUUID(), file: null})
        },
        remove_selection_list(selection_list) {
            this.cancel_file_upload(selection_list, "file")
            this.additional_selection_lists.splice(this.additional_selection_lists.indexOf(selection_list), 1)
        },

        open_uploaded_pdf(obj, label) {
            var fileReader = new FileReader();

            fileReader.onload = function(e) {
                var arrayBuffer = e.target.result;
                renderPdf(arrayBuffer);
            };

            fileReader.readAsArrayBuffer(this.uploaded_files[obj[label]]);
            document.getElementById("pdfViewer").style.display = 'block'
            document.body.style.overflow = 'hidden';
        }
    },
    mounted() {
        axios("/api/cart/get_many/").then(response => this.cart = response.data)
        var astana_current_time = moment.tz("Asia/Almaty").hour()
        var astana_current_time_minutes = moment.tz("Asia/Almaty").minutes()
        this.order_making_is_available = astana_current_time < 24 && astana_current_time > -1
        this.time_is_until_18px = astana_current_time < -1 && astana_current_time > 25
    }
})


cart_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_cart_app = cart_app.mount("#cart_page")




function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (Math.random() * 16) | 0,
        v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}




document.addEventListener("DOMContentLoaded", function() {
    var footer = document.querySelector(".footer-container");
    var button = document.querySelector(".tech_support_btn");
    var buttonHeight = button.getBoundingClientRect().top + 200;

    window.addEventListener("scroll", function() {
        var footerTop = footer.getBoundingClientRect().top;

        if (footerTop < buttonHeight) {
            button.style.bottom = (button.offsetHeight * 2) + (buttonHeight - footerTop) + "px";
        } else {
            button.style.bottom = "10%";
        }
    });
});

function close_pdf_viewer() {
    document.getElementById('pdfViewer').style.display = 'none'
    document.body.style.overflow = 'auto';
    destroyPdfViewer()
}

var pdfPages = [];
function destroyPdfViewer() {
    pdfPages.forEach(function(canvas) {
        pdfViewer.removeChild(canvas);
    });

    pdfPages = [];
}

var md = new MobileDetect(window.navigator.userAgent);
var device_is_mobile = md.mobile()
var device_is_tablet = md.tablet()

function renderPdf(arrayBuffer) {
    pdfjsLib.getDocument(arrayBuffer, {viewer: { touch: true }}).promise.then(function(pdf) {
        var pdfViewer = document.getElementById('pdfViewer');

        for (var pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
            pdf.getPage(pageNumber).then(function(page) {
                var canvas = document.createElement('canvas');
                var context = canvas.getContext('2d');
                var viewport = page.getViewport({ scale: device_is_mobile ? 1.5 : (device_is_tablet ? 1.75 : 2) });

                canvas.height = viewport.height;
                canvas.width = viewport.width;

                var renderContext = {
                    canvasContext: context,
                    viewport: viewport
                };

                page.render(renderContext).promise.then(function() {
                    pdfPages.push(canvas);
                    pdfViewer.appendChild(canvas);
                });
            });
        }
    });
}
