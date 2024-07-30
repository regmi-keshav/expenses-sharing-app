import csv
from django.http import HttpResponse
from rest_framework import viewsets, serializers, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import User, Expense
from .serializers import UserSerializer, ExpenseSerializer
from .permissions import IsOwnerOrReadOnly
from django.db import transaction


class CustomTokenObtainPairView(TokenObtainPairView):
    # Customizing token obtain view if needed
    pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "User has been deleted."}, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def user_expenses(self, request):
        expenses = Expense.objects.filter(payer=request.user)
        serializer = self.get_serializer(expenses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def overall_expenses(self, request):
        expenses = Expense.objects.all()
        serializer = self.get_serializer(expenses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def balance_sheet(self, request):
        user_expenses = Expense.objects.filter(payer=request.user)
        balance_data = {
            "user_expenses": ExpenseSerializer(user_expenses, many=True).data,
            "total_expenses": sum(expense.total_amount for expense in user_expenses)
        }
        return Response(balance_data)

    @action(detail=False, methods=['get'], url_path='download-balance-sheet', permission_classes=[permissions.IsAuthenticated])
    def download_balance_sheet(self, request):
        user_expenses = Expense.objects.filter(payer=request.user)
        # Make sure to create this template in your templates directory
        template_path = 'balance_sheet.html'

        context = {
            'user_expenses': user_expenses,
            'total_expenses': sum(expense.total_amount for expense in user_expenses)
        }

        html_content = render_to_string(template_path, context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="balance_sheet.pdf"'

        pisa_status = pisa.CreatePDF(html_content, dest=response)

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html_content + '</pre>')

        return response

    # @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    # def balance_sheet(self, request):
    #     user_expenses = Expense.objects.filter(payer=request.user)
    #     balance_data = {
    #         "user_expenses": ExpenseSerializer(user_expenses, many=True).data,
    #         "total_expenses": sum(expense.total_amount for expense in user_expenses),
    #         "splits": [
    #             {
    #                 "expense": expense.id,
    #                 "description": expense.description,
    #                 "splits": ExpenseSplitSerializer(expense.splits.all(), many=True).data
    #             }
    #             for expense in user_expenses
    #         ]
    #     }
    #     return Response(balance_data)

# @action(detail=False, methods=['get'], url_path='download-csv', permission_classes=[permissions.IsAuthenticated])
# def download_csv(self, request):
#     user_expenses = Expense.objects.filter(payer=request.user)

#     # Create the HttpResponse object with the appropriate CSV header.
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="user_expenses.csv"'

#     writer = csv.writer(response)
#     # Write the header row
#     writer.writerow(['ID', 'Description', 'Total Amount', 'Date'])

#     # Write data rows
#     for expense in user_expenses:
#         writer.writerow([expense.id, expense.description,
#                         expense.total_amount, expense.date])

#     return response


@action(detail=False, methods=['get'], url_path='download-csv', permission_classes=[permissions.IsAuthenticated])
def download_csv(self, request):
    user_expenses = Expense.objects.filter(payer=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Description', 'Total Amount', 'Date'])

    for expense in user_expenses:
        writer.writerow([expense.id, expense.description,
                        expense.total_amount, expense.date])

    return response
