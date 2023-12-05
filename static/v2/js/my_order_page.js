function open_replaced_by_product_image(event, url) {
    event.preventDefault()
    document.getElementById("replaced_by_product_image_window").style.display = "block"
    document.getElementById("replaced_by_product_image").src = url
}

function close_replaced_by_product_image() {
    document.getElementById("replaced_by_product_image_window").style.display = "none"
}
