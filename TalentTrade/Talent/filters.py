import django_filters
from .models import TalentsPost, Categories


class TalentFilter(django_filters.FilterSet):

    # #Creates a dropdown filter for a ForeignKey field
# Automatically creates <select> dropdown in HTML
# Because category is a ForeignKey to Categories model
# It's a "choice" from existing Categories
    category = django_filters.ModelChoiceFilter(
        queryset=Categories.objects.all(),
        label='Category',
        empty_label='All Categories'
    )
    # Like configuration settings for the filter
    class Meta:
        model = TalentsPost
        fields = ['category']