function clear_favourites() {
    UserServices.clear_favourites()
    mounted_products_app.products = []
}

if (user_is_authenticated) {
    ProductServices.get_products({products_filtration: JSON.stringify({favourites__user__username: username})})
} else {
    favourite_products = UserServices.get_local_favourite_products()
    ProductServices.get_products({products_filtration: JSON.stringify({id__in: favourite_products})})
}

setInterval(function() {
    if (document.getElementsByClassName("product_card").length == 0) {
        document.getElementById("clear_favourites_btn").style.display = "none"
        document.getElementById("favourites_are_empty_text").style.display = "block"
    } else {
        document.getElementById("clear_favourites_btn").style.display = "block"
        document.getElementById("favourites_are_empty_text").style.display = "none"
    }
}, 1000)
