function add_wishlist(event) {
    event.preventDefault()

    if (user_is_authenticated) {
        if (event.target.getAttribute("data-value") == "true") {
            event.target.setAttribute("data-value", "false")
            event.target.src = "/static/v2/imgs/empty_heart.png"

            axios.post("/api/user/remove_product_from_favourites/", {product_id: Number(event.target.getAttribute("data-id"))}, {
                headers: {
                    "X-CSRFToken": $cookies.get("csrftoken"),
                }
            }).then((response) => {
                return
            }).catch((error) => {
                console.log(error)
            })
        } else {
            event.target.setAttribute("data-value", "true")
            event.target.src = "/static/v2/imgs/heart.png"

            axios.post("/api/user/add_products_to_favourites/", {products_ids: [Number(event.target.getAttribute("data-id"))]}, {
                headers: {
                    "X-CSRFToken": $cookies.get("csrftoken"),
                }
            }).then((response) => {
                return
            }).catch((error) => {
                console.log(error)
            })
        }
    }
}