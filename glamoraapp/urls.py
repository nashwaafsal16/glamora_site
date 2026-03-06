from django.urls import path
from . import views

urlpatterns = [

    # ---------------- HOME ----------------
    path('', views.index, name='index'),

    # ---------------- AUTH ----------------
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('admin/users/', views.admin_manage_users, name='admin_manage_users'),
    path('admin/block-user/<int:user_id>/', views.block_user, name='block_user'),
    path('admin/unblock-user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('logout/', views.logout_view, name='logout'),

    # ---------------- DASHBOARD ----------------
    path('admin-dashboard/', views.admin_index, name='admin_index'),
    path('user-index/', views.user_index, name='user_index'),

    # ---------------- ADMIN SERVICE MANAGEMENT ----------------
    path('add_beauty_service/', views.add_beauty_service, name='add_beauty_service'),
    path('view-beauty-services/', views.view_beauty_services, name='view_beauty_services'),
    path('update-beauty-service/<int:id>/', views.update_beauty_service, name='update_beauty_service'),
    path('delete-service/<int:id>/', views.delete_service, name='delete_service'),
    
    path('view-all-bookings/', views.view_all_bookings, name='view_all_bookings'),

    path('confirm-booking/<int:id>/', views.confirm_booking, name='confirm_booking'),
    path('admin/cancel-booking/<int:id>/', views.admin_cancel_booking, name='admin_cancel_booking'),
  
    #---------------USER SERVICE MANAGEMENT------------------
    path('user-index/', views.user_index, name='user_index'),

    path('view-services/',views.view_services,name='view_services'),
    

    path('book_service/<int:service_id>/', views.book_service, name='book_service'),
    path('booking-history/', views.booking_history, name='booking_history'),
    
    path('user/cancel-booking/<int:booking_id>/', views.user_cancel_booking, name='user_cancel_booking'),

        # ====================== USER FEEDBACK ======================
    path('send-feedback/', views.send_feedback, name='send_feedback'),
    path('my-feedback/', views.view_feedback, name='view_feedback'),

    path('admin/feedback/', views.admin_view_feedback, name='admin_view_feedback'),
    path('admin/feedback/reply/<int:feedback_id>/', views.admin_reply_feedback, name='admin_reply_feedback'),
        # ====================== ADMIN NOTIFICATIONS ======================
    path('admin/send-notification/', views.admin_send_notification, name='admin_send_notification'),
    path('admin/', views.admin_index, name='admin_index'),
    # ====================== USER NOTIFICATIONS ======================
    path('user/notifications/', views.user_view_notifications, name='user_view_notifications'),
    path('user/notifications/mark/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('user/notifications/mark-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

     # ====================== USER PAYMENT ======================
   path('payment/<int:booking_id>/', views.make_payment, name='make_payment'),
   path('payment-success/<int:payment_id>/', views.payment_success, name='payment_success'),

    path('user/profile/', views.user_profile, name='user_profile'),
    
    path('admin_payments/',views.admin_payments,name='admin_payments')
   

]





