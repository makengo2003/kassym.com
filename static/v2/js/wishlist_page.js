function clear_wishlist(event) {
    event.target.style.display = "none"
    there_is_no_favourite_product_text.style.display = "block"
    document.getElementsByClassName("products_list")[0].style.display = "none"

    axios.post("/api/user/clear_favourites/", {}, {
        headers: {
            "X-CSRFToken": $cookies.get("csrftoken"),
        }
    })
}