from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserRegister, AdminTable, BeautyService, Booking, Feedback, Notification, Payment
import uuid  # Add this for generating transaction IDs
from django.utils import timezone


# --------------------
# HOME PAGE
# --------------------
def index(request):
    return render(request, 'index.html')


# --------------------
# REGISTER
# --------------------
def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')  # ADD THIS LINE
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')

        # ADD THIS PASSWORD CHECK (right after getting all fields)
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if UserRegister.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register')

        UserRegister.objects.create(
            name=name,
            email=email,
            password=password,
            phone=phone,
            address=address,
            city=city
        )

        messages.success(request, "Registration Successful!")
        return redirect('login')

    return render(request, 'register.html')

# --------------------
# SINGLE LOGIN (ADMIN + USER)
# --------------------
def login_view(request):

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        admin = AdminTable.objects.filter(email=email, password=password).first()
        if admin:
            request.session['admin_id'] = admin.id
            request.session['role'] = 'admin'

            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'admin_index')

        user = UserRegister.objects.filter(email=email, password=password).first()
        if user:
            request.session['user_id'] = user.id
            request.session['role'] = 'user'

            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'user_index')

    return render(request, 'login.html')

# ====================== ADMIN MANAGE USERS ======================
def admin_manage_users(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    
    filter_type = request.GET.get('filter', 'all')
    
    if filter_type == 'active':
        users = UserRegister.objects.filter(is_blocked=False)
    elif filter_type == 'blocked':
        users = UserRegister.objects.filter(is_blocked=True)
    else:
        users = UserRegister.objects.all()
    
    return render(request, 'admin/admin_manage_users.html', {'users': users, 'filter': filter_type})

def block_user(request, user_id):
    if request.session.get('role') != 'admin':
        return redirect('login')
    
    user = get_object_or_404(UserRegister, id=user_id)
    user.is_blocked = True
    user.save()
    
    messages.success(request, f'User {user.name} has been blocked successfully.')
    return redirect('admin_manage_users')

def unblock_user(request, user_id):
    if request.session.get('role') != 'admin':
        return redirect('login')
    
    user = get_object_or_404(UserRegister, id=user_id)
    user.is_blocked = False
    user.save()
    
    messages.success(request, f'User {user.name} has been unblocked successfully.')
    return redirect('admin_manage_users')

# ADMIN DASHBOARD

def admin_index(request):

    if request.session.get('role') != 'admin':
        return redirect('login')

    return render(request, 'admin/admin_index.html')


# --------------------
# USER DASHBOARD
# --------------------
def user_index(request):

    if request.session.get('role') != 'user':
        return redirect('login')

    user = UserRegister.objects.get(id=request.session['user_id'])

    return render(request, 'user/user_index.html', {'user': user})


# --------------------
# LOGOUT
# --------------------
def logout_view(request):
    request.session.flush()
    return redirect('login')


# --------------------
# ADD SERVICE (ADMIN ONLY)
# --------------------
def add_beauty_service(request):

    if request.session.get('role') != 'admin':
        return redirect('login')

    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration = request.POST.get('duration')
        image = request.FILES.get('image')
        
        BeautyService.objects.create(
            name=name,
            description=description,
            price=price,
            duration=duration,
            image=image
        )

        return redirect('view_beauty_services')

    return render(request, 'admin/add_beauty_services.html')


# --------------------
# VIEW SERVICES (ADMIN)
# --------------------
def view_beauty_services(request):

    if request.session.get('role') != 'admin':
        return redirect('login')

    services = BeautyService.objects.all()
    return render(request, 'admin/view_beauty_service.html', {'services': services})


# --------------------
# UPDATE SERVICE
# --------------------
from django.shortcuts import render, redirect, get_object_or_404
from .models import BeautyService

def update_beauty_service(request, id):

    service = BeautyService.objects.get(id=id)

    if request.method == "POST":

        service.name = request.POST.get('name')

        service.description = request.POST.get('description')

        service.price = request.POST.get('price')

        service.duration = request.POST.get('duration')


        # FIX IMAGE PROBLEM

        if request.FILES.get('image'):

            service.image = request.FILES.get('image')


        service.save()

        return redirect('view_beauty_services')


    return render(request, 'admin/update_beauty_service.html', {'service': service})
#Delete Service
def delete_service(request, id):
    service = get_object_or_404(BeautyService, id=id)
    service.delete()
    return redirect('view_beauty_services')

#View all bookings
def view_all_bookings(request):
    # Only admin can access
    if request.session.get('role') != 'admin':
        return redirect('login')

    # Get all bookings, latest first
    bookings = Booking.objects.all().order_by('-id')

    # Render to the admin template
    return render(request, 'admin/view_all_bookings.html', {'bookings': bookings})

# CONFIRM BOOKING
def confirm_booking(request, id):

    booking = Booking.objects.get(id=id)

    booking.status = "Confirmed"

    booking.save()

    return redirect('view_all_bookings')

# ====================== ADMIN CANCEL BOOKING (EXISTING - FOR ADMIN SIDE) ======================
def admin_cancel_booking(request, id):
    booking = Booking.objects.get(id=id)
    booking.status = "Cancelled"
    booking.save()
    return redirect('view_all_bookings')
# ====================== USER CANCEL BOOKING (FOR USER SIDE) ======================

def user_cancel_booking(request, booking_id):
    # Check if user is logged in
    if request.session.get('role') != 'user':
        return redirect('login')
    
    booking = get_object_or_404(Booking, id=booking_id)
    user_id = request.session.get('user_id')
    
    # Ensure the booking belongs to the logged-in user
    if booking.user.id != user_id:
        messages.error(request, 'You cannot cancel this booking.')
        return redirect('booking_history')
    
    # Only allow cancellation if status is Pending
    if booking.status == 'Pending':
        booking.status = 'Cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'Only pending bookings can be cancelled.')
    
    return redirect('booking_history')



#View available beauty services
def view_services(request):

    services = BeautyService.objects.all()

    return render(request,'user/view_services.html', {'services': services})




from .models import Booking, BeautyService, UserRegister


from django.shortcuts import render, redirect, get_object_or_404
from .models import UserRegister, BeautyService, Booking
from django.contrib import messages

from .models import BeautyService, Booking, UserRegister

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from .models import BeautyService, Booking
# ====================== USER BOOK SERVICE ======================
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def book_service(request, service_id):

    if request.session.get('role') != 'user':
        return redirect('login')

    service = get_object_or_404(BeautyService, id=service_id)

    user_id = request.session.get('user_id')
    user = UserRegister.objects.get(id=user_id)

    total_price = service.price
    advance_amount = total_price * Decimal('0.5')
    balance_amount = total_price - advance_amount

    if request.method == "POST":

        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')

        if booking_date and booking_time:

            booking = Booking.objects.create(
                user=user,
                service=service,
                booking_date=booking_date,
                booking_time=booking_time,   # ✅ IMPORTANT FIX
                status='pending'
            )

            messages.success(request, "Booking created! Please complete 50% payment.")
            return redirect('make_payment', booking_id=booking.id)

        else:
            messages.error(request, "Please select date and time")

    context = {
        'service': service,
        'advance_amount': advance_amount,
        'balance_amount': balance_amount
    }

    return render(request, 'user/book_service.html', context)
from django.shortcuts import render, redirect
from .models import Booking, UserRegister
from django.contrib import messages

def booking_history(request):
    # Check user login
    if request.session.get('role') != 'user':
        return redirect('login')

    user = UserRegister.objects.get(id=request.session['user_id'])
    bookings = Booking.objects.filter(user=user).order_by('-booking_date')

    return render(request, 'user/booking_history.html', {'bookings': bookings})

from django.shortcuts import render, redirect
from .models import Feedback
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Feedback, UserRegister

# ====================== USER FEEDBACK ======================

def send_feedback(request):
    # Check if user is logged in
    if request.session.get('role') != 'user':
        return redirect('login')

    user_id = request.session.get('user_id')
    user = UserRegister.objects.get(id=user_id)

    if request.method == "POST":
        message = request.POST.get('message')
        rating = request.POST.get('rating')  # Get rating from form
        
        if message:
            Feedback.objects.create(
                user=user, 
                message=message,
                rating=rating if rating else None  # Save rating if provided
            )
            messages.success(request, 'Feedback sent successfully!')  # Add success message
            return redirect('view_feedback')
        else:
            messages.error(request, 'Please enter your feedback.')  # Add error message

    return render(request, 'user/send_feedback.html')

def view_feedback(request):
    # Check if user is logged in
    if request.session.get('role') != 'user':
        return redirect('login')

    user_id = request.session.get('user_id')
    user = UserRegister.objects.get(id=user_id)  # Get user object
    feedbacks = Feedback.objects.filter(user=user).order_by('created_at')  # Use user object

    return render(request, 'user/view_feedback.html', {'feedbacks': feedbacks})

# ====================== ADMIN FEEDBACK ======================

def admin_view_feedback(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'admin/admin_view_feedback.html', {'feedbacks': feedbacks})

def admin_reply_feedback(request, feedback_id):
    if request.session.get('role') != 'admin':
        return redirect('login')
    
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    if request.method == 'POST':
        reply = request.POST.get('reply')
        if reply:
            feedback.reply = reply
            feedback.reply_at = timezone.now()  # Add timestamp
            feedback.save()
            messages.success(request, 'Reply sent successfully')
        else:
            messages.error(request, 'Please enter a reply')
        return redirect('admin_view_feedback')
    
    return render(request, 'admin/admin_reply_feedback.html', {'feedback': feedback})


from .models import UserRegister, AdminTable, BeautyService, Booking, Feedback, Notification, Payment
#  ADMIN NOTIFICATIONS 
def admin_send_notification(request):
    # Ensure only admin can access
    if request.session.get('role') != 'admin':
        return redirect('login')
    
    users = UserRegister.objects.all()
    
    if request.method == "POST":
        user_id = request.POST.get('user')
        notification_type = request.POST.get('notification_type')
        custom_message = request.POST.get('custom_message')
        
        if user_id and notification_type:
            user = UserRegister.objects.get(id=user_id)
            
            # Set title and message based on notification type
            if notification_type == 'service':
                title = "📋 New Service Available"
                message = "New services have been added to GLAMORA! Check out our latest offerings."
            elif notification_type == 'offer':
                title = "🎉 Special Offer"
                message = "Special offers available this week! Get discounts on beauty services."
            elif notification_type == 'booking':
                title = "📅 Booking Update"
                message = "Your booking status has been updated. Please log in to view details."
            elif notification_type == 'custom':
                title = "Notification from Admin"
                message = custom_message
            else:
                title = "Notification"
                message = "You have a new notification."
            
            # Create notification
            Notification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                is_read=False
            )
            messages.success(request, 'Notification sent successfully!')
            return redirect('admin_send_notification')
        else:
            messages.error(request, 'Please select a user and notification type.')
    
    return render(request, 'admin/admin_send_notification.html', {'users': users})


# ====================== USER NOTIFICATIONS ======================
def user_view_notifications(request):
    # Check if user is logged in
    if request.session.get('role') != 'user':
        return redirect('login')
    
    user_id = request.session.get('user_id')
    user = UserRegister.objects.get(id=user_id)
    
    # Get filter from request
    filter_type = request.GET.get('filter', 'all')
    
    # Get notifications based on filter
    if filter_type == 'unread':
        notifications = Notification.objects.filter(user=user, is_read=False)
    elif filter_type == 'read':
        notifications = Notification.objects.filter(user=user, is_read=True)
    else:
        notifications = Notification.objects.filter(user=user)
    
    # Order by latest first
    notifications = notifications.order_by('-created_at')
    
    # Get counts
    total_count = Notification.objects.filter(user=user).count()
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    read_count = total_count - unread_count
    
    # DON'T auto-mark as read here - let user mark manually
    # This matches your functional flow "Receives notifications"
    
    context = {
        'notifications': notifications,
        'total_count': total_count,
        'unread_count': unread_count,
        'read_count': read_count,
        'filter': filter_type,
    }
    return render(request, 'user/user_view_notifications.html', context)


def mark_notification_read(request, notification_id):
    """Mark single notification as read"""
    if request.session.get('role') != 'user':
        return redirect('login')
    
    user_id = request.session.get('user_id')
    notification = get_object_or_404(Notification, id=notification_id, user_id=user_id)
    notification.is_read = True
    notification.save()
    messages.success(request, 'Notification marked as read.')
    return redirect('user_view_notifications')


def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    if request.session.get('role') != 'user':
        return redirect('login')
    
    user_id = request.session.get('user_id')
    notifications = Notification.objects.filter(user_id=user_id, is_read=False)
    count = notifications.count()
    
    for notification in notifications:
        notification.is_read = True
        notification.save()
    
    messages.success(request, f'{count} notification(s) marked as read.')
    return redirect('user_view_notifications')
# ====================== USER PAYMENT ======================
import random
from decimal import Decimal
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def make_payment(request, booking_id):

    if request.session.get('role') != 'user':
        return redirect('login')

    booking = get_object_or_404(Booking, id=booking_id)

    # Calculate 50% advance
    total_price = booking.service.price
    advance_amount = total_price * Decimal('0.5')

    if request.method == "POST":

        payment_method = request.POST.get('payment_method')

        if not payment_method:
            messages.error(request, 'Please select a payment method.')
            return redirect('make_payment', booking_id=booking.id)

        transaction_id = 'TXN' + str(random.randint(100000, 999999))

        payment = Payment.objects.create(
            booking=booking,
            payment_method=payment_method,
            amount=total_price,
            paid_amount=advance_amount,
            status='completed',
            transaction_id=transaction_id
        )

        booking.status = 'confirmed'
        booking.save()

        messages.success(request, 'Payment successful! Booking confirmed.')
        return redirect('payment_success', payment_id=payment.id)

    context = {
        'booking': booking,
        'advance_amount': advance_amount
    }

    return render(request, 'user/make_payment.html', context)
def payment_success(request, payment_id):
    """Show payment success page"""
    if request.session.get('role') != 'user':
        return redirect('login')
    
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'user/payment_success.html', {'payment': payment})

# ====================== ADMIN MONITOR PAYMENT DETAILS ======================

def admin_payments(request):
    # Ensure only admin can access
    if request.session.get('role') != 'admin':
        return redirect('login')
    
    # Get all payments with related booking, user, service data
    payments = Payment.objects.select_related('booking__user', 'booking__service').all().order_by('-payment_date')
    
    # Calculate payment statistics
    payments_completed = payments.filter(status='completed').count()
    payments_pending = payments.filter(status='pending').count()
    payments_failed = payments.filter(status='failed').count()
    
    context = {
        'payments': payments,
        'payments_completed': payments_completed,
        'payments_pending': payments_pending,
        'payments_failed': payments_failed,
    }
    
    return render(request, 'admin/admin_payments.html', context)
# ====================== USER MANAGE PROFILE DETAILS ======================

def user_profile(request):
    # Check if user is logged in
    if request.session.get('role') != 'user':
        return redirect('login')
    
    user_id = request.session.get('user_id')
    user = UserRegister.objects.get(id=user_id)
    
    if request.method == "POST":
        # Get updated details from form
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        
        # Update user object
        user.name = name
        user.phone = phone
        user.address = address
        user.city = city
        
        # Update password only if provided
        new_password = request.POST.get('new_password')
        if new_password:
            user.password = new_password
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    
    return render(request, 'user/user_profile.html', {'user': user})





import os
import google.generativeai as genai
from dotenv import load_dotenv
from django.shortcuts import render

# Load .env file
load_dotenv()

# Get API key from env
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


def gemini_chat(request):
    response_text = ""

    if request.method == "POST":
        message = request.POST.get("message")

        response = model.generate_content(message)
        response_text = response.text

    return render(request, "gemini_chat.html", {"response": response_text})