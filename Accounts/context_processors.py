def user_role(request):
    user_role = None
    if request.user.is_authenticated and request.user.is_prison_account and hasattr(request.user, 'role'):
        user_role = request.user.role.role
    return {'user_role': user_role}

def user_account_type(request):
    account_type = None
    if request.user.is_authenticated:
        if request.user.is_court_account:
            account_type = 'court'
        elif request.user.is_prison_account:
            account_type = 'prison'
    return {'account_type': account_type}
