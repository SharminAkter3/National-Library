from django.shortcuts import render


def about(request):
    return render(request, "accounts/aboutUs.html")


def contact(request):
    return render(request, "accounts/contactUs.html")
