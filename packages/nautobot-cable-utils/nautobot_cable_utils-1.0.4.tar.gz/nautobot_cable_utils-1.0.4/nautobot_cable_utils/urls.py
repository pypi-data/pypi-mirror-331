from __future__ import unicode_literals

from django.urls import path

from . import views

app_name = 'nautobot_cable_utils'
urlpatterns = [
    path(r'reconnect/<uuid:pk>/edit/', views.ReconnectView.as_view(), name='reconnect'),
    path(r'commission/<uuid:pk>/edit/', views.CommissionView.as_view(), name='commission'),
    path(r'undo_commission/<uuid:pk>/edit/', views.UndoCommissionView.as_view(), name='undo_commission'),
    path(r'device_commission/<uuid:pk>/edit/', views.DeviceCommissionView.as_view(), name='device_commission'),
    path(r'cable_inventory_items/', views.CableInventoryItemListView.as_view(), name='cableinventoryitem_list'),
    path(r'cable_inventory_items/<uuid:pk>', views.CableInventoryItemView.as_view(), name='cableinventoryitem'),
    path(r'cable_inventory_items/add/', views.CableInventoryItemCreateView.as_view(), name='cableinventoryitem_add'),
    path(r'cable_inventory_items/bulk-add/', views.CableInventoryItemBulkCreateView.as_view(), name='cableinventoryitem_bulk_add'),
    path(r'cable_inventory_items/import/', views.CableInventoryItemBulkImportView.as_view(), name='cableinventoryitem_import'),
    path(r'cable_inventory_items/edit/', views.CableInventoryItemBulkEditView.as_view(), name='cableinventoryitem_bulk_edit'),
    path(r'cable_inventory_items/delete/', views.CableInventoryItemBulkDeleteView.as_view(), name='cableinventoryitem_bulk_delete'),
    path(r'cable_inventory_items/delete/<uuid:pk>', views.CableInventoryItemDeleteView.as_view(), name='cableinventoryitem_delete'),
    path(r'cable_inventory_items/edit/<uuid:pk>', views.CableInventoryItemEditView.as_view(), name='cableinventoryitem_edit'),
    path(r'measurement_logs/', views.MeasurementLogListView.as_view(), name='measurement_log_list'),
    path(r'measurement_logs/add/', views.MeasurementLogCreateView.as_view(), name='measurement_log_add'),
    path(r'measurement_logs/delete/', views.MeasurementLogBulkDeleteView.as_view(), name='measurement_log_bulk_delete'),
    path(r'measurement_logs/edit/<uuid:pk>', views.MeasurementLogEditView.as_view(), name='measurement_log_edit'),
    path(r'cable_router/link/<str:termination_a_type>/<uuid:termination_a_id>/to/<str:termination_b_type>', views.CableRouterAddView.as_view(), name='cable_router_link'),
    path(r'cable_router/verify/', views.CableRouterVerifyView.as_view(), name='cable_router_verify')
]
