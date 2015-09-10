# -*- coding: utf-8 -*-
from django.contrib.sites.shortcuts import get_current_site
from allaccess.models import Provider


def provider_available(request, provider_name):
    """
    return true if a provider is available for the given site
    """
    site = get_current_site(request)
    available = Provider.objects.filter(
        name=provider_name, site=site).exists()
    return available
