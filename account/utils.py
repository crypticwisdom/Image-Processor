def create_account(request):
    success = False

    phone_number = request.data.get('phone_number')
    home_address = request.data.get('home_address')
    country = request.data.get('country')
    state = request.data.get('state')
    city = request.data.get('city')
    profile_picture = request.data.get('profile_picture')







