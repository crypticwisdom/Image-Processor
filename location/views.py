from django.shortcuts import render, HttpResponse
# from django_countries import countries
from .models import *
import requests
import threading
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .country_info import *


@api_view(['GET'])
@permission_classes([])
def country_view(request):
    for country in all_countries:
        if not Country.objects.filter(code=country['alpha2Code']).exists():
            Country.objects.create(name=country['name'], code=country['alpha2Code'])

        try:
            for currency in country['currencies']:
                currency_code = currency['code']
                currency_name = currency['name']
                currency_symbol = currency['symbol']

                Country.objects.filter(code=country['alpha2Code'], currency_name__isnull=True).update(
                    currency_name=currency_name,
                    currency_code=currency_code,
                    currency_symbol=currency_symbol,
                    flag_link=country['flag'],
                )
        except Exception as ex:
            print(str(ex))

    thread = threading.Thread(target=create_states, args=[request])
    thread.start()

    data = {
        'countries': Country.objects.all().values('id', 'name', 'code').order_by('id'),
    }
    return Response(data)


def create_states(request):
    for country in Country.objects.all():
        try:
            Country.objects.get(pk=country.pk)
            code = country.code
            url = 'https://countryrestapi.herokuapp.com'
            url = str("{}/{}").format(url, code.lower())
            r = requests.get(url)
            # print(str('{0} - {1}').format(code, r.status_code))
            if str(r.status_code) != '200':
                print(str("Delete {0} from countries").format(code))
                Country.objects.filter(code=code).delete()
            else:
                try:
                    r = r.json()
                    for state in r['states']:
                        if not State.objects.filter(name=state, country=country).exists():
                            new_state = State.objects.create(name=state, country=country)
                            print(str('State created: {0} - {1}').format(state, country))
                except Exception as ex:
                    print(str("Error: {}").format(ex))
                    print(str("Delete {0} from countries").format(code))
                    Country.objects.filter(code=code).delete()
        except Exception as ex:
            print("Error: {}".format(ex))


class GetStatesView(APIView):

    permission_classes = []

    def get(self, request):

        if not request.GET.get("country"):
            return Response("No country selected")

        country = request.GET.get("country")

        if not Country.objects.filter(code__iexact=country).exists():
            data = {
                'detail': "This Country is not available"
            }
            return Response(data)

        if not State.objects.filter(country__code__iexact=country).exists():
            data = {
                'detail': "Selected country does not have a state"
            }
            return Response(data)

        all_states = []
        states = State.objects.filter(country__code__iexact=country).order_by('name')
        for state in states:
            states = {'id': state.id, 'value': state.name, 'name': state.name}
            all_states.append(states)
        data = {
            'states': all_states
        }
        return Response(data)


class GetLocalityView(APIView):

    permission_classes = []

    def get(self, request):

        if not request.GET.get("state"):
            return Response("No state selected")

        state = request.GET.get("state")

        if not State.objects.filter(id__iexact=state).exists():
            data = {
                'detail': "This State is not available"
            }
            return Response(data)

        if not City.objects.filter(state__id__iexact=state).exists():
            data = {
                'locality': [],
                'detail': "Selected state does not have a locality"
            }
            return Response(data)

        all_locality = []
        locality = City.objects.filter(state__id__iexact=state).order_by('name')
        for local in locality:
            locals = {'id': local.id, 'value': local.name, 'name': local.name}
            all_locality.append(locals)
        data = {
            'locality': all_locality
        }
        return Response(data)
