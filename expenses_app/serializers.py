from rest_framework import serializers
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from .models import User, Expense, ExpenseSplit


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'mobile_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.create_user(**validated_data)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    def validate_mobile_number(self, value):
        if User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError(
                "A user with this mobile number already exists.")
        return value


class ExpenseSplitSerializer(serializers.ModelSerializer):
    percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True)
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True)

    class Meta:
        model = ExpenseSplit
        fields = ['user', 'amount', 'percentage']


class ExpenseSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitSerializer(many=True)

    class Meta:
        model = Expense
        fields = ['id', 'payer', 'total_amount',
                  'split_method', 'description', 'date', 'splits']

    def validate(self, data):
        splits_data = data.get('splits', [])
        total_amount = Decimal(data.get('total_amount', 0))
        split_method = data.get('split_method')

        print(f"Debug: split_method={split_method}")  # Debugging print
        print(f"Debug: splits_data={splits_data}")  # Debugging print

        if split_method == 'equal':
            if not splits_data:
                raise serializers.ValidationError(
                    "Splits data is required for equal split.")
            if len(splits_data) < 1:
                raise serializers.ValidationError(
                    "At least one split is required for equal split.")
            equal_amount = total_amount / len(splits_data)
            for split in splits_data:
                amount = Decimal(split.get('amount', 0))
                if amount and amount != equal_amount:
                    raise serializers.ValidationError(
                        "Each participant must have an equal amount in an equal split.")
                if split.get('percentage') is not None:
                    raise serializers.ValidationError(
                        "Percentage should be null for equal split method.")

        elif split_method == 'exact':
            total_split_amount = sum(Decimal(split.get('amount', 0))
                                     for split in splits_data)
            if total_split_amount != total_amount:
                raise serializers.ValidationError(
                    "The sum of exact amounts must equal the total amount.")
            for split in splits_data:
                if split.get('percentage') is not None:
                    raise serializers.ValidationError(
                        "Percentage should be null for exact split method.")

        elif split_method == 'percentage':
            total_percentage = Decimal('0.00')
            for split in splits_data:
                percentage = Decimal(split.get('percentage', '0.00'))
                print(f"Debug: percentage={percentage}")  # Debugging print
                if percentage < 0 or percentage > 100:
                    raise serializers.ValidationError(
                        "Percentage must be between 0 and 100.")
                total_percentage += percentage

            # Debugging print
            print(f"Debug: total_percentage={total_percentage}")

            if not (Decimal('99.99') <= total_percentage <= Decimal('100.01')):
                raise serializers.ValidationError(
                    "The sum of percentages must equal 100%.")
            for split in splits_data:
                if split.get('amount') is not None:
                    raise serializers.ValidationError(
                        "Amount should be null for percentage split method.")

        return data

    def create(self, validated_data):
        splits_data = validated_data.pop('splits')
        with transaction.atomic():
            expense = Expense.objects.create(**validated_data)

            if expense.split_method == 'percentage':
                # Calculate amounts from percentages
                for split_data in splits_data:
                    percentage = Decimal(split_data.get('percentage', '0.00'))
                    amount = (percentage / 100) * Decimal(expense.total_amount)
                    split_data['amount'] = amount
                    split_data['percentage'] = percentage

            elif expense.split_method == 'equal':
                # Calculate amounts for equal split
                amount = Decimal(expense.total_amount) / len(splits_data)
                for split_data in splits_data:
                    split_data['amount'] = amount
                    split_data['percentage'] = (
                        amount / Decimal(expense.total_amount)) * 100

            elif expense.split_method == 'exact':
                # Calculate percentages from amounts
                total_amount = Decimal(expense.total_amount)
                for split_data in splits_data:
                    amount = Decimal(split_data.get('amount', '0.00'))
                    percentage = (amount / total_amount) * 100
                    split_data['percentage'] = percentage

            for split_data in splits_data:
                ExpenseSplit.objects.create(expense=expense, **split_data)

        return expense
