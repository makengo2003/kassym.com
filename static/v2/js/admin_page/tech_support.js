tech_support_app = Vue.createApp({
    data() {
        return {
            search_input: "",
            searched: false,
            chats: [],
            selected_user_id: null,

            uploaded_files: [],
            textarea: "",
            is_sending_message: false,
            is_getting_messages: false,
        }
    },
    methods: {
        open_section() {
            this.get_chats()
            setInterval(this.get_chats, 10000);
        },
        close_section() {},

        get_chats() {
            var filtration = {}

            if (this.search_input) {
                filtration["search_input"] = this.search_input

                this.searched = true
            } else {
                this.searched = false
            }

            axios("/api/message/get_chats/", {params: filtration}).then((response) => {
                this.chats = response.data
            })
        },
        select_chat(chat) {
            this.selected_user_id = chat.user_id
            document.getElementById("messages").innerHTML = ""
            this.is_sending_message = false
            this.uploaded_files = []
            this.textarea = ""

            this.get_messages()
            setInterval(this.get_messages, 10000);
        },

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
                    user_id: this.selected_user_id
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
                } else {
                    var last_message_id = 0
                }

                axios("/messages/tech_support/", {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    params: {
                        id__gt: last_message_id,
                        user_id: this.selected_user_id
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
        },

        handle_file_upload(event) {
            var file = event.target.files[0]

            if (file) {
                this.uploaded_files.push(file)
            }

            event.target.value = null
        }
    },
})


tech_support_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_tech_support_app = tech_support_app.mount("#tech_support_section")
