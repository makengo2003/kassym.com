let total_products_count = parseInt(document.getElementById("total_count_of_products").value)
let pageSize = 30
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
                var url = new URL(window.location.href);
                var queryParams = url.searchParams;
                queryParams.set("page", pagination.pageNumber);
                history.pushState({}, "", url.href);

                axios("/api/product/get_many/", {
                    params: {
                        "offset": parseInt(pagination.pageNumber * pageSize - pageSize),
                        "limit": parseInt(pageSize),
                        "search_input": search_input,
                    }
                }).then((response) => {
                    var newElement = document.createElement('div')
                    newElement.innerHTML = response.data["html"]

                    var products_list = document.getElementsByClassName("products_list")[0]
                    products_list.innerHTML = newElement.getElementsByClassName("products_list")[0].innerHTML
                })
            }
        }
    })
}

url_params = new URLSearchParams(window.location.search)
let search_input = url_params.get("search_input")
let page = url_params.get("page")
document.getElementsByClassName("search")[0].getElementsByTagName("input")[0].value = search_input

create_pagination()
pagination_el.pagination(page || 1)