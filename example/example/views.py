from django.shortcuts import render


def home(request):
    """Simple homepage view."""
    context = {}
    if request.user.is_authenticated():
        try:
            access = request.user.accountaccess_set.all()[0]
        except IndexError:
            access = None
        else:
            client = access.api_client
            context['info'] = client.get_profile_info(raw_token=access.access_token)
    return render(request, 'home.html', context)
