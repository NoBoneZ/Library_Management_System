from rest_framework import serializers

from accounts.models import Members, Wallet


class MemberWalletNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ("wallet_number",)
        extra_kwargs = {
            "wallet_number": {"read_only": True}
        }


class MembersSerializer(serializers.ModelSerializer):
    wallet_number = MemberWalletNumberSerializer(read_only=True)

    class Meta:
        model = Members
        fields = ("username", "email", "gender", "wallet_number")


class WalletSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Wallet
        fields = ("owner", "wallet_number", "balance", "outstanding_debts")
        extra_kwargs = {
            
        }

    def get_owner(self, obj):
        return obj.owner.username
