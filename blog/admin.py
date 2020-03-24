from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin.models import LogEntry
from .adminforms import PostAdminForm
from .models import Category, Tag, Post
from typeidea.custom_site import custom_site

from typeidea.base_admin import BaseOwnerAdmin


class PostInline(admin.TabularInline):
    """分类页面直接编辑文章功能"""
    fields = ('title', 'desc', 'content',)
    extra = 1
    model = Post


class CategoryOwnerFilter(admin.SimpleListFilter):
    """自定义过滤器只展示当前用户分类"""
    title = "分类过滤器"
    parameter_name = 'owner_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset


# Register your models here.
@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    inlines = [PostInline]

    list_display = ('name', 'status', 'is_nav', 'created_time', 'post_count', 'owner')
    fields = ('name', 'status', 'is_nav')

    # list_filter = [CategoryOwnerFilter]

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = "文章数量"

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(CategoryAdmin, self).save_model(request, obj, form, change)

    # 控制权限
    def get_queryset(self, request):
        qs = super(CategoryAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time', 'owner')
    fields = ('name', 'status')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(TagAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)


@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm

    list_display = ['title', 'category', 'status', 'created_time', 'owner', 'operator']

    list_display_links = []
    # list_filter = ['category']
    list_filter = [CategoryOwnerFilter]
    search_fields = ['title', 'category__name']

    actions_on_bottom = True
    actions_on_top = True
    # 编辑页面
    save_on_top = True

    # fields = (
    #     ('category', 'title'),
    #     'desc',
    #     'status',
    #     'content',
    #     'tag',
    # )
    # fields  表示展示字段和顺序 fieldsets表示布局,classes表示样式
    fieldsets = (
        ('基础配置', {
            'description': '基础配置描述',
            'fields': (('category', 'title'),
                       'status',
                       )
        }),
        ('内容', {
            'fields': ('desc', 'content')
        }),
        ('额外信息', {
            'classes': ('collapse',),
            'fields': ('tag',)
        })
    )

    def operator(self, obj):
        return format_html(
            '<a href = "{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=(obj.id,))
        )

    operator.short_description = "操作"

    class Media:
        """设置资源"""

        # css = {
        #     'all': ("https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/css/bootstrap.min.css",)
        # }
        # js = ("https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/js/bootstrap.min.js",)


@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['object_repr', 'object_id', 'action_flag', 'user', 'change_message']
