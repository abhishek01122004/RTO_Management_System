from django.shortcuts import render

def license_service(request):
    """View for license service information page"""
    return render(request, 'services/license_service.html')

def vehicle_service(request):
    """View for vehicle service information page"""
    return render(request, 'services/vehicle_service.html')

def challan_service(request):
    """View for challan service information page"""
    return render(request, 'services/challan_service.html') 