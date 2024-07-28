from rest_framework import serializers
from .models import User, Expense, Split
from decimal import Decimal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'mobile_number']


class SplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Split
        fields = ['user', 'amount', 'percentage']


class ExpenseSerializer(serializers.ModelSerializer):
    splits = SplitSerializer(many=True)

    class Meta:
        model = Expense
        fields = ['id', 'user', 'description',
                  'total_amount', 'date', 'split_type', 'splits']

    def validate_splits(self, splits):
        split_type = self.initial_data.get('split_type', None)
        if split_type == 'percentage':
            total_percentage = sum([split['percentage'] for split in splits])
            if total_percentage != 100:
                raise serializers.ValidationError(
                    "Percentages must add up to 100%")
        return splits

    def create(self, validated_data):
        splits_data = validated_data.pop('splits')
        expense = Expense.objects.create(**validated_data)
        for split_data in splits_data:
            Split.objects.create(expense=expense, **split_data)
        return expense
