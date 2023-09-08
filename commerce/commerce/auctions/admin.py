from django.contrib import admin
from .models import Listing
from .models import User
from .models import Comment
from .models import Watchlist
# Register your models here.
admin.site.register(Listing)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Watchlist)

