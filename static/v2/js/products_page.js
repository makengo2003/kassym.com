var ordering_select = null
var category_select = null
var min_price_input = null
var max_price_input = null

function set_values_of_get_many_request_params() {
    ordering_select = document.getElementById("ordering_select")
    category_select = document.getElementById("category_select")
    min_price_input = document.getElementById("min_price_input")
    max_price_input = document.getElementById("max_price_input")
}

var filter_details = document.getElementsByClassName("filter_details")[0];
filter_details.getElementsByTagName("summary")[0].addEventListener("click", function(event) {
    event.preventDefault()

    if (filter_details.hasAttribute("data-open")) {
        filter_details.removeAttribute("data-open")
        filter_details.classList.remove('open_details');
    } else {
        filter_details.setAttribute("data-open", "true")
        filter_details.classList.add('open_details');
    }
});

set_values_of_get_many_request_params()
var price_range_minimum_difference = max_price_input.value * 0.1

let total_products_count = parseInt(document.getElementById("total_count_of_products").value)
let pageSize = 24
let pageNumber = Math.ceil(total_products_count / pageSize)
let pagination_el = $('#pagination')

function create_pagination() {
    let first_pagination_usage = true

    pagination_el.pagination({
        dataSource: Array.from({ length: pageNumber }),
        pageSize: 1,
        callback: function(data, pagination) {
            if (first_pagination_usage) {
                first_pagination_usage = false
            } else {
                set_values_of_get_many_request_params()

                var get_products_query_params = {
                    "category_id": parseInt(category_select.options[category_select.selectedIndex].value),
                    "ordering": [ordering_select.options[ordering_select.selectedIndex].value],
                    "min_price": parseInt(min_price_input.value),
                    "max_price": parseInt(max_price_input.value),
                    "page": pagination.pageNumber
                }

                var url = new URL(window.location.href);
                var queryParams = url.searchParams;

                for (var key in get_products_query_params) {
                    queryParams.set(key, get_products_query_params[key]);
                }

                history.pushState({}, "", url.href);

                var filtration = {
                    "category_id": get_products_query_params["category_id"],
                    "price__lte": get_products_query_params["max_price"],
                    "price__gte": get_products_query_params["min_price"],
                }

                axios("/api/product/get_many/", {
                    params: {
                        "filtration": JSON.stringify(filtration),
                        "ordering": JSON.stringify(get_products_query_params["ordering"]),
                        "offset": parseInt(get_products_query_params["page"] * pageSize - pageSize),
                        "limit": parseInt(pageSize)
                    }
                }).then((response) => {
                    console.log("response")
                    if (response.data["count"] != total_products_count) {
                        total_products_count = response.data["count"]
                        pageNumber = Math.ceil(total_products_count / pageSize)

                        pagination_el.pagination("destroy")
                        create_pagination()
                        pagination_el.pagination(get_products_query_params["page"])
                    }

                    var newElement = document.createElement('div')
                    newElement.innerHTML = response.data["html"]

                    var products_list = document.getElementsByClassName("products_list")[0]
                    products_list.innerHTML = newElement.getElementsByClassName("products_list")[0].innerHTML
                })
            }
        }
    })
}

create_pagination()
pagination_el.pagination((new URLSearchParams(window.location.search).get("page")) || 1)

function slide_min_price() {
    set_values_of_get_many_request_params()

    if(parseInt(max_price_input.value) - parseInt(min_price_input.value) <= price_range_minimum_difference){
        min_price_input.value = parseInt(max_price_input.value) - price_range_minimum_difference;
    }

    min_price_input.value = Number(min_price_input.value)
    document.getElementById("min_price_text").innerText = min_price_input.value + " Р"
}

function slide_max_price() {
    set_values_of_get_many_request_params()

    if(parseInt(max_price_input.value) - parseInt(min_price_input.value) <= price_range_minimum_difference){
        max_price_input.value = parseInt(min_price_input.value) + price_range_minimum_difference;
    }

    max_price_input.value = Number(max_price_input.value)
    document.getElementById("max_price_text").innerText = max_price_input.value + " Р"
}

function open_category() {
    set_values_of_get_many_request_params()
    window.location.href = "/products/?category_id=" + category_select.value
}
