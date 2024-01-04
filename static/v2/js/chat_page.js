chat_app = Vue.createApp({
    data() {
        return {
            uploaded_files: [],
            textarea: "",
            is_sending_message: false,
            is_getting_messages: false,
        }
    },
    methods: {
        delete_file(index) {
            this.uploaded_files.splice(index, 1)
        },

        add_file() {
            document.getElementById("file_upload_input").click()
        },

        send_message() {
            if (!(this.textarea) && this.uploaded_files.length == 0) {
                Swal.fire("Пустое сообщение", "Чтобы отправить сообщение, добавьте текст или прикрепите файл.", "warning")
                return
            }

            if (!(this.is_sending_message)) {
                this.is_sending_message = true

                var data = {
                    text: this.textarea,
                }

                for (var i = 0; i < this.uploaded_files.length; i++) {
                    data["file_" + (i + 1)] = this.uploaded_files[i]
                }

                axios.post("/api/message/add_message/", data, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        "X-CSRFToken": $cookies.get("csrftoken"),
                    }
                }).then((response) => {
                    this.get_messages()
                    this.is_sending_message = false
                    this.uploaded_files = []
                    this.textarea = ""
                }).catch((error) => {
                    Swal.fire("Ошибка", "Не удалось отправить сообщение", "error")
                })
            }
        },

        get_messages() {
            if (!(this.is_getting_messages)) {
                this.is_getting_messages = true

                var last_message = document.querySelector('#messages .message:last-child');

                if (last_message) {
                    var last_message_id = last_message.getAttribute("data-id")
                    axios("/messages/tech_support/?id__gt=" + last_message_id, {
                        headers: {
                            "X-Requested-With": "XMLHttpRequest"
                        }
                    }).then((response) => {
                        this.is_getting_messages = false

                        var prev_messages_count = document.getElementById("messages").getElementsByClassName("message").length
                        document.getElementById("messages").innerHTML += response.data
                        var new_messages_count = document.getElementById("messages").getElementsByClassName("message").length

                        if (new_messages_count != prev_messages_count) {
                            var scrollableDiv = document.getElementById('messages');
                            scrollableDiv.scrollTop = scrollableDiv.scrollHeight + 200;
                        }
                    })
                }
            }
        },

        handle_file_upload(event) {
            var file = event.target.files[0]

            if (file) {
                this.uploaded_files.push(file)
            }

            event.target.value = null
        }
    },
    mounted() {
        setInterval(this.get_messages, 10000);
    }
})


chat_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_chat_app = chat_app.mount("#chat")
