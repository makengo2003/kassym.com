from expense.models import Expense


def get_expenses(user, change_time):
    expenses = Expense.objects.filter(user=user, change_time=change_time).only("sum", "description", "currency").order_by("-id")

    response = {
        "expenses": [],
        "total_expenses_sum_in_ruble": 0,
        "total_expenses_sum_in_tenge": 0,
    }

    for expense in expenses:
        response["expenses"].append({"sum": expense.sum, "description": expense.description, "currency": expense.get_currency_display()})

        if expense.currency == "ruble":
            response["total_expenses_sum_in_ruble"] += expense.sum
        elif expense.currency == "tenge":
            response["total_expenses_sum_in_tenge"] += expense.sum

    return response


def save(user, data):
    if hasattr(user, "buyer"):
        employee_type = "buyer"
    else:
        employee_type = "manager"

    Expense.objects.create(**data, user=user, employee_type=employee_type)
