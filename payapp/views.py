import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.response import Response

from django.views.generic import ListView, DetailView, TemplateView

from payapp.models import Transaction, TransactionRequest
from payapp.utils import convert_currency, convert_to_float
from register.models import User
from rest_framework.views import APIView
from rest_framework.status import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST
)
from register.models import User


class HomeTemplateView(TemplateView):
    template_name = 'payapp/home.html'


@method_decorator(login_required, name='dispatch')
class DashboardTemplateView(TemplateView):
    template_name = 'payapp/dashboard.html'

    def get_context_data(self, **kwargs):

        context = super(DashboardTemplateView, self).get_context_data(**kwargs)
        context['amount'] =round(self.request.user.total_amount, 1)
        context['currency'] = self.request.user.currency_type
        context['t_sent'] = Transaction.objects.filter(sender=self.request.user).count()
        context['t_received'] = Transaction.objects.filter(receiver=self.request.user).count()
        context['r_sent'] = TransactionRequest.objects.filter(sender=self.request.user).count()
        context['r_received'] = TransactionRequest.objects.filter(receiver=self.request.user).count()
        return context


""" TRANSACTION VIEWS"""


@method_decorator(login_required, name='dispatch')
class TransactionListView(ListView):
    template_name = 'payapp/transactions.html'
    context_object_name = 'objects'

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )


@method_decorator(login_required, name='dispatch')
class TransactionDetailView(DetailView):

    def get_object(self, queryset=None):
        return get_object_or_404(
            Transaction.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user)),
            pk=self.kwargs['pk']
        )


@method_decorator(login_required, name='dispatch')
class TransactionCreateView(View):
    template_name = 'payapp/transaction_create.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        amount = request.POST.get('amount')

        # IF: missing parameters
        if not email or not amount:
            messages.warning(request, "Email or Amount is missing")
            return redirect('payapp:transaction-create')

        receiver = User.objects.filter(email=email)

        # IF: no receiver
        if not receiver:
            messages.error(request, "User doesn't exists with this email address")
            return redirect('payapp:transaction-create')

        sender = request.user
        receiver = receiver[0]

        # IF: same user
        if receiver == sender:
            messages.warning(request, "You can't sent amounts to yourself")
            return redirect('payapp:transaction-create')

        # IF: amount issue
        if sender.total_amount <= float(amount):
            messages.warning(request, "In sufficient balance to perform this transaction")
            return redirect('payapp:transaction-create')

        # ADD: transaction
        Transaction.objects.create(sender=sender, receiver=receiver, amount=amount)
        receiver.total_amount += float(amount)
        receiver.save()
        sender.total_amount -= float(amount)
        sender.save()
        messages.success(request, "Amount Transferred successfully.")
        return redirect('payapp:transactions')


""" TRANSACTION REQUEST VIEWS"""


@method_decorator(login_required, name='dispatch')
class TransactionRequestListView(ListView):
    template_name = 'payapp/request_transaction_list.html'

    def get_queryset(self):
        return TransactionRequest.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )


@method_decorator(login_required, name='dispatch')
class TransactionRequestDetailView(DetailView):

    def get_object(self, queryset=None):
        return get_object_or_404(
            TransactionRequest.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user)),
            pk=self.kwargs['pk']
        )


@method_decorator(login_required, name='dispatch')
class TransactionRequestCreateView(View):
    template_name = 'payapp/request_transaction_create.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        amount = request.POST.get('amount')

        # IF: no status parameter
        if not email or not amount:
            messages.warning(request, "Email or Amount is missing")
            return redirect('payapp:request-create')

        # IF: receiver not available
        request_from = User.objects.filter(email=email)
        if not request_from:
            messages.error(request, "User doesn't exists with this email address")
            return redirect('payapp:request-create')

        request_to = request.user
        request_from = request_from[0]

        # IF: same user
        if request_from == request_to:
            messages.warning(request, "You can't request amounts from yourself")
            return redirect('payapp:request-create')

        # SUCCESS: create transaction
        TransactionRequest.objects.create(sender=request_to, receiver=request_from, amount=amount)
        messages.success(request, "Your transactions request added successfully")
        return redirect('payapp:requests')


@method_decorator(login_required, name='dispatch')
class TransactionRequestUpdateView(View):

    def get(self, request, pk):

        # IF: no status parameter
        status = request.GET.get('status')

        # IF: get transaction or 404
        transaction_request = get_object_or_404(
            TransactionRequest.objects.filter(receiver=request.user, status='pending'), pk=pk
        )
        sender = transaction_request.receiver
        receiver = transaction_request.sender
        amount = transaction_request.amount

        # IF: wrong parameter
        if status not in ['approved', 'cancel']:
            messages.warning(request, "Some parameters are missing")
            return redirect('payapp:requests')

        if status == "cancel":
            transaction_request.status = "cancelled"
            transaction_request.checked_on = datetime.datetime.now()
            transaction_request.save()
            return redirect('payapp:requests')

        # IF: sender amount is less
        if amount > sender.total_amount:
            messages.warning(request, "In sufficient balance to perform this transaction")
            return redirect('payapp:requests', )

        # ADD: transaction
        Transaction.objects.create(
            sender=sender, receiver=receiver, amount=amount
        )

        # ADD: transaction
        Transaction.objects.create(
            sender=sender, receiver=receiver, amount=amount
        )

        # UPDATE: sender and receiver amounts
        sender.total_amount -= amount
        sender.save()
        receiver.total_amount += amount
        receiver.save()

        transaction_request.status = 'accepted'
        messages.success(request, "Request approved and transaction performed successfully")

        # UPDATE: request
        transaction_request.checked_on = datetime.datetime.now()
        transaction_request.save()

        # SUCCESS: message and redirect

        return redirect('payapp:requests')


""" API """


@method_decorator(login_required, name='dispatch')
class CurrencyConversionAPI(APIView):
    def get(self, request, currency1, currency2, amount):

        # IF: currencies not supported
        if currency1 not in ['USD', 'EURO', 'GBP'] or currency2 not in ['USD', 'EURO', 'GBP']:
            return Response(
                status=HTTP_400_BAD_REQUEST, data={
                    'error': 'Only USD, EURO and GBP are supported'
                }
            )

        float_amount = convert_to_float(amount)

        # IF: not supported to convert into int or float
        if not float_amount:
            return Response(
                status=HTTP_400_BAD_REQUEST, data={
                    'error': 'Amount must be number (integer, float)'
                }
            )

        # IF: amount is less or equal to 0
        if float_amount <= 0:
            return Response(
                status=HTTP_200_OK, data={
                    'error': 'Amount must be numeric and greater than 0'
                }
            )

        # SUCCESS: everything is fine here
        converted_amount = convert_currency(currency1, currency2, float_amount)
        return Response(
            status=HTTP_200_OK, data={
                'amount': converted_amount
            }
        )
