from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Customer, Cake, CakeCustomization, Cart, Order
)
from .serializers import (
    CustomerSerializer, CakeSerializer, CakeCustomizationSerializer, 
    CartSerializer, OrderSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            customer = Customer.objects.get(email=email, password=password)
            return Response({"message": "Login Successful"}, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class CakeViewSet(viewsets.ModelViewSet):
    queryset = Cake.objects.all()
    serializer_class = CakeSerializer

    @action(detail=True, methods=['get'])
    def available(self, request, pk=None):
        """Check if a specific cake is available."""
        cake = self.get_object()
        if cake.available:
            return Response({"message": f"{cake.name} is available"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": f"{cake.name} is not available"}, status=status.HTTP_404_NOT_FOUND)


class CakeCustomizationViewSet(viewsets.ModelViewSet):
    queryset = CakeCustomization.objects.all()
    serializer_class = CakeCustomizationSerializer

    @action(detail=True, methods=['post'])
    def create_customization(self, request, pk=None):
        """Create customization for a cake."""
        cake = Cake.objects.get(pk=pk)
        customization_data = request.data
        customization = CakeCustomization.objects.create(cake=cake, **customization_data)
        return Response(
            CakeCustomizationSerializer(customization).data, 
            status=status.HTTP_201_CREATED
        )


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(detail=True, methods=['post'])
    def add_cake(self, request, pk=None):
        """Add a cake to the cart with or without customization."""
        cart = self.get_object()
        cake_id = request.data.get('cake_id')
        customization_data = request.data.get('customization', None)

        try:
            cake = Cake.objects.get(id=cake_id, available=True)
        except Cake.DoesNotExist:
            return Response({"error": "Cake not available"}, status=status.HTTP_400_BAD_REQUEST)

        if customization_data:
            customization = CakeCustomization.objects.create(
                cake=cake, **customization_data
            )
            cart.customization = customization

        cart.cakes.add(cake)
        cart.save()
        return Response({"message": "Cake added to cart"}, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def place_order(self, request, pk=None):
        """Place an order with items from the cart."""
        cart = Cart.objects.get(id=pk)

        if not cart.cakes.exists():
            return Response({"error": "No cakes in the cart"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            customer=cart.customer,
            total_price=cart.total_amount,
            delivery_address=cart.customer.address
        )
        order.items.set(cart.cakes.all())
        order.save()

        # Clear the cart after order placement
        cart.cakes.clear()
        cart.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def update_payment(self, request, pk=None):
        """Update payment details and send confirmation email."""
        order = self.get_object()
        order.payment_status = request.data.get('payment_status', 'Completed')
        order.payment_method = request.data.get('payment_method', 'Card')
        order.save()

        # Simulate sending an email to the customer
        email_message = f"Payment Successful! Your order has been placed."
        print(f"Sending email to {order.customer.email}: {email_message}")

        return Response({"message": "Payment updated and email sent"}, status=status.HTTP_200_OK)
