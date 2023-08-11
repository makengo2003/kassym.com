function phone_number_on_input(event) {
    if (!event.target.value.startsWith("+7")) {
        event.target.value = "+7" + event.target.value
        if (event.target.value.endsWith("+")) {
            event.target.value = event.target.value.slice(0, event.target.value.length-1)
        }
    }
}

