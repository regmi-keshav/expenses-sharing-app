from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Expense
from .serializers import UserSerializer, ExpenseSerializer
from .permissions import IsOwnerOrReadOnly
import csv
from django.http import HttpResponse


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='balance-sheet')
    def balance_sheet(self, request):
        expenses = Expense.objects.filter(splits__user=request.user)
        balance_sheet_data = self.calculate_balance(expenses)
        return Response(balance_sheet_data)

    @action(detail=False, methods=['get'], url_path='download-balance-sheet')
    def download_balance_sheet(self, request):
        expenses = Expense.objects.filter(splits__user=request.user)
        response = self.generate_csv(expenses)
        return response

    def calculate_balance(self, expenses):
        total_owed = 0
        total_paid = 0
        for expense in expenses:
            for split in expense.splits.all():
                if split.user == self.request.user:
                    total_owed += split.amount
                if expense.user == self.request.user:
                    total_paid += split.amount
        balance = total_paid - total_owed
        return {
            'total_owed': total_owed,
            'total_paid': total_paid,
            'balance': balance,
            'expenses': self.get_serializer(expenses, many=True).data
        }

    def generate_csv(self, expenses):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="balance_sheet.csv"'

        writer = csv.writer(response)
        writer.writerow(['Description', 'Total Amount', 'Date',
                        'Split Type', 'User', 'Amount', 'Percentage'])

        for expense in expenses:
            for split in expense.splits.all():
                writer.writerow([
                    expense.description,
                    expense.total_amount,
                    expense.date,
                    expense.split_type,
                    split.user.name,
                    split.amount,
                    split.percentage
                ])
        return response
