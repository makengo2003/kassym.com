var base_course_form_data = {
    id: 0,
    language: "",
    is_available: false,
    poster: "",
    name: "",
    lessons: [],
    on_submit: false,
    errors: []
}


courses_app = Vue.createApp({
    data() {
        return {
            courses: [],
            course_form: {}
        }
    },
    methods: {
        open() {
            if (this.courses.length == 0) {
                this.get_courses()
            }
        },
        close() {},
        get_courses() {
            axios.get("/api/course/get_courses/").then((response) => {
                this.courses = response.data
            })
        },
        open_course_form(course=null) {
            if (this.course_form["poster"] != "") {
                delete this.course_form[this.course_form["poster"]]
            }

            for (var i = 0; i < this.course_form["lessons"].length; i++) {
                if (this.course_form["lessons"][i]["video"] != "") {
                    delete this.course_form[this.course_form["lessons"][i]["video"]]
                }
            }

            var product_form_image_inputs = document.getElementsByClassName("product_form_image_input")

            for (var i = 0; i < product_form_image_inputs.length; i++) {
                product_form_image_inputs[i].value = null
            }

            if (course) {
                axios.get("/api/course/get_course/", {params: {course_id: course.id}}).then((response) => {
                    this.course_form = Object.assign({}, response["data"])
                })
            } else {
                if (this.course_form["id"]) {
                    this.course_form = Object.assign({}, base_course_form_data)
                    this.course_form["lessons"] = []
                }
            }

            document.getElementById("course_form_window").style.display = "block"
        },
        course_form_submit() {
            if (!this.course_form["on_submit"]) {
                this.course_form["on_submit"] = true

                if (this.course_form["id"]) {
                    var submit_url = "/api/course/edit_course/"
                } else {
                    var submit_url = "/api/course/add_course/"
                }

                var submit_data = Object.assign({}, this.course_form)
                submit_data["lessons"] = JSON.stringify(this.course_form["lessons"])

                axios.post(submit_url, submit_data, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        "X-CSRFToken": $cookies.get("csrftoken"),
                    }
                }).then((response) => {
                    this.get_courses()
                    document.getElementById("course_form_window").style.display = "none"
                    this.course_form = Object.assign({}, base_course_form_data)
                    this.course_form["lessons"] = []
                }).catch((error) => {
                    if (error.response) {
                        if (error.response.status == 400) {
                            this.course_form.errors = []
                            for (var key in error.response.data) {
                                for (var err in error.response.data[key]) {
                                    this.course_form.errors.push(error.response.data[key][err])
                                }
                            }
                        } else {
                            swal("Упс", "Что-то пошло не так!")
                        }
                    }
                }).finally(() => {
                    this.course_form["on_submit"] = false
                })
            }
        },
        delete_course() {
            swal({
              title: "Подтвердите ваше действия. Вы хотите удалить курс?",
              icon: "warning",
              buttons: true,
              dangerMode: true,
            }).then((will) => {
                if (will) {
                    axios.post("/api/course/delete_course/", {course_id: this.course_form.id}, {
                        headers: {
                            "X-CSRFToken": $cookies.get("csrftoken"),
                        }
                    }).then((response) => {
                        this.get_courses()
                        document.getElementById("course_form_window").style.display = "none"
                    })
                }
            })
        },
        course_poster_is_uploaded_to_input() {
            return !(this.course_form.poster.startsWith("/media/"))

        },
        lesson_video_is_uploaded_to_input(lesson) {
            return !(lesson.video.startsWith("/media/"))

        },
        handle_lesson_video_upload(lesson, event) {
            var file = event.target.files[0]
            if (file) {
                delete this.course_form[lesson["video"]]
                lesson["video"] = (this.course_form.lessons.indexOf(lesson) + 1) + ". " + file.name
                this.course_form[lesson["video"]] = file
            } else {
                if (lesson["video"]) {
                    delete this.course_form[lesson["video"]]
                    lesson["video"] = ""
                }
            }
        },
        handle_course_poster_upload(event) {
            var file = event.target.files[0]
            if (file) {
                this.course_form["poster"] = file.name
                this.course_form[file.name] = file
            }
        },
        add_lesson() {
            this.course_form.lessons.push({name: "", video: ""})

        },
        delete_lesson(lesson) {
            delete this.course_form[lesson["video"]]
            this.course_form.lessons.splice(this.course_form.lessons.indexOf(lesson), 1)
        },
        window_scroll_down_event_listener() {}
    },
    mounted() {
        this.course_form = Object.assign({}, base_course_form_data)
    }
})

courses_app.config.compilerOptions.delimiters = ["${", "}"];
mounted_courses_app = courses_app.mount("#courses")
