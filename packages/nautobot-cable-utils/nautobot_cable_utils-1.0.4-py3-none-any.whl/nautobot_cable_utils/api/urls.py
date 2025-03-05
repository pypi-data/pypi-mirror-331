from nautobot.apps.api import OrderedDefaultRouter
from .views import CablePlugViewSet, CableInventoryItemViewSet

router = OrderedDefaultRouter()
router.register("cable-plug", CablePlugViewSet)
router.register("cable-inventory-item", CableInventoryItemViewSet)

app_name = "nautobot_cable_utils-api"
urlpatterns = router.urls
