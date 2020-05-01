from django.conf import settings

def global_settings(request):
	return {
	'DEPLOYMENT_ENV' : settings.ENV
	}
